# PGVECTOR Memory Safety Analysis - Executive Summary

## Analysis Completed
**Date:** November 11, 2025  
**Codebase:** pgvector (PostgreSQL vector extension)  
**Files Analyzed:** 27 C/H source files

## Critical Findings

### 1. INTEGER OVERFLOW IN ALLOCATION SIZE CALCULATIONS
**Severity:** CRITICAL  
**Files Affected:**
- `/tmp/pgvector/src/ivfkmeans.c` (Lines 288, 291)
- `/tmp/pgvector/src/ivfutils.c` (Line 27)

**Description:**  
Integer overflow occurs in multiplication of allocation sizes without proper bounds checking. The vulnerable code performs `int * int` multiplication before casting to Size type.

**Example from ivfkmeans.c line 291:**
```c
Size halfcdistSize = sizeof(float) * numCenters * numCenters;
```
If `numCenters = 46,341`, then `numCenters * numCenters = 2,147,683,281` which overflows to ~-2.1B in signed int, resulting in incorrect allocation size.

**Exploitation Path:**
1. Create IVF index with crafted parameters causing numCenters overflow
2. Triggers buffer allocation with wrong size
3. Subsequent array access causes heap overflow
4. Potential information disclosure or code execution

**Impact:** HIGH - Can be triggered via SQL commands that create indexes

---

### 2. NULL POINTER DEREFERENCE IN SCAN CODE
**Severity:** CRITICAL/HIGH  
**File:** `/tmp/pgvector/src/ivfscan.c` (Line 196)

**Description:**  
The `scan->orderByData` pointer is dereferenced without NULL check:

```c
if (scan->orderByData->sk_flags & SK_ISNULL)  // Line 196 - No NULL check!
```

The NULL check occurs later at line 364, long after dereferencing.

**Impact:** DoS via segmentation fault when querying IVFFlat indexes

---

## Additional High-Severity Issues

### 3. Bounds Check Timing Bug (sparsevec.c:1111)
The safety check for array bounds occurs AFTER writing to the array:
```c
for (int i = 0; i < result->nnz; i++) {
    if (rx[i] == 0) continue;
    if (j >= newResult->nnz)  // TOO LATE - already wrote at line 1114
        elog(ERROR, "safety check failed");
    newResult->indices[j] = result->indices[i];  // Line 1114
```

### 4. Unsafe Macro Arithmetic (hnsw.h:64-66)
Size calculations in macros without overflow validation:
```c
#define HNSW_NEIGHBOR_ARRAY_SIZE(lm) \
    (offsetof(...) + sizeof(HnswCandidate) * (lm))
```

---

## Summary Statistics

| Severity | Count | Files |
|----------|-------|-------|
| CRITICAL | 2 | ivfkmeans.c, ivfutils.c |
| HIGH | 3 | ivfscan.c, hnsw.h, sparsevec.c |
| MEDIUM | 2 | ivfkmeans.c (multiple issues) |
| LOW | 1 | vector.c |
| **TOTAL** | **8** | **6 unique files** |

---

## Risk Assessment

**Overall Risk Level:** HIGH

**Attack Surface:**
- IVF Index creation with malicious parameters
- Query execution against indexes with crafted parameters
- Memory corruption via integer overflow attacks

**PostgreSQL Version Vulnerable:** All versions with pgvector installed

---

## Immediate Actions Required

1. **Apply integer overflow fixes** in ivfkmeans.c and ivfutils.c
2. **Add NULL pointer checks** in ivfscan.c before dereference operations
3. **Fix timing of bounds checks** in sparsevec.c
4. **Convert unsafe macros** to inline functions with validation

## Testing Recommendations

- Enable AddressSanitizer (-fsanitize=address)
- Fuzzing with large index parameters
- Review compilation with -Wall -Wextra -Werror

---

## Files to Review

**High Priority (Critical Issues):**
- `/tmp/pgvector/src/ivfkmeans.c`
- `/tmp/pgvector/src/ivfutils.c`
- `/tmp/pgvector/src/ivfscan.c`

**Medium Priority (High Issues):**
- `/tmp/pgvector/src/sparsevec.c`
- `/tmp/pgvector/src/hnsw.h`

**Documentation:**
See detailed findings in the comprehensive report for specific line numbers and code contexts.
