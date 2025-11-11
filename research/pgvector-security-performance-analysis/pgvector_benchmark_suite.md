# pgvector Security & Performance Benchmark Suite

## Overview
Benchmarks to validate security findings and performance issues identified in pgvector analysis.

---

## 1. INTEGER OVERFLOW BENCHMARKS

### Benchmark 1.1: K-means Center Multiplication Overflow
**Purpose**: Validate if `numCenters * numCenters` can overflow before validation check

**Test Cases**:
```sql
-- Test 1: Maximum safe value (current limit)
CREATE TABLE vectors_test (id SERIAL, vec vector(128));
INSERT INTO vectors_test SELECT i, array_fill(random(), ARRAY[128])::vector(128)
FROM generate_series(1, 100000) i;

-- Attempt with max lists (should succeed)
CREATE INDEX idx_max_lists ON vectors_test USING ivfflat (vec) WITH (lists = 32768);

-- Test 2: Measure memory allocation during build
SELECT pg_size_pretty(pg_relation_size('idx_max_lists'));
```

**Expected Results**:
- lists=32768: 32768 * 32768 = 1,073,741,824 < INT_MAX (2,147,483,647) ✓
- Should succeed without overflow
- Monitor memory usage: expect ~13GB peak (from analysis)

**Validation Method**:
- Enable PostgreSQL logging: `SET log_min_messages = DEBUG1;`
- Monitor with: `SELECT * FROM pg_stat_activity WHERE state = 'active';`
- Check for OOM or unexpected errors

---

### Benchmark 1.2: Sparse Vector Size Calculation
**Purpose**: Test `nnz * sizeof(type)` overflow

```sql
-- Test maximum nnz
CREATE TABLE sparse_test (id SERIAL, svec sparsevec(50000));

-- Test 1: Max safe nnz (16000)
INSERT INTO sparse_test VALUES (1,
  (SELECT string_agg(i || ':' || random()::text, ',')
   FROM generate_series(1, 16000) i)::sparsevec);

-- Test 2: Attempt beyond limit (should error)
INSERT INTO sparse_test VALUES (2,
  (SELECT string_agg(i || ':' || random()::text, ',')
   FROM generate_series(1, 16001) i)::sparsevec);
```

**Expected Results**:
- 16000 elements: SPARSEVEC_SIZE = offsetof + (16000 * 4) + (16000 * 4) = ~128KB ✓
- 16001 elements: Should error with "sparsevec cannot have more than 16000 non-zero elements"

---

## 2. RESOURCE EXHAUSTION BENCHMARKS

### Benchmark 2.1: IVFFlat maxProbes Memory Allocation
**Purpose**: Validate if maxProbes can cause excessive memory allocation

**Test Setup**:
```sql
-- Create index with many lists
CREATE TABLE probe_test (id SERIAL, vec vector(1536));
INSERT INTO probe_test SELECT i, array_fill(random(), ARRAY[1536])::vector(1536)
FROM generate_series(1, 100000) i;

CREATE INDEX idx_probes ON probe_test USING ivfflat (vec) WITH (lists = 10000);
```

**Test Cases**:
```sql
-- Test 1: Default probes (safe)
SET ivfflat.probes = 10;
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM probe_test ORDER BY vec <-> array_fill(0.5, ARRAY[1536])::vector(1536) LIMIT 10;

-- Test 2: High probes
SET ivfflat.probes = 1000;
-- Monitor memory growth

-- Test 3: Extreme probes (with iterative scan)
SET ivfflat_iterative_scan = on;
SET ivfflat_max_probes = 100000;  -- Attempt massive value
-- Measure memory allocation
```

**Measurements**:
- Memory per probe: `BlockNumber` (4 bytes) + `IvfflatScanList` struct
- Expected allocation: `maxProbes * (4 + sizeof(IvfflatScanList))`
- Monitor with: `SELECT * FROM pg_backend_memory_contexts WHERE name = 'ExecutorState';`

**Validation**:
- Check if allocation is bounded by `lists` parameter (should cap at 10,000 in this test)
- Verify no integer overflow in multiplication

---

### Benchmark 2.2: K-means Sample Allocation
**Purpose**: Measure actual memory used during IVF index build with large samples

```sql
-- Create memory-intensive scenario
CREATE TABLE kmeans_test (id SERIAL, vec vector(2000));
INSERT INTO kmeans_test SELECT i, array_fill(random(), ARRAY[2000])::vector(2000)
FROM generate_series(1, 1000000) i;

-- Monitor memory before build
SELECT pg_size_pretty(sum(pg_backend_memory_contexts.total_bytes))
FROM pg_backend_memory_contexts;

-- Build with maximum lists
SET maintenance_work_mem = '16GB';  -- Set high limit
CREATE INDEX idx_kmeans ON kmeans_test USING ivfflat (vec) WITH (lists = 32768);

-- Monitor peak memory usage
```

**Expected Calculation**:
- numSamples = 32768 * 50 = 1,638,400
- Memory per sample = 2000 dimensions * 4 bytes = 8KB
- Total samples memory = 1,638,400 * 8KB = ~13GB
- Plus centers: 32768 * 8KB = ~256MB
- **Total expected: ~13.3GB**

**Validation**: Does actual usage match prediction?

---

### Benchmark 2.3: HNSW Recursion Depth
**Purpose**: Test layer traversal depth and memory usage

```sql
CREATE TABLE hnsw_test (id SERIAL, vec vector(768));
INSERT INTO hnsw_test SELECT i, array_fill(random(), ARRAY[768])::vector(768)
FROM generate_series(1, 100000) i;

-- Build HNSW index
CREATE INDEX idx_hnsw ON hnsw_test USING hnsw (vec) WITH (m = 16);

-- Check actual max level in index
-- (Would need to query internal structures)

-- Test search with varying ef_search
SET hnsw.ef_search = 10;
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM hnsw_test ORDER BY vec <-> array_fill(0.5, ARRAY[768])::vector(768) LIMIT 10;

SET hnsw.ef_search = 1000;
-- Measure memory difference
```

**Measurements**:
- Query `entryPoint->level` distribution across elements
- Memory per level = `ef_search * M * pointer_size`
- Validate max level formula: `ceil(log(n) / log(m))` where n=100000, m=16
- Expected max level ≈ 4-5

---

## 3. CONCURRENCY BENCHMARKS

### Benchmark 3.1: PRNG State Corruption
**Purpose**: Test if parallel builds corrupt random number generation

```bash
# Create test script: parallel_build_test.sh
for i in {1..4}; do
  psql -c "
    CREATE TABLE hnsw_parallel_$i (id SERIAL, vec vector(128));
    INSERT INTO hnsw_parallel_$i
    SELECT i, array_fill(random(), ARRAY[128])::vector(128)
    FROM generate_series(1, 50000) i;
    CREATE INDEX idx_hnsw_$i ON hnsw_parallel_$i USING hnsw (vec) WITH (m = 16);
  " &
done
wait
```

**Validation**:
- Check if indexes have consistent structure
- Query random samples from each index
- Verify level distribution is consistent
- Test if search quality is similar across all indexes

**Expected Issue**:
- If PRNG is corrupted, level assignments may be skewed
- Graph connectivity could be suboptimal

---

### Benchmark 3.2: Flushed Flag Race Condition
**Purpose**: Test concurrent inserts during flush

```sql
-- Session 1: Start large insert (triggers flush)
BEGIN;
INSERT INTO hnsw_test SELECT i, array_fill(random(), ARRAY[768])::vector(768)
FROM generate_series(1000000, 1100000) i;
-- Don't commit yet

-- Session 2: Immediately start another insert
BEGIN;
INSERT INTO hnsw_test SELECT i, array_fill(random(), ARRAY[768])::vector(768)
FROM generate_series(1100001, 1100100) i;
COMMIT;

-- Session 1: Now commit
COMMIT;

-- Validation: Check for duplicates or missing rows
SELECT COUNT(*) FROM hnsw_test;  -- Should be exact count
SELECT id, COUNT(*) FROM hnsw_test GROUP BY id HAVING COUNT(*) > 1;  -- Should be empty
```

---

## 4. PERFORMANCE BENCHMARKS

### Benchmark 4.1: K-means Distance Calculation Redundancy
**Purpose**: Measure time spent in k-means during IVF build

**Setup**:
```sql
-- Enable timing
\timing on
SET client_min_messages = 'debug1';

CREATE TABLE perf_test (id SERIAL, vec vector(128));
INSERT INTO perf_test SELECT i, array_fill(random(), ARRAY[128])::vector(128)
FROM generate_series(1, 500000) i;
```

**Test Cases**:
```sql
-- Test 1: Small lists (less k-means overhead)
\timing
CREATE INDEX idx_perf_small ON perf_test USING ivfflat (vec) WITH (lists = 100);
-- Record time

DROP INDEX idx_perf_small;

-- Test 2: Large lists (more k-means overhead)
\timing
CREATE INDEX idx_perf_large ON perf_test USING ivfflat (vec) WITH (lists = 10000);
-- Record time
```

**Expected Results**:
- Time should grow super-linearly with lists parameter
- K-means iterations dominate build time
- Validate with: `EXPLAIN (ANALYZE, TIMING ON) CREATE INDEX ...`

**Optimization Validation**:
If developers fix the O(n*k) issue to O(n*log(k)):
- Expected speedup: 20-50% for large lists
- Measure with: `pgbench -c 1 -t 1 -f create_index.sql`

---

### Benchmark 4.2: Sparse Vector Parsing Performance
**Purpose**: Measure double-pass overhead

```sql
-- Generate large sparse vectors
CREATE TABLE sparse_perf (id SERIAL, svec sparsevec(50000));

-- Test 1: Small nnz (less overhead)
\timing
INSERT INTO sparse_perf
SELECT i, (SELECT string_agg(j || ':' || random()::text, ',')
           FROM generate_series(1, 100) j)::sparsevec
FROM generate_series(1, 10000) i;
-- Record time

-- Test 2: Large nnz (more double-pass overhead)
TRUNCATE sparse_perf;
\timing
INSERT INTO sparse_perf
SELECT i, (SELECT string_agg(j || ':' || random()::text, ',')
           FROM generate_series(1, 10000) j)::sparsevec
FROM generate_series(1, 1000) i;
-- Record time
```

**Metrics**:
- Time per element should be linear with nnz
- Single-pass optimization should reduce time by ~30-40%

---

### Benchmark 4.3: HNSW Lock Contention
**Purpose**: Measure parallel build scalability

```bash
# Test with varying worker counts
for workers in 1 2 4 8; do
  psql -c "
    SET max_parallel_maintenance_workers = $workers;
    CREATE TABLE hnsw_workers_$workers (id SERIAL, vec vector(384));
    INSERT INTO hnsw_workers_$workers
    SELECT i, array_fill(random(), ARRAY[384])::vector(384)
    FROM generate_series(1, 100000) i;

    \timing
    CREATE INDEX idx_hnsw_w$workers ON hnsw_workers_$workers USING hnsw (vec) WITH (m = 16);
  "
done
```

**Expected Behavior**:
- If lock contention exists: Speedup plateaus after 2-4 workers
- Ideal scaling: 2x workers = ~1.8x speedup
- Measure with: `SELECT * FROM pg_stat_progress_create_index;`

---

## 5. INPUT VALIDATION BENCHMARKS

### Benchmark 5.1: Unbounded Input Parsing
**Purpose**: Test CPU exhaustion with long malicious input

```sql
-- Test 1: Very long input with many commas (sparse vector)
SELECT (SELECT repeat('1:1.0,', 1000000) || '1:1.0')::sparsevec;
-- Should error quickly, not hang

-- Test 2: Very long float strings
SELECT ('[' || repeat('1.123456789012345,', 100000) || '1.0]')::vector;
-- Should error or timeout, not consume excessive CPU
```

**Validation**:
- Set statement_timeout = '5s'
- Monitor CPU usage during parse
- Should error with dimension/nnz limit, not timeout

---

### Benchmark 5.2: Dimension Limit Enforcement
**Purpose**: Verify limits are checked early

```sql
-- Test vector limits
SELECT array_fill(1.0, ARRAY[16001])::vector;  -- Should error immediately
SELECT array_fill(1.0, ARRAY[16000])::vector;  -- Should succeed

-- Test sparse vector limits
SELECT (SELECT string_agg(i || ':1.0', ',') FROM generate_series(1, 16001) i)::sparsevec;
```

---

## 6. MEMORY LEAK BENCHMARKS

### Benchmark 6.1: Buffer Pin Leak Detection
**Purpose**: Test if error paths leak buffer pins

```sql
-- Create scenario that triggers errors during scan
CREATE TABLE leak_test (id SERIAL, vec vector(128));
INSERT INTO leak_test VALUES
  (1, array_fill(1.0, ARRAY[128])::vector),
  (2, array_fill(2.0, ARRAY[128])::vector);

CREATE INDEX idx_leak ON leak_test USING ivfflat (vec) WITH (lists = 10);

-- Check initial buffer usage
SELECT count(*) FROM pg_buffercache WHERE relfilenode = 'idx_leak'::regclass::oid;

-- Trigger many scans, some with errors
DO $$
BEGIN
  FOR i IN 1..1000 LOOP
    BEGIN
      PERFORM * FROM leak_test ORDER BY vec <-> array_fill(random(), ARRAY[128])::vector LIMIT 1;
    EXCEPTION WHEN OTHERS THEN
      NULL;  -- Swallow errors
    END;
  END LOOP;
END $$;

-- Check if buffer count increased abnormally
SELECT count(*) FROM pg_buffercache WHERE relfilenode = 'idx_leak'::regclass::oid;
```

**Expected**: Buffer count should stabilize, not grow linearly

---

## 7. COMPREHENSIVE STRESS TEST

### Benchmark 7.1: Combined Stress
**Purpose**: Test all issues simultaneously

```sql
-- Create large dataset
CREATE TABLE stress_test (
  id SERIAL PRIMARY KEY,
  vec_small vector(128),
  vec_large vector(2000),
  sparse sparsevec(10000)
);

-- Insert 1M rows
INSERT INTO stress_test
SELECT
  i,
  array_fill(random(), ARRAY[128])::vector(128),
  array_fill(random(), ARRAY[2000])::vector(2000),
  (SELECT string_agg(j || ':' || random()::text, ',')
   FROM generate_series(1, (random() * 1000)::int) j)::sparsevec
FROM generate_series(1, 1000000) i;

-- Create all index types
SET maintenance_work_mem = '16GB';
SET max_parallel_maintenance_workers = 4;

\timing
CREATE INDEX idx_stress_ivf_small ON stress_test USING ivfflat (vec_small) WITH (lists = 1000);
CREATE INDEX idx_stress_ivf_large ON stress_test USING ivfflat (vec_large) WITH (lists = 10000);
CREATE INDEX idx_stress_hnsw ON stress_test USING hnsw (vec_small) WITH (m = 16);

-- Run concurrent queries
\! for i in {1..10}; do psql -c "SELECT * FROM stress_test ORDER BY vec_small <-> array_fill(random(), ARRAY[128])::vector(128) LIMIT 10" & done
```

**Monitor**:
- Peak memory usage
- CPU utilization
- Buffer cache usage
- Parallel worker efficiency
- Time to completion

---

## SUMMARY TABLE

| Benchmark | Purpose | Critical Finding Validated | Expected Runtime |
|-----------|---------|---------------------------|------------------|
| 1.1 | Integer overflow | K-means multiplication | 5-10 min |
| 1.2 | Integer overflow | Sparse vector size | 1 min |
| 2.1 | Resource exhaustion | maxProbes allocation | 5 min |
| 2.2 | Resource exhaustion | K-means samples | 15-30 min |
| 2.3 | Resource exhaustion | HNSW recursion | 5 min |
| 3.1 | Concurrency | PRNG corruption | 10 min |
| 3.2 | Concurrency | Flushed flag race | 2 min |
| 4.1 | Performance | K-means redundancy | 20 min |
| 4.2 | Performance | Sparse parse overhead | 5 min |
| 4.3 | Performance | Lock contention | 15 min |
| 5.1 | Input validation | Unbounded parsing | 2 min |
| 5.2 | Input validation | Dimension limits | 1 min |
| 6.1 | Memory leak | Buffer pins | 5 min |
| 7.1 | Stress test | All issues | 1-2 hours |

**Total estimated time**: ~2-3 hours for full suite
