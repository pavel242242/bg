# Datagen Feature Requests - Critical for Marketing Analytics Data Quality

**Submitted by:** Data Quality Analysis Team
**Date:** 2025-11-09
**Priority:** HIGH
**Impact:** Blocks production-ready data generation

---

## Executive Summary

During analysis of the Marketing Growth Analytics dataset, we identified **5 critical missing features** that prevent datagen from generating production-ready data without post-processing.

**Current situation:**
- Datagen generates 277,043 records across 22 tables
- **Quality score: 52/100** (unusable for production)
- **16,286 records (5.9%)** require post-processing fixes
- Post-processing adds complexity and breaks deterministic reproducibility

**With these features:**
- Datagen could generate **100/100 quality** data directly
- No post-processing needed
- Truly deterministic and reproducible

---

## Feature Request #1: Conditional Field Generation

### Problem
Fields that should only be populated when another field has a specific value are always generated independently.

### Impact
- **135/200 companies** (67.5%) have invalid data
- Non-customers (`is_customer=False`) have `signed_date` and `mrr_usd` populated
- Makes customer segmentation impossible
- Revenue analysis completely broken

### Current Workaround
Post-processing script to set NULL/0 values after generation

### Proposed Feature

```json
{
  "name": "signed_date",
  "type": "datetime",
  "nullable": true,
  "generator": {
    "conditional": {
      "if": "is_customer == true",
      "then": {
        "datetime_series": {
          "within": {"start": "2024-01-01", "end": "2024-12-31"},
          "freq": "D"
        }
      },
      "else": null
    }
  }
}
```

### Alternative Syntax (less preferred)

```json
{
  "name": "mrr_usd",
  "type": "int",
  "nullable": true,
  "generator": {
    "distribution": {
      "type": "lognormal",
      "params": {"mean": 7.5, "sigma": 1.5},
      "clamp": [100, 50000]
    }
  },
  "modifiers": [{
    "transform": "nullif",
    "args": {"condition": "is_customer == false"}
  }]
}
```

### Use Cases
1. **Customer data:** Only customers have MRR, signed dates, contract terms
2. **Email funnels:** Only opened emails can be clicked (see FR #4)
3. **Optional fields:** Fields that should be NULL based on other field values
4. **Status-dependent data:** Different data based on status/state fields

### Priority
**P0 - CRITICAL**

---

## Feature Request #2: Parent-Referenced Temporal Constraints

### Problem
Child records can have timestamps before their parent record was created.

### Impact
- **14,906 records** (43% of FK-related data) violate timeline logic
- Sessions before user registration: 7,412 violations
- Campaign mentions before campaign start: 1,289 violations
- Transactions before company signed: 495 violations
- Social engagement before posts: 4,694 violations
- Support tickets resolved before created: 1,406 violations

### Current Workaround
Post-processing script to adjust child timestamps after parent dates

### Proposed Feature

```json
{
  "id": "user_sessions",
  "kind": "fact",
  "parents": ["people"],
  "columns": [
    {
      "name": "timestamp",
      "type": "datetime",
      "generator": {
        "datetime_series": {
          "after": "people.first_seen_date",  // ← NEW: Reference parent timestamp
          "within": {"end": "2024-12-31T23:59:59Z"},
          "freq": "H"
        }
      }
    }
  ]
}
```

### Alternative Syntax

```json
{
  "name": "timestamp",
  "type": "datetime",
  "generator": {
    "datetime_series": {
      "within": {"start": "2024-01-01", "end": "2024-12-31"},
      "freq": "H"
    }
  },
  "constraints": {
    "after": "people.first_seen_date",  // Constraint enforced during generation
    "min_offset": "1H"  // Optional: minimum time after parent
  }
}
```

### Self-Referenced Version

For fields within the same table:

```json
{
  "name": "resolved_at",
  "type": "datetime",
  "nullable": true,
  "generator": {
    "datetime_series": {
      "after": "created_at",  // ← Self-reference to earlier column
      "add_duration": {
        "distribution": {
          "type": "lognormal",
          "params": {"mean": 4.0, "sigma": 2.0},
          "clamp": [3600, 604800]  // 1 hour to 7 days in seconds
        }
      }
    }
  }
}
```

### Use Cases
1. **User lifecycle:** Sessions/events after user registration
2. **Campaign attribution:** Mentions/conversions after campaign launch
3. **Business events:** Transactions after contract signed
4. **Content engagement:** Engagement after content published
5. **Support workflows:** Resolution after ticket creation
6. **Sequential events:** Any child event that must occur after parent

### Priority
**P0 - CRITICAL**

---

## Feature Request #3: Dependent Field Logic (Funnel Constraints)

### Problem
Boolean fields representing funnel stages are generated independently, creating impossible states.

### Impact
- **1,165 email/newsletter records** with impossible funnel states
- 16 emails clicked without being opened
- 1,149 newsletters clicked without being opened
- Funnel analysis completely invalid

### Current Workaround
Post-processing script to set `opened=True` when `clicked=True`

### Proposed Feature

```json
{
  "name": "opened",
  "type": "bool",
  "generator": {
    "choice": {
      "choices": [true, false],
      "weights": [0.35, 0.65]
    }
  }
},
{
  "name": "clicked",
  "type": "bool",
  "generator": {
    "conditional": {
      "if": "opened == true",
      "then": {
        "choice": {
          "choices": [true, false],
          "weights": [0.34, 0.66]  // 12% / 35% = 34% of opened emails
        }
      },
      "else": false
    }
  }
},
{
  "name": "converted",
  "type": "bool",
  "generator": {
    "conditional": {
      "if": "opened == true",
      "then": {
        "choice": {
          "choices": [true, false],
          "weights": [0.086, 0.914]  // 3% / 35% = 8.6% of opened emails
        }
      },
      "else": false
    }
  }
}
```

### Alternative: Constraints Block

```json
{
  "columns": [
    {"name": "opened", "type": "bool", ...},
    {"name": "clicked", "type": "bool", ...},
    {"name": "converted", "type": "bool", ...}
  ],
  "constraints": {
    "funnels": [
      {
        "stages": ["opened", "clicked", "converted"],
        "mode": "progressive"  // Each stage requires previous stage
      }
    ]
  }
}
```

### Use Cases
1. **Email marketing:** sent → opened → clicked → converted
2. **User onboarding:** signed_up → activated → engaged → retained
3. **Purchase funnels:** viewed → added_to_cart → checkout → purchased
4. **Content engagement:** viewed → liked → commented → shared
5. **Trial conversion:** started → activated → upgraded

### Priority
**P0 - CRITICAL**

---

## Feature Request #4: Uniqueness Constraint for choice Generator

### Problem
When using `choice` generator, values can repeat even when they should be unique.

### Impact
- **28/50 campaigns** (56%) have duplicate names
- "VS Code Extension" appears 4 times with different IDs/configs
- Joins become ambiguous
- Campaign analysis requires ID instead of human-readable names

### Current Workaround
Post-processing script to add version suffixes (e.g., "VS Code Extension v2")

### Proposed Feature

**Option A: unique flag on choice generator**

```json
{
  "name": "campaign_name",
  "type": "string",
  "generator": {
    "choice": {
      "choices": [...50 names...],
      "weights_kind": "uniform",
      "unique": true  // ← NEW: Each row gets unique value (no repeats)
    }
  }
}
```

**Option B: sequence_choice generator**

```json
{
  "name": "campaign_name",
  "type": "string",
  "generator": {
    "sequence_choice": {  // ← NEW generator type
      "choices": [...50 names...],
      "shuffle": true  // Optional: randomize order
    }
  }
}
```

**Option C: unique constraint (validates but doesn't enforce)**

```json
{
  "constraints": {
    "unique": ["campaigns.campaign_name"]
  }
}
```
> Note: This only validates uniqueness AFTER generation, doesn't prevent duplicates

### Use Cases
1. **Named entities:** Campaign names, product names, project names
2. **Codes/IDs:** Coupon codes, invite codes, reference numbers
3. **Limited resources:** Fixed set of options assigned once each
4. **Assignments:** Assign N people to N roles (one-to-one)

### Priority
**P1 - HIGH**

---

## Feature Request #5: Derived Field from Lookup

### Problem
When a table has multiple foreign keys, they're looked up independently, creating invalid combinations.

### Impact
- **1,524/1,534 transactions** (99.4%) have company_id that doesn't match person's company
- Person from Company A buying products for Company B
- Revenue attribution completely broken

### Current Status
**ACTUALLY SUPPORTED!** Using `lookup` with `on` parameter:

```json
{
  "name": "person_id",
  "type": "int",
  "generator": {
    "lookup": {"from": "people.person_id"}
  }
},
{
  "name": "company_id",
  "type": "int",
  "generator": {
    "lookup": {
      "from": "people.company_id",
      "on": {"person_id": "person_id"}  // Join on person_id
    }
  }
}
```

### Request
**Better documentation** and **examples** of this feature in:
- README.md
- datagen_spec.md
- Example schemas

This is a powerful feature that's hidden! Many users don't know it exists.

### Priority
**P2 - DOCUMENTATION** (feature exists, needs visibility)

---

## Feature Request #6: BONUS - Conditional Probability Distributions

### Problem
Distributions that should vary based on other fields are uniform across all records.

### Impact (Lower Priority)
- Company MRR doesn't scale with company_size
- Small companies (1-10 employees) have same MRR range as large enterprises
- Reduces data realism but doesn't break functionality

### Proposed Feature

```json
{
  "name": "mrr_usd",
  "type": "int",
  "generator": {
    "distribution": {
      "type": "lognormal",
      "params": {
        "mean": {
          "case": "company_size",  // ← NEW: Value depends on another field
          "values": {
            "1-10": 6.5,
            "11-50": 7.5,
            "51-200": 8.5,
            "201-500": 9.0,
            "501-1000": 9.5,
            "1000+": 10.0
          }
        },
        "sigma": 1.5
      },
      "clamp": [100, 50000]
    }
  }
}
```

### Use Cases
1. **Size-based metrics:** Revenue, employees, customers based on company size
2. **Tier-based pricing:** Different price ranges for free/pro/enterprise
3. **Geo-based variation:** Different distributions by country/region
4. **Segment-based behavior:** Different engagement patterns by user segment

### Priority
**P2 - ENHANCEMENT** (nice to have, not blocking)

---

## Summary Table

| FR # | Feature | Priority | Impact | Records Affected | Workaround |
|------|---------|----------|--------|------------------|------------|
| #1 | Conditional field generation | P0 | Customer segmentation broken | 135 (67.5%) | Post-processing |
| #2 | Parent-referenced timestamps | P0 | Timeline analysis invalid | 14,906 (43%) | Post-processing |
| #3 | Funnel constraints | P0 | Funnel analysis broken | 1,165 (9.5%) | Post-processing |
| #4 | Unique choice values | P1 | Name ambiguity | 28 (56%) | Post-processing |
| #5 | Derived field docs | P2 | Revenue attribution broken | 1,524 (99.4%) | **ALREADY SUPPORTED** |
| #6 | Conditional distributions | P2 | Reduces realism | All records | Accept limitation |

---

## Implementation Suggestions

### For FR #1 & #3 (Conditional Logic)

Could be unified under a single `conditional` generator:

```python
class ConditionalGenerator(BaseModel):
    """Conditional field generation based on other fields."""
    conditional: dict

    @field_validator("conditional")
    @classmethod
    def validate_conditional(cls, v):
        if "if" not in v:
            raise ValueError("conditional must have 'if' clause")
        if "then" not in v:
            raise ValueError("conditional must have 'then' clause")
        # 'else' is optional, defaults to null/false

        # Validate condition expression
        condition = v["if"]
        # Support simple comparisons: field == value, field != value, field > value, etc.

        return v
```

**Generation logic:**
1. Generate prerequisite field first (e.g., `is_customer`)
2. Evaluate condition for each row
3. Generate `then` branch for True rows, `else` for False rows
4. Combine results

### For FR #2 (Temporal Constraints)

Extend `datetime_series` generator:

```python
class DatetimeSeriesGenerator(BaseModel):
    """Datetime series with optional parent reference."""
    datetime_series: dict

    @field_validator("datetime_series")
    @classmethod
    def validate_datetime_series(cls, v):
        # Existing validation...

        # New: parent-referenced bounds
        if "after" in v:
            after_ref = v["after"]
            # Validate format: "table.column" or just "column" (self-ref)
            if not isinstance(after_ref, str):
                raise ValueError("after must be a string reference")

        return v
```

**Generation logic:**
1. For self-references: Generate earlier column first
2. For parent references: Access parent row data
3. Set `start` bound to referenced timestamp + optional offset
4. Generate timestamp within constrained range

---

## Expected Outcomes

**With FR #1, #2, #3 implemented:**
- Data quality: 52/100 → **95/100**
- Post-processing: Required → **Eliminated**
- Determinism: Broken by post-proc → **Fully deterministic**
- Usability: Demo only → **Production ready**

**With FR #4 implemented:**
- Data quality: 95/100 → **98/100**
- Name-based queries: Ambiguous → **Reliable**

**With FR #5 (docs) implemented:**
- Users discover existing powerful features
- Reduces support burden
- Better schema examples

**With FR #6 implemented:**
- Data quality: 98/100 → **100/100**
- Realism: Synthetic → **Highly realistic**

---

## Migration Path

**Phase 1 (MVP):** Implement FR #1, #2, #3
- Covers 80% of data quality issues
- Eliminates need for post-processing
- Estimated effort: 2-3 weeks

**Phase 2:** Implement FR #4
- Eliminates remaining uniqueness issues
- Estimated effort: 1 week

**Phase 3:** Improve FR #5 documentation
- Better examples and visibility
- Estimated effort: 1-2 days

**Phase 4 (Future):** Implement FR #6
- Advanced realism features
- Estimated effort: 2-3 weeks

---

## References

- **Analysis Report:** `MARKETING_DATA_QUALITY_SYNTHESIS.md`
- **Fix Recommendations:** `DATAGEN_FIX_RECOMMENDATIONS.md`
- **Coverage Analysis:** `DATAGEN_COVERAGE_AND_GAPS.md`
- **Improvement Report:** `DATA_QUALITY_IMPROVEMENT_REPORT.md`

---

## Contact

For questions or clarifications on these feature requests, please reference:
- GitHub Issue: [Link to be created]
- Analysis Repository: https://github.com/pavel242242/bg
- Branch: `claude/analyze-marketing-data-quality-011CUxA4mZwSr5JauPkfWgma`

---

**Generated:** 2025-11-09
**Dataset Analyzed:** Marketing Growth Analytics (277,043 records, 22 tables)
**Quality Gap:** 52/100 → 100/100 requires these features
**Business Impact:** Blocks production use of synthetic marketing data
