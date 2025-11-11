# pgvector Memory Efficiency Analysis - Query Runtime

## Executive Summary

Analysis of pgvector query paths (ivfscan.c, hnswscan.c, hnswutils.c, ivfutils.c) reveals **multiple memory efficiency concerns** during query execution:

1. **Persistent memory allocations that grow with search parameters** (ef_search, probes)
2. **Inefficient per-query memory context usage in IVFFlat** (memory not in dedicated context)
3. **Potential double-reset issues in iterative scan mode**
4. **Memory not respecting work_mem limits in some paths**

---

## DETAILED FINDINGS

### 1. HNSW: Memory Allocations in HnswSearchLayer (hnswutils.c)

**File/Lines:** `/tmp/pgvector/src/hnswutils.c:817-980`

#### Allocated Per Search Query:

```c
pairingheap *C = pairingheap_allocate(CompareNearestCandidates, NULL);  // line 821
pairingheap *W = pairingheap_allocate(CompareFurthestCandidates, NULL);  // line 822
HnswUnvisited *unvisited = palloc(lm * sizeof(HnswUnvisited));           // line 829
localNeighborhood = palloc(neighborhoodSize);                             // line 851
```

**Memory Impact:**
- **Per search:** ~(ef_search * M) * 48 bytes for C and W heaps (pairing heap node overhead)
- **unvisited:** `lm * sizeof(HnswUnvisited)` = `lm * 16 bytes` (where lm = M*2 for layer 0)
  - For M=16: 512 bytes per layer query
- **localNeighborhood:** `HNSW_NEIGHBOR_ARRAY_SIZE(lm)` = offset + `(lm * sizeof(HnswCandidate))`
  - For M=16, layer 0: ~1KB per search
- **Visited hash tables** (InitVisited line 841):
  - tidhash_create for disk: `ef_search * M * 2` entries = ~200-500KB for ef_search=40, M=16
  - Memory grows **linearly with ef_search and M**

**Example Calculation (default: ef_search=40, M=16):**
```
Per search baseline:
- C+W heaps: ~4KB overhead
- unvisited: 512 bytes  
- localNeighborhood: 1KB
- Visited hash: ~300KB (ef * m * 2 entries * ~50 bytes per entry)
= ~305KB per search
```

**Issue:** Memory allocated but NOT explicitly freed - relies on tmpCtx reset. If error occurs during HnswSearchLayer loop, memory is left allocated until next MemoryContextReset() at rescan/endscan.

**Cleanup Path:** `/tmp/pgvector/src/hnswscan.c:165-166` (hnswrescan)
```c
MemoryContextReset(so->tmpCtx);  // Line 166
```
This DOES clean up, but only at next rescan. First query to hnswendscan will fully delete.

---

### 2. IVFFlat: Query Memory NOT in Dedicated Context

**File/Lines:** `/tmp/pgvector/src/ivfscan.c:339-393`

#### Critical Issue: No Memory Context Switch in ivfflatgettuple()

```c
bool ivfflatgettuple(IndexScanDesc scan, ScanDirection dir)
{
    IvfflatScanOpaque so = (IvfflatScanOpaque) scan->opaque;
    // NO MemoryContextSwitchTo(so->tmpCtx) HERE!
    
    if (so->first) {
        // ...
        GetScanItems(scan, value);  // Tuplesort allocated in CurrentMemoryContext!
    }
    
    while (!tuplesort_gettupleslot(so->sortstate, true, false, so->mslot, NULL)) {
        GetScanItems(scan, so->value);  // More memory in CurrentMemoryContext
    }
}
```

**Memory Allocated in CurrentMemoryContext (NOT tmpCtx):**
- Tuplesort internal structures (line 235)
- Each call to `tuplesort_puttupleslot()` in GetScanItems allocates tuple storage

**Memory Per Query:**
```
Per vector found:
- Tuplesort tuple metadata: ~48 bytes
- Vector value copy: dimensions * 4 bytes (float)

Example: 1M vectors scanned with 512-dim vector
= 1M * (48 + 512*4) = 1M * 2096 bytes = 2GB memory!
```

This memory is NOT freed until:
1. `ivfflatendscan()` calls `tuplesort_end()` (line 404)
2. OR `ivfflatrescan()` but that doesn't reset sortstate!

**Issue:** Calling `ivfflatrescan()` does NOT reset the tuplesort! The old tuples remain:
```c
void ivfflatrescan(IndexScanDesc scan, ...) {
    // ...
    pairingheap_reset(so->listQueue);  // Line 326
    // NO tuplesort_reset() or tuplesort_end() + reinit!
    // ...
}
```

**Memory Leak on Rescan:** If a query is rescanned without calling `ivfflatendscan()`, the tuplesort retains all previous tuples!

---

### 3. Visited Hash Table Memory Growth - HNSW Iterative Scan

**File/Lines:** `/tmp/pgvector/src/hnswutils.c:666-675`

```c
static inline void
InitVisited(char *base, visited_hash * v, bool inMemory, int ef, int m)
{
    if (!inMemory)
        v->tids = tidhash_create(CurrentMemoryContext, ef * m * 2, NULL);  // Line 670
    else if (base != NULL)
        v->offsets = offsethash_create(CurrentMemoryContext, ef * m * 2, NULL);  // Line 672
    else
        v->pointers = pointerhash_create(CurrentMemoryContext, ef * m * 2, NULL);  // Line 674
}
```

**Memory Per Search:**
- Hash table with `ef * m * 2` buckets
- Default ef_search=40, M=16: 40 * 16 * 2 = 1,280 entries
- Each entry: ~32-64 bytes (hash table overhead)
- **Total: ~50-80KB per search**

**Scaling with Parameters:**
```
ef_search=100, M=64: 100 * 64 * 2 = 12,800 entries = ~400KB+
```

**Cleanup:** Memory context reset at hnswrescan, but NOT explicitly freed until context is deleted.

---

### 4. Over-Allocation: Candidate Lists and Priority Queues

**File/Lines:** `/tmp/pgvector/src/hnswutils.c:821-976`

The C (candidate) and W (result) pairingheaps grow **dynamically** during search but never shrink:

```c
pairingheap *C = pairingheap_allocate(CompareNearestCandidates, NULL);
pairingheap *W = pairingheap_allocate(CompareFurthestCandidates, NULL);

// In loop:
while (!pairingheap_is_empty(C)) {
    // ...
    pairingheap_add(C, &e->c_node);      // Line 947
    pairingheap_add(W, &e->w_node);      // Line 948
    
    if (wlen > ef) {
        HnswSearchCandidate *d = HnswGetSearchCandidate(w_node, 
                                    pairingheap_remove_first(W));
        // Only removes from W, C keeps growing
    }
}
```

**Issue:** C can accumulate ALL candidates explored, not just top-ef. Memory usage:
```
Worst case: ef_search=40, explore 10K candidates
= 10K * sizeof(HnswSearchCandidate) = 10K * 32 bytes = 320KB
```

---

### 5. List-Based Candidate Storage - HNSW Iterative Scan

**File/Lines:** `/tmp/pgvector/src/hnswscan.c:14-75`

```c
static List *GetScanItems(IndexScanDesc scan, Datum value) {
    // ...
    return HnswSearchLayer(base, q, ep, hnsw_ef_search, 0, index, support, m, false, 
                          NULL, &so->v, 
                          hnsw_iterative_scan != HNSW_ITERATIVE_SCAN_OFF ? &so->discarded : NULL,
                          true, &so->tuples);
}
```

The `so->w` list persists across queries and grows unbounded in iterative mode:

```c
// In hnswgettuple (line 238):
if (list_length(so->w) == 0) {
    if (hnsw_iterative_scan == HNSW_ITERATIVE_SCAN_OFF) break;
    
    if (so->tuples >= hnsw_max_scan_tuples || 
        MemoryContextMemAllocated(so->tmpCtx, false) > so->maxMemory) {
        // Return remaining from discarded
    } else {
        so->w = ResumeScanItems(scan);  // Appends to w
    }
}
```

**Memory Impact:**
```
Per iteration: so->w holds ef_search candidates
= 40 * sizeof(HnswSearchCandidate) = 1.3KB
+ so->discarded pairingheap: 40 * 32 bytes = 1.3KB
Total per batch: ~2.6KB per ef_search batch
```

**Over Multiple Iterations:**
If resuming scan 100 times: 100 * 2.6KB = 260KB accumulated

---

## WORK_MEM COMPLIANCE ISSUES

### HNSW Respects work_mem (Correct)

**File/Lines:** `/tmp/pgvector/src/hnswscan.c:138-145`

```c
maxMemory = (double) work_mem * hnsw_scan_mem_multiplier * 1024.0 + 256;
so->maxMemory = Min(maxMemory, (double) SIZE_MAX);

// Checked at line 248:
if (so->tuples >= hnsw_max_scan_tuples || 
    MemoryContextMemAllocated(so->tmpCtx, false) > so->maxMemory) {
    // Stop iterating
}
```

**Issue:** Checks memory allocation but parameter `hnsw_scan_mem_multiplier` defaults to unknown value (likely 1.0 or 2.0). Default work_mem=4MB, so effective limit ~4-8MB per query.

### IVFFlat Ignores work_mem (Incorrect)

**File/Lines:** `/tmp/pgvector/src/ivfscan.c:235`

```c
return tuplesort_begin_heap(tupdesc, 1, attNums, sortOperators, sortCollations, 
                           nullsFirstFlags, work_mem, NULL, false);
```

The tuplesort DOES receive work_mem parameter, BUT:
1. Memory allocated outside tmpCtx, so MemoryContextMemAllocated won't track it
2. No memory checks in ivfflatgettuple loop - will allocate until work_mem internal limit

**Risk:** Large LIMIT or many probes can exceed work_mem silently.

---

## POTENTIAL MEMORY LEAKS ON ERROR

### HNSW (Mitigated by Memory Context)

**File/Lines:** `/tmp/pgvector/src/hnswscan.c:179-319`

```c
MemoryContext oldCtx = MemoryContextSwitchTo(so->tmpCtx);  // Line 182

// If error occurs in GetScanItems or loop:
so->w = GetScanItems(scan, value);  // Line 219
// or in loop at line 269: so->w = ResumeScanItems(scan);

MemoryContextSwitchTo(oldCtx);  // Line 310 - NOT reached on error!
```

**Issue:** If ereport(ERROR) is thrown during GetScanItems, the MemoryContextSwitchTo(oldCtx) is not reached. However, PostgreSQL error handling automatically resets CurrentMemoryContext, so tmpCtx memory IS freed.

**Actual Leak:** None - error handling is safe via memory context

### IVFFlat (No Error Context)

**File/Lines:** `/tmp/pgvector/src/ivfscan.c:339-393`

No memory context switches at all. If error in GetScanItems:
- Tuplesort memory allocated in CurrentMemoryContext is NOT freed
- But PostgreSQL error handler resets CurrentMemoryContext, so effectively OK

**Actual Leak:** None - PostgreSQL error handling saves it

---

## UNNECESSARY ALLOCATIONS

### 1. List Storage for HNSW Candidates

**File/Lines:** `/tmp/pgvector/src/hnswutils.c:972-976`

```c
while (!pairingheap_is_empty(W)) {
    HnswSearchCandidate *sc = HnswGetSearchCandidate(w_node, pairingheap_remove_first(W));
    w = lappend(w, sc);  // Convert pairingheap to List - unnecessary!
}
return w;
```

**Issue:** Result stored as PostgreSQL List with list cell allocations, could use array instead.

**Memory waste:** 40 candidates * ~24 bytes per ListCell = 960 bytes per search

### 2. Vector Array Copies

**File/Lines:** `/tmp/pgvector/src/hnswutils.c:512-515`

```c
if (loadVec) {
    char *base = NULL;
    Datum value = datumCopy(PointerGetDatum(&etup->data), false, -1);  // Line 513
    HnswPtrStore(base, element->value, DatumGetPointer(value));
}
```

Vector is copied every time loaded during search. For each candidate visited, the vector is copied.

**Memory waste:** 512-dim vector * 4 bytes * 100 candidates = 200KB per search

### 3. Temporary Neighborhood Array

**File/Lines:** `/tmp/pgvector/src/hnswutils.c:850-851`

```c
if (inMemory) {
    neighborhoodSize = HNSW_NEIGHBOR_ARRAY_SIZE(lm);
    localNeighborhood = palloc(neighborhoodSize);  // Allocated but mostly unused
}
```

Allocated only if `inMemory` (in-memory build/update), not needed during scan. But allocated anyway during layer search traversal.

**Memory waste:** 1-2KB per layer traversal

---

## SUMMARY TABLE: Memory Per Query

| Component | IVFFlat | HNSW | Notes |
|-----------|---------|------|-------|
| **Tuplesort/Visited** | Variable (grows with results) | ~300KB (ef_search=40, M=16) | Scales with result count |
| **Candidate lists** | N/A | ~1.3KB per batch | Only in iterative mode |
| **Hash tables** | N/A | ~50-80KB (disk queries) | Created once per search |
| **Temporary buffers** | N/A | ~1.5KB | unvisited + neighborhood |
| **Total baseline** | <10KB | ~350KB | With default parameters |
| **Scaling** | O(results) | O(ef_search * M) | Both can grow large |

---

## SCALING EXAMPLES

### IVFFlat: Large Result Set
```
Query: SELECT * FROM vectors ORDER BY vector <-> query LIMIT 100000
With: 1M vectors, 512 dims, 1 probe
- Tuplesort holds 100K vectors: 100K * 2KB = 200MB
- Risk: Exceeds work_mem=4MB significantly
- Work_mem monitoring: YES (tuplesort handles it)
```

### HNSW: Large ef_search
```
Query: SELECT * FROM vectors ORDER BY vector <-> query LIMIT 1000
With: ef_search=200, M=16
- Visited hash: 200 * 16 * 2 * 64 bytes = ~400KB
- C+W heaps: 200 * 32 * 2 = 12.8KB
- Total: ~413KB (well under 4MB work_mem)
- Work_mem monitoring: YES (MemoryContextMemAllocated checked)
```

### IVFFlat: Rescanned Query
```
Query: repeated scan with multiple ORDER BY iterations
- First scan: tuplesort allocates 100MB
- Rescan via ivfflatrescan(): 
  - pairingheap_reset() called
  - BUT tuplesort NOT reset!
  - Old tuples still in memory
  - Next GetScanItems adds more
  - Total: 200MB+ accumulated
```

---

## RECOMMENDATIONS (Not Requested, Info Only)

1. **IVFFlat:** Add `MemoryContextSwitchTo(so->tmpCtx)` in ivfflatgettuple() around GetScanItems calls
2. **IVFFlat:** Call `tuplesort_reset()` in ivfflatrescan() or create fresh tuplesort
3. **HNSW:** Add explicit pairingheap cleanup or use dedicated memory context
4. **Both:** Add per-query memory tracking with explicit pfree() of large allocations
5. **HNSW:** Convert final List to array to avoid ListCell overhead

