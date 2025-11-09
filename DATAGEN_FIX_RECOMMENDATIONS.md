# Datagen Schema Fix Recommendations
**Schema:** marketing_growth_analytics.json
**Analysis Date:** 2025-11-09

---

## Executive Summary

5 parallel agents analyzed 277,043 records across 22 tables and found **8 critical data quality issues** affecting 21,478 records (7.7% direct, 43% cascade effect).

All issues traced to datagen schema configuration - specifically **lack of conditional logic and temporal constraints**.

**Current Score:** 52/100
**Target Score:** 95+/100
**Estimated Fix Time:** 12-16 hours

---

## 🔴 CRITICAL FIXES (P0 - Required for Production)

### 1. Companies: Add Conditional Logic for is_customer

**Location:** marketing_growth_analytics.json lines 301-346

**Problem:** All 3 fields generated independently
```json
"is_customer": { "weights": [0.3, 0.7] },  // Independent
"signed_date": { ... },  // Independent
"mrr_usd": { ... }  // Independent
```

**Impact:** 135/200 companies (67.5%) have is_customer=False but populated signed_date and MRR

**Fix Required:** Add conditional generation

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
          "within": {
            "start": "2024-01-01T00:00:00Z",
            "end": "2024-12-31T23:59:59Z"
          },
          "freq": "D"
        }
      },
      "else": null
    }
  }
},
{
  "name": "mrr_usd",
  "type": "int",
  "nullable": true,
  "generator": {
    "conditional": {
      "if": "is_customer == true",
      "then": {
        "distribution": {
          "clamp": [100, 50000],
          "type": "lognormal",
          "params": { "mean": 7.5, "sigma": 1.5 }
        }
      },
      "else": 0
    }
  }
}
```

**Alternative** (if conditionals not supported): Split into 2 tables or add post-generation cleanup

---

### 2. Campaign Names: Add Uniqueness Constraint

**Location:** marketing_growth_analytics.json lines 32-90

**Problem:** 50 campaigns choosing from 50 names without uniqueness = duplicates

**Impact:** 28/50 campaigns (56%) have duplicate names (e.g., "VS Code Extension" × 4)

**Fix Option A:** Add uniqueness (preferred)
```json
{
  "name": "campaign_name",
  "type": "string",
  "generator": {
    "choice": {
      "choices": [...],
      "weights_kind": "uniform",
      "unique": true  // ← ADD THIS
    }
  }
}
```

**Fix Option B:** Use sequential selection
```json
{
  "name": "campaign_name",
  "type": "string",
  "generator": {
    "sequence_choice": {
      "choices": [...],
      "shuffle": true
    }
  }
}
```

---

### 3. Add Temporal Constraints (Multi-Fix)

**Problem:** Child timestamps ignore parent creation dates

**Impact:** 15,631 records (43%) violate timeline logic

#### 3a. User Sessions After Person Registration

**Location:** lines 1273-1283

**Current:**
```json
"timestamp": {
  "generator": {
    "datetime_series": {
      "within": { "start": "2024-01-01", "end": "2024-12-31" }
    }
  }
}
```

**Fix:**
```json
"timestamp": {
  "generator": {
    "datetime_series": {
      "after": "people.first_seen_date",  // ← Reference parent date
      "within": { "end": "2024-12-31T23:59:59Z" },
      "freq": "H"
    }
  }
}
```

#### 3b. Campaign Mentions After Campaign Start

**Location:** lines 1582-1592

**Fix:**
```json
"timestamp": {
  "generator": {
    "datetime_series": {
      "after": "campaigns.start_date",  // ← Reference parent
      "within": { "end": "2024-12-31T23:59:59Z" },
      "freq": "H"
    }
  }
}
```

#### 3c. Transactions After Company Signed

**Location:** lines 2542-2552

**Fix:**
```json
"timestamp": {
  "generator": {
    "datetime_series": {
      "after": "companies.signed_date",  // ← Reference parent
      "within": { "end": "2024-12-31T23:59:59Z" },
      "freq": "D"
    }
  }
}
```

#### 3d. Social Engagement After Post

**Location:** lines 1924-1934

**Fix:**
```json
"timestamp": {
  "generator": {
    "datetime_series": {
      "after": "social_posts.posted_at",  // ← Reference parent
      "within": { "end": "2024-12-31T23:59:59Z" },
      "freq": "S"
    }
  }
}
```

#### 3e. Support Tickets: resolved_at After created_at

**Location:** lines 2410-2421

**Fix:**
```json
"resolved_at": {
  "type": "datetime",
  "nullable": true,
  "generator": {
    "datetime_series": {
      "after": "support_tickets.created_at",  // ← Self-reference
      "add_duration": {
        "distribution": {
          "type": "lognormal",
          "params": { "mean": 4.0, "sigma": 2.0 },
          "clamp": [3600, 604800]  // 1 hour to 7 days
        }
      }
    }
  }
}
```

---

### 4. Email/Newsletter: Add Funnel Logic

**Location:**
- email_sends: lines 1728-1772
- newsletter_sends: lines 2723-2752

**Problem:** opened/clicked/converted are independent booleans

**Impact:**
- Emails: 22/251 (8.8%) impossible states
- Newsletters: 1,149/12,074 (9.5%) impossible states

**Fix for email_sends:**
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
          "weights": [0.34, 0.66]  // 12% / 35% = 0.34
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
          "weights": [0.086, 0.914]  // 3% / 35% = 0.086
        }
      },
      "else": false
    }
  }
}
```

**Apply same pattern to newsletter_sends** (lines 2723-2752)

---

### 5. Social Engagement: Use Real User IDs

**Location:** lines 1961-1976

**Current:**
```json
"user_id": {
  "generator": {
    "distribution": {
      "type": "uniform",
      "params": { "min": 1, "max": 100000 }
    }
  }
}
```

**Problem:** Generates random IDs, not from people table

**Impact:** All 9,787 engagements have meaningless user_ids (actual result: all had user_id=1!)

**Fix:**
```json
"user_id": {
  "type": "int",
  "generator": {
    "lookup": {
      "from": "people.person_id",
      "allow_duplicates": true  // ← Users can engage multiple times
    }
  }
}
```

---

### 6. Transactions: Align Person-Company Relationship

**Location:** lines 2524-2539

**Problem:** company_id and person_id looked up independently

**Impact:** 99.35% of transactions have person from wrong company

**Current:**
```json
"company_id": {
  "generator": { "lookup": { "from": "companies.company_id" } }
},
"person_id": {
  "generator": { "lookup": { "from": "people.person_id" } }
}
```

**Fix:** Remove company_id as direct parent, derive from person
```json
"person_id": {
  "type": "int",
  "generator": {
    "lookup": { "from": "people.person_id" }
  }
},
"company_id": {
  "type": "int",
  "generator": {
    "derived": {
      "from": "person_id",
      "lookup": "people.company_id"  // ← Get company from selected person
    }
  }
}
```

**Alternative:** Update parents declaration
```json
"parents": ["people"],  // Remove "companies"
```

---

## 🟡 IMPORTANT FIXES (P1 - Improves Usability)

### 7. Add product_id to Transactions

**Location:** lines 2501-2654

**Current:** transactions table has no product reference

**Impact:** Cannot analyze revenue by product

**Add:**
```json
{
  "name": "product_id",
  "type": "int",
  "nullable": true,
  "generator": {
    "lookup": {
      "from": "products.product_id",
      "probability": 0.8  // 80% of transactions tied to product
    }
  }
}
```

Update constraints:
```json
"fks": [
  { "column": "product_id", "references": "products.product_id" }
]
```

---

### 8. Clarify Source-Channel Relationship

**Location:**
- campaigns.channel: lines 113-133
- user_sessions.source: lines 1329-1350

**Issue:** These seem related but generated independently

**Options:**

**A. Make them independent (current):** Document this is intentional
- session.source = user's entry point
- campaign.channel = campaign's primary distribution

**B. Make them aligned:** Add correlation
```json
// In user_sessions
"source": {
  "generator": {
    "conditional": {
      "if": "campaign_id != null",
      "then": {
        "derived": {
          "from": "campaign_id",
          "lookup": "campaigns.channel",
          "map": {
            "organic_search": "organic",
            "twitter": "social",
            "linkedin": "social",
            "email": "email",
            "direct": "direct"
          }
        }
      },
      "else": {
        "choice": {
          "choices": ["organic", "direct", "referral"],
          "weights": [0.5, 0.3, 0.2]
        }
      }
    }
  }
}
```

---

## 🟢 NICE TO HAVE (P2)

### 9. Add MRR-to-CompanySize Correlation

**Location:** lines 331-346

Current MRR doesn't scale with company_size. Add weighting:

```json
"mrr_usd": {
  "generator": {
    "conditional": {
      "if": "is_customer == true",
      "then": {
        "distribution": {
          "type": "lognormal",
          "params": {
            "mean": {
              "case": "company_size",
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
      },
      "else": 0
    }
  }
}
```

---

## 📋 IMPLEMENTATION CHECKLIST

**Priority 0 (Must fix):**
- [ ] 1. Add is_customer conditional logic for signed_date & mrr_usd
- [ ] 2. Add campaign_name uniqueness constraint
- [ ] 3a. user_sessions.timestamp after people.first_seen_date
- [ ] 3b. campaign_mentions.timestamp after campaigns.start_date
- [ ] 3c. transactions.timestamp after companies.signed_date
- [ ] 3d. social_engagement.timestamp after social_posts.posted_at
- [ ] 3e. support_tickets.resolved_at after created_at
- [ ] 4. Add email/newsletter funnel logic (opened → clicked → converted)
- [ ] 5. Fix social_engagement.user_id to lookup from people
- [ ] 6. Align transaction person-company relationship

**Priority 1 (Should fix):**
- [ ] 7. Add product_id to transactions table
- [ ] 8. Decide on source-channel relationship and implement

**Priority 2 (Nice to have):**
- [ ] 9. Add MRR correlation with company_size

---

## 🎯 VALIDATION QUERIES

After regenerating data, run these queries to verify fixes:

```sql
-- 1. Check companies logic
SELECT is_customer,
       COUNT(*) as count,
       COUNT(signed_date) as with_signed_date,
       COUNT(mrr_usd) as with_mrr
FROM companies
GROUP BY is_customer;
-- Expected: is_customer=false should have 0 signed_date and 0 mrr

-- 2. Check campaign name uniqueness
SELECT campaign_name, COUNT(*) as count
FROM campaigns
GROUP BY campaign_name
HAVING COUNT(*) > 1;
-- Expected: 0 rows

-- 3. Check temporal: sessions after person registration
SELECT COUNT(*) as violations
FROM user_sessions s
JOIN people p ON s.person_id = p.person_id
WHERE s.timestamp < p.first_seen_date;
-- Expected: 0

-- 4. Check temporal: mentions after campaign start
SELECT COUNT(*) as violations
FROM campaign_mentions cm
JOIN campaigns c ON cm.campaign_id = c.campaign_id
WHERE cm.timestamp < c.start_date;
-- Expected: 0

-- 5. Check email funnel logic
SELECT clicked, opened, COUNT(*) as count
FROM email_sends
GROUP BY clicked, opened;
-- Expected: No rows where clicked=true AND opened=false

-- 6. Check social engagement user_ids
SELECT COUNT(DISTINCT user_id) as distinct_users
FROM social_engagement;
-- Expected: > 100 (not just 1!)

-- 7. Check transaction person-company alignment
SELECT COUNT(*) as violations
FROM transactions t
JOIN people p ON t.person_id = p.person_id
WHERE t.company_id != p.company_id;
-- Expected: 0
```

---

## 📊 EXPECTED OUTCOMES

**After implementing P0 fixes:**
- Data Quality Score: 52 → 90+
- Production Ready: No → Yes
- Usable for revenue analysis: No → Yes
- Usable for attribution: No → Yes
- Usable for cohort analysis: No → Yes

**Time estimates:**
- P0 fixes: 12 hours
- P1 fixes: 4 hours
- Testing & validation: 2 hours
- **Total: 18 hours**

---

## 🤔 DESIGN QUESTIONS FOR CP

Before implementing fixes 7-8, please clarify:

1. **Product-Transaction link:** Should we add product_id to transactions? Or is revenue tracking at company level sufficient?

2. **Source-Channel semantics:** Should session.source match campaign.channel? Or are they independent dimensions?

3. **MRR calculation:** Should MRR correlate with company_size? Or is current distribution intentional?

---

## 📁 SUPPORTING DOCUMENTS

All detailed analysis reports in `/home/user/bg/`:
- `MARKETING_DATA_QUALITY_SYNTHESIS.md` - Comprehensive findings
- `DATA_QUALITY_FINDINGS_TREE.txt` - Visual decision tree
- `DATAGEN_FIX_RECOMMENDATIONS.md` - This document

Original data: `/tmp/datagen/marketing_example/`
Schema: `/tmp/datagen/schemas/marketing_growth_analytics.json`

---

**Generated by:** 5-agent parallel data quality analysis
**Confidence:** High (multi-agent cross-validation)
**Next step:** Review with CP, then implement P0 fixes
