# pgvector Search Correctness Issues - Detailed Analysis

## Executive Summary
Analysis of pgvector codebase (12,119 lines) reveals **10 search correctness issues** across IVFFlat and HNSW implementations that could return wrong results, incorrect distances, missing results, or wrong ordering.

---

## CRITICAL ISSUES

### 1. Float/Double Precision Mismatch in HNSW Search
**File:** `/tmp/pgvector/src/hnswutils.c:1329`
**Severity:** CRITICAL
**Impact:** Precision loss causes incorrect distance comparisons and potentially wrong result ordering

**Problem:**
```c
// Line 1325-1329
HnswSearchCandidate *sc = lfirst(lc2);  // sc->distance is double
HnswCandidate *hc = palloc(sizeof(HnswCandidate));
hc->element = sc->element;
hc->distance = sc->distance;  // IMPLICIT CAST: double → float
```

- `HnswSearchCandidate.distance` is `double` (hnsw.h:177)
- `HnswCandidate.distance` is `float` (hnsw.h:161)
- Assignment at line 1329 implicitly casts `double` to `float`, losing ~7 digits of precision
- Affects: neighbor selection during index building and insertion (`HnswFindElementNeighbors`)

**How it affects results:**
- Distance values lose precision during neighbor selection
- Two distances that should be different may become identical after truncation
- Tie-breaking based on distances becomes unpredictable
- Can cause suboptimal neighbor selection, affecting future searches

**Example scenario:**
```
Original distances (double): 1.23456789012345, 1.23456789012346
After cast to float: both become 1.234568
Tie-breaking becomes ambiguous
```

---

### 2. Unsafe Distance Comparisons Without Infinity/NaN Handling
**File:** `/tmp/pgvector/src/hnswutils.c:887, 923, 929`
**Severity:** CRITICAL
**Impact:** Incorrect termination of search, missing results, wrong ordering

**Problem:**
```c
// Line 887: Main search loop termination
if (c->distance > f->distance)
    break;

// Line 929: Result filtering
if (eElement == NULL || !(eDistance < f->distance || alwaysAdd)) {
    // Discard result
    continue;
}
```

- No checks for NaN or Infinity in distance values
- If `c->distance` is NaN, condition `c->distance > f->distance` is always FALSE
- Searches continue indefinitely examining unreachable nodes
- If `eDistance` is NaN, results are incorrectly filtered

**Comparison semantics with special values:**
```
NaN < x = false
NaN > x = false
NaN == x = false
NaN <= x = false
NaN >= x = false
```

**How it affects results:**
1. **NaN distances:** Nodes with NaN distances are never pruned
   - Memory exhaustion
   - Incorrect candidates added to result set
   - Wrong results returned

2. **Infinity distances:** Can dominate comparisons
   - Valid results skipped
   - Search bounds broken

3. **Search never terminates:** Loop at line 881-969 continues until all candidates exhausted

---

### 3. Double-to-Float Precision Loss in Neighbor Selection
**File:** `/tmp/pgvector/src/hnswutils.c:1045`
**Severity:** CRITICAL
**Impact:** Incorrect neighbor pruning, suboptimal graph structure, worse search quality

**Problem:**
```c
// Line 1045 in CheckElementCloser()
float distance = HnswGetDistance(eValue, riValue, support);
// HnswGetDistance returns double, implicitly cast to float

// Line 1047 - comparison after precision loss
if (distance <= e->distance)  // both are float, but lost precision
    return false;
```

- `HnswGetDistance()` returns `double` but assigned to `float`
- Comparison at line 1047 uses truncated distance value
- Called during neighbor selection (Algorithm 4 from paper)
- Affects: `SelectNeighbors()` → `HnswFindElementNeighbors()` → index building

**How it affects results:**
- Neighbors selected based on truncated distances
- Graph structure becomes suboptimal
- Future searches using this suboptimal graph return lower quality results
- Systematic bias in neighbor selection degrades search effectiveness

---

## MODERATE ISSUES

### 4. Off-by-One in IVFFlat List Probing Logic
**File:** `/tmp/pgvector/src/ivfscan.c:123`
**Severity:** MODERATE
**Impact:** Missing results if probes=0, edge case in batch probing

**Problem:**
```c
// Line 123 in GetScanItems()
while (so->listIndex < so->maxProbes && (++batchProbes) <= so->probes)
{
    BlockNumber searchPage = so->listPages[so->listIndex++];
    // ...
}
```

- If `so->probes == 0`, condition `(++batchProbes) <= so->probes` fails immediately
- No lists are probed → no results returned
- Edge case: When iterative scanning with probes parameter set to 0

**How it affects results:**
- With probes=0 (edge case), query returns empty result set
- With large ef values, batching behavior is incorrect
- Correct behavior: should probe at least 1 list if maxProbes > 0

**When triggered:**
```
SELECT ... ORDER BY embedding <-> query LIMIT k;
-- If ivfflat_probes=0 set explicitly
-- OR iterative scan with probes update
```

---

### 5. Inadequate wlen Limit Enforcement
**File:** `/tmp/pgvector/src/hnswutils.c:957-966`
**Severity:** MODERATE
**Impact:** Returning more than ef results, incorrect result count, memory overconsumption

**Problem:**
```c
// Lines 957-966 in HnswSearchLayer()
if (CountElement(skipElement, eElement))
{
    wlen++;

    /* No need to decrement wlen */
    if (wlen > ef)
    {
        HnswSearchCandidate *d = HnswGetSearchCandidate(w_node,
                                  pairingheap_remove_first(W));
        if (discarded != NULL)
            pairingheap_add(*discarded, &d->w_node);
    }
}
```

- `wlen` is incremented BEFORE checking limit
- When `wlen > ef`, only ONE element is removed
- If multiple unvisited candidates with same distance are added
- Multiple elements can be added before next removal
- Results in `wlen` far exceeding `ef`

**Example execution:**
```
ef = 40, unvisitedLength = 50 candidates with same distance
Loop iteration:
  wlen = 40, alwaysAdd = false
  Add 50 candidates (each satisfies eDistance < f->distance)
  Each triggers wlen++
  Result: wlen = 90 (should be ~40)
  Only 1 removal per iteration
```

**How it affects results:**
1. **Wrong result count:** Returns more than requested
2. **Incorrect filtering:** Results further away included
3. **Memory overhead:** Keeps unnecessary candidates in memory
4. **Algorithm violation:** HNSW spec says exactly ef candidates should be returned

---

### 6. Unsynchronized Element State in HNSW Scan
**File:** `/tmp/pgvector/src/hnswscan.c:300, 286-300`
**Severity:** MODERATE
**Impact:** Race condition, incorrect heaptid sequence, potential data corruption

**Problem:**
```c
// Line 286-300 in hnswgettuple()
if (element->heaptidsLength == 0) {
    so->w = list_delete_last(so->w);
    continue;
}

heaptid = &element->heaptids[--element->heaptidsLength];
```

- Uses pre-decrement: `--element->heaptidsLength`
- Modifies element state without synchronization
- Element is shared across multiple scan iterations
- Between `hnswgettuple()` calls, same element accessed again

**Thread-safety issue:**
- If same index is scanned concurrently
- Element shared in memory
- Pre-decrement modifies shared state
- Race condition between check at line 286 and decrement at line 300

**How it affects results:**
1. **Incorrect heap TID returned:** Skipped or duplicated rows
2. **Out-of-bounds access:** If external modification of heaptidsLength
3. **Consistency violation:** Element state corrupted between scan iterations
4. **Missing results:** Heaptids skipped due to race condition

**Scenario:**
```
Thread A: Check heaptidsLength == 0 (line 286) → false
Thread B: Modifies heaptidsLength
Thread A: Pre-decrement gives wrong index
```

---

### 7. Equals-Distance Results Filtered Without Tie-Breaking
**File:** `/tmp/pgvector/src/hnswutils.c:906, 929`
**Severity:** MODERATE
**Impact:** Missing results with equal distances, incorrect determinism

**Problem:**
```c
// Line 906: Decide if always add
bool alwaysAdd = wlen < ef;

// Line 929: Filter candidates
if (eElement == NULL || !(eDistance < f->distance || alwaysAdd))
{
    // Skip this candidate
    continue;
}
```

- Condition: `eDistance < f->distance || alwaysAdd`
- If `eDistance == f->distance` AND `wlen >= ef`:
  - First part: `eDistance < f->distance` = FALSE
  - Second part: `alwaysAdd` = FALSE
  - Entire condition = FALSE
  - Result is DISCARDED

**Impact on equal distances:**
```
Candidates with distance = 1.0:
  1st candidate: wlen=39, alwaysAdd=true → ADDED
  2nd candidate: wlen=40, alwaysAdd=false, eDistance==f->distance → DISCARDED
  3rd candidate: DISCARDED
  ...
Only 1 result with distance 1.0, others lost
```

**How it affects results:**
1. **Non-deterministic:** Which equal-distance results survive depends on processing order
2. **Missing results:** Some results with same distance filtered
3. **Inconsistent LIMIT behavior:** Top-K may return < K results
4. **Violates algorithm spec:** Paper expects ef results, not fewer

---

### 8. Incomplete Batch Exhaustion in Iterative Scan
**File:** `/tmp/pgvector/src/hnswscan.c:63-76` (ResumeScanItems)
**Severity:** MODERATE
**Impact:** Inconsistent result ordering, incorrect LIMIT handling

**Problem:**
```c
// Lines 63-75 in ResumeScanItems()
for (int i = 0; i < batch_size; i++)
{
    HnswSearchCandidate *sc;

    if (pairingheap_is_empty(so->discarded))
        break;

    sc = HnswGetSearchCandidate(w_node, pairingheap_remove_first(so->discarded));
    ep = lappend(ep, sc);
}

return HnswSearchLayer(base, &so->q, ep, batch_size, 0, index,
                       &so->support, so->m, false, NULL, &so->v,
                       &so->discarded, false, &so->tuples);
```

- Batches discarded candidates `batch_size` at a time
- But `HnswSearchLayer()` may return fewer due to filtering
- Can cause: stalled iteration, missing results

**How it affects results:**
1. **Incomplete batches:** Some candidates never processed
2. **Missing results:** Batching prevents full exhaustion
3. **Incorrect ordering:** Results from batches intermixed incorrectly
4. **LIMIT violation:** LIMIT N may not return exactly N results

---

## MINOR ISSUES

### 9. Insufficient NULL Query Vector Handling
**File:** `/tmp/pgvector/src/hnswscan.c:87-88, ivfscan.c:196-199`
**Severity:** MINOR
**Impact:** Silent distance calculation failures, misleading results

**Problem:**

In hnswscan.c (GetScanValue):
```c
// Line 87-88
if (scan->orderByData->sk_flags & SK_ISNULL)
    value = PointerGetDatum(NULL);
else
    value = scan->orderByData->sk_argument;
```

In hnswutils.c (HnswLoadElementImpl):
```c
// Lines 548-553
if (distance != NULL)
{
    if (DatumGetPointer(q->value) == NULL)
        *distance = 0;  // Silent fallback to 0
    else
        *distance = HnswGetDistance(q->value, ..., support);
}
```

**Issues:**
1. NULL query vector silently becomes distance=0 for all candidates
2. No error message or warning
3. All results appear equidistant
4. Violates expectation: NULL query should likely fail or warn

**How it affects results:**
- NULL query returns arbitrary ordering
- No distance information available
- Misleading results (all same distance)
- Hard to debug: silent semantic change

---

### 10. previousDistance Initialization with Negative Infinity
**File:** `/tmp/pgvector/src/hnswscan.c:165, 304-308`
**Severity:** MINOR
**Impact:** Edge case in strict mode, potential overflow

**Problem:**
```c
// Line 165 in hnswrescan()
so->previousDistance = -get_float8_infinity();

// Line 304-307 in hnswgettuple()
if (hnsw_iterative_scan == HNSW_ITERATIVE_SCAN_STRICT)
{
    if (sc->distance < so->previousDistance)
        continue;
    so->previousDistance = sc->distance;
}
```

**Issue:**
- Negative infinity is special case for "no previous result"
- If first result has distance = -infinity, comparison fails
- Comparison: `-infinity < -infinity` = FALSE
- Result is returned (correct by accident)

**How it affects results:**
1. **Edge case fragility:** Depends on -infinity as sentinel
2. **Weird distances:** If index contains -infinity distances (shouldn't happen but...)
3. **Strict mode semantics:** Non-obvious that negative infinity used as sentinel

---

## SUMMARY TABLE

| Issue | File | Line | Severity | Category | Impact |
|-------|------|------|----------|----------|---------|
| Double→Float cast | hnswutils.c | 1329 | CRITICAL | Precision Loss | Wrong distances, wrong ordering |
| NaN/Infinity handling | hnswutils.c | 887, 923, 929 | CRITICAL | Comparison Logic | Infinite loops, wrong results |
| Double→Float in neighbor select | hnswutils.c | 1045 | CRITICAL | Precision Loss | Suboptimal graph, lower quality |
| List probing off-by-one | ivfscan.c | 123 | MODERATE | Logic Error | Empty results if probes=0 |
| wlen overflow | hnswutils.c | 957-966 | MODERATE | Limit Enforcement | Too many results |
| Element state race condition | hnswscan.c | 300 | MODERATE | Concurrency | Incorrect rows |
| Equal-distance filtering | hnswutils.c | 929 | MODERATE | Filtering Logic | Missing results |
| Incomplete batch exhaustion | hnswscan.c | 63-76 | MODERATE | Iterator Logic | Inconsistent ordering |
| NULL vector handling | hnswscan.c, ivfscan.c | 87, 196 | MINOR | Error Handling | Silent failures |
| Negative infinity sentinel | hnswscan.c | 165, 304 | MINOR | Edge Case | Fragile logic |

---

## RECOMMENDATIONS

### Immediate Fixes (High Priority)
1. **Use double for all distance calculations** - Change HnswCandidate.distance to double
2. **Add NaN/Infinity checks** - Validate distances before comparisons
3. **Enforce wlen <= ef** - Check limit before adding, not after

### Medium Priority
4. **Fix list probing logic** - Use `(++batchProbes) < so->probes` or `while (so->listIndex < ...) && (++batchProbes) <= so->probes && batchProbes >= 1`
5. **Add synchronization** - Use locks for element heaptid iteration
6. **Improve tie-breaking** - Use stable sort or random seed for deterministic results

### Low Priority
7. **Document NULL vector behavior** - Error or document semantic
8. **Replace negative infinity sentinel** - Use explicit flag instead

---

## TEST CASES TO ADD

```sql
-- Test 1: Distances with same values
SELECT id, distance FROM embeddings
ORDER BY embedding <-> '[1,0,0]' LIMIT 10;
-- Verify: Deterministic ordering of equal distances

-- Test 2: Edge case with probes=0
SET ivfflat.probes = 0;
SELECT COUNT(*) FROM embeddings
ORDER BY embedding <-> '[1,0,0]' LIMIT 10;
-- Verify: Returns results (not 0)

-- Test 3: Large ef_search
SET hnsw.ef_search = 1000;
SELECT COUNT(*) FROM embeddings
ORDER BY embedding <-> '[1,0,0]' LIMIT 100;
-- Verify: Returns exactly 100 (not 1000+)

-- Test 4: NULL query vector
SELECT COUNT(*) FROM embeddings
ORDER BY embedding <-> NULL LIMIT 10;
-- Verify: Error or documented behavior
```

---

## FILES AFFECTED

1. `/tmp/pgvector/src/hnswutils.c` - HNSW search and neighbor selection
2. `/tmp/pgvector/src/hnswscan.c` - HNSW scan iteration
3. `/tmp/pgvector/src/ivfscan.c` - IVFFlat scan iteration
4. `/tmp/pgvector/src/hnsw.h` - Data structures (precision mismatch)
