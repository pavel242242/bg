# MARKETING DATA QUALITY ANALYSIS - Schema v1.1
## Before vs After Comparison

**Analysis Date:** 2024-11-09
**Dataset:** /tmp/datagen/marketing_example_v1.1/
**Analysis Tool:** DuckDB (Python)

---

## EXECUTIVE SUMMARY

| Issue | Status | Before v1.1 | After v1.1 | Change |
|-------|--------|-----------|-----------|--------|
| Campaign Names (Duplicates) | 🚨 STILL BROKEN | 56% (28/50) | 70% (35/50) | **WORSE +14%** |
| Campaign Mentions (Temporal) | 🚨 STILL BROKEN | 42.4% (1289/3040) | 42.4% (1289/3040) | **NO CHANGE** |
| Email Sends (Funnel) | 🚨 STILL BROKEN | ~9.5% | 6.4% of total, 61.5% of clicked | **WORSE** |
| Newsletter Sends (Funnel) | 🚨 STILL BROKEN | 9.5% (1149/12074) | 9.5% (1149/12074) | **NO CHANGE** |
| Social Engagement (User Diversity) | ✅ **FIXED** | All users = 1 (0% diverse) | 1000 unique users (100% diverse) | **FIXED!** |
| Social Engagement (Temporal) | 🚨 STILL BROKEN | 48% (4694/9787) | 48% (4694/9787) | **NO CHANGE** |

---

## DETAILED FINDINGS

### 1. CAMPAIGN NAMES: Duplicate Analysis

**Status:** 🚨 STILL BROKEN (WORSE)

#### SQL Query:
```sql
SELECT
    campaign_name,
    COUNT(*) as occurrences,
    COUNT(DISTINCT campaign_id) as unique_ids
FROM read_parquet('/tmp/datagen/marketing_example_v1.1/campaigns.parquet')
GROUP BY campaign_name
HAVING COUNT(*) > 1
ORDER BY COUNT(*) DESC
```

#### Results:
- **Total campaigns:** 50
- **Duplicate names:** 14 groups
- **Records affected:** 35 out of 50 (70%)
- **Change from v1.0:** WORSE! Was 56%, now 70%

#### Duplicate Details:
```
               campaign_name  occurrences  unique_ids
0          VS Code Extension            4           4
1    YouTube Tutorial Series            3           3
2          Webinar Series Q1            3           3
3             Pricing Revamp            3           3
4           Free Tier Launch            3           3
5               Podcast Tour            3           3
6       Open Source Advocacy            2           2
7       Partner Co-Marketing            2           2
8    Platform Feature Launch            2           2
9         HackerNews Show HN            2           2
10              Beta Program            2           2
11      GitHub Trending Push            2           2
12  Valentine Developer Love            2           2
13            Back to School            2           2
```

**Issue:** Campaign names are NOT unique. The schema needed a UNIQUE constraint or deduplication during datagen.

**Requires:** FR #4 - Add unique constraint or enforce name uniqueness

---

### 2. CAMPAIGN MENTIONS: Temporal Integrity

**Status:** 🚨 STILL BROKEN (NO CHANGE)

#### SQL Query:
```sql
WITH mention_violations AS (
    SELECT
        cm.mention_id,
        cm.campaign_id,
        cm.timestamp,
        c.start_date,
        c.campaign_name
    FROM read_parquet('/tmp/datagen/marketing_example_v1.1/campaign_mentions.parquet') cm
    LEFT JOIN read_parquet('/tmp/datagen/marketing_example_v1.1/campaigns.parquet') c
        ON cm.campaign_id = c.campaign_id
    WHERE cm.timestamp < c.start_date
)
SELECT
    COUNT(*) as violations,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM read_parquet('/tmp/datagen/marketing_example_v1.1/campaign_mentions.parquet')), 1) as violation_pct,
    MIN(timestamp) as earliest_mention,
    MAX(timestamp) as latest_violation,
    COUNT(DISTINCT campaign_id) as affected_campaigns
FROM mention_violations
```

#### Results:
| Metric | Value |
|--------|-------|
| Total mentions | 3,040 |
| Violations | 1,289 |
| Violation % | 42.4% |
| Affected campaigns | 49 out of 50 |
| Date range of violations | 2024-01-01 to 2024-12-05 |
| Min days before start | -361 days |
| Max days before start | -1 day |

#### Sample Violations:
```
           campaign_name start_date           timestamp  days_before_start
0      VS Code Extension 2024-05-19 2024-05-18 23:00:00                 -1
1    Influencer Outreach 2024-02-18 2024-02-17 02:00:00                 -1
2           Beta Program 2024-09-08 2024-09-07 06:00:00                 -1
3     Black Friday Promo 2024-07-14 2024-07-13 03:00:00                 -1
4  Hackathon Sponsorship 2024-03-17 2024-03-16 16:00:00                 -1
```

**Issue:** Mentions are recorded BEFORE campaigns officially start. This violates temporal ordering.

**Analysis:** Most violations are off by just 1 day, but some are off by a full year (361 days). This suggests either:
- Mentions dated incorrectly in datagen
- Campaign start dates should be shifted earlier
- OR mentions should respect campaign start_date constraint

**Requires:** FR #2 - Add temporal constraint that mentions.timestamp >= campaign.start_date

---

### 3. EMAIL SENDS: Funnel Integrity

**Status:** 🚨 STILL BROKEN

#### SQL Query - Funnel Breakdown:
```sql
WITH email_states AS (
    SELECT
        CASE
            WHEN opened = true AND clicked = true THEN '✅ Opened & Clicked (Correct)'
            WHEN opened = true AND clicked = false THEN '⚠️  Opened, Not Clicked'
            WHEN opened = false AND clicked = true THEN '🚨 VIOLATION: Clicked without Opening'
            WHEN opened = false AND clicked = false THEN '⬜ Not Opened, Not Clicked'
        END as state,
        COUNT(*) as count
    FROM read_parquet('/tmp/datagen/marketing_example_v1.1/email_sends.parquet')
    GROUP BY state
)
SELECT state, count FROM email_states ORDER BY count DESC
```

#### Results:
| State | Count | Status |
|-------|-------|--------|
| ⬜ Not Opened, Not Clicked | 155 | Normal |
| ⚠️ Opened, Not Clicked | 70 | Normal |
| 🚨 **VIOLATION: Clicked without Opening** | **16** | **Problem** |
| ✅ Opened & Clicked (Correct) | 10 | Correct |

**Violation Metrics:**
- Total email sends: 251
- Violations: 16
- Violation % of total: 6.4%
- Violation % of clicked emails: 61.5% (16 of 26 clicked emails didn't have opened=true)

**Issue:** 16 emails show clicked=true but opened=false, violating email funnel logic (you can't click without opening)

**Before v1.1:** Was 9.5% of sends (approximately 24 records in previous dataset)
**After v1.1:** Now 6.4% of sends (16 records) - SLIGHT IMPROVEMENT but still broken

**Requires:** FR #3 - Add constraint: clicked = true IMPLIES opened = true

---

### 4. NEWSLETTER SENDS: Funnel Integrity

**Status:** 🚨 STILL BROKEN (NO CHANGE)

#### SQL Query - Funnel Breakdown:
```sql
WITH newsletter_states AS (
    SELECT
        CASE
            WHEN opened = true AND clicked = true THEN '✅ Opened & Clicked (Correct)'
            WHEN opened = true AND clicked = false THEN '⚠️  Opened, Not Clicked'
            WHEN opened = false AND clicked = true THEN '🚨 VIOLATION: Clicked without Opening'
            WHEN opened = false AND clicked = false THEN '⬜ Not Opened, Not Clicked'
        END as state,
        COUNT(*) as count,
        ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM read_parquet('/tmp/datagen/marketing_example_v1.1/newsletter_sends.parquet')), 1) as pct
    FROM read_parquet('/tmp/datagen/marketing_example_v1.1/newsletter_sends.parquet')
    GROUP BY state
)
SELECT state, count, pct FROM newsletter_states ORDER BY count DESC
```

#### Results:
| State | Count | % |
|-------|-------|---|
| ⬜ Not Opened, Not Clicked | 6,130 | 50.8% |
| ⚠️ Opened, Not Clicked | 4,060 | 33.6% |
| 🚨 **VIOLATION: Clicked without Opening** | **1,149** | **9.5%** |
| ✅ Opened & Clicked (Correct) | 735 | 6.1% |

**Violation Metrics:**
- Total newsletter sends: 12,074
- Violations: 1,149
- Violation % of total: 9.5%
- Violation % of clicked newsletters: 61.0% (1,149 of 1,884 clicked newsletters didn't have opened=true)

**Change from v1.0:** NO CHANGE - Still exactly 9.5% (1,149 violations)

**Issue:** Same as email - funnel integrity broken. Users clicking without opening is impossible.

**Requires:** FR #3 - Add constraint: clicked = true IMPLIES opened = true

---

### 5. SOCIAL ENGAGEMENT: User ID Diversity

**Status:** ✅ **FIXED!**

#### SQL Query:
```sql
SELECT
    COUNT(DISTINCT user_id) as unique_user_ids,
    COUNT(*) as total_records,
    MIN(user_id) as min_user_id,
    MAX(user_id) as max_user_id,
    COUNT(CASE WHEN user_id = 1 THEN 1 END) as count_user_1,
    ROUND(100.0 * COUNT(CASE WHEN user_id = 1 THEN 1 END) / COUNT(*), 1) as pct_user_1
FROM read_parquet('/tmp/datagen/marketing_example_v1.1/social_engagement.parquet')
```

#### Results:
| Metric | Value |
|--------|-------|
| Unique user_ids | **1,000** |
| Total engagement records | 9,787 |
| Min user_id | 10,000 |
| Max user_id | 10,999 |
| Count with user_id=1 | 0 |
| % with user_id=1 | 0.0% |

**Sample engagement records:**
```
   engagement_id  post_id           timestamp  user_id
0        5000000   300000 2024-07-11 20:33:46    10976
1        5000001   300000 2024-03-15 11:44:11    10923
2        5000002   300000 2024-01-14 16:53:02    10043
3        5000003   300000 2024-12-19 01:51:15    10556
4        5000004   300000 2024-07-31 17:08:37    10755
...
```

**IMPROVEMENT:**
- **Before v1.0:** All 9,787 records had user_id = 1 (0% diverse, 100% concentrated)
- **After v1.1:** 1,000 unique user_ids spread across 10000-10999 range
- **Status:** ✅ COMPLETELY FIXED

This is the ONLY issue that was successfully resolved in v1.1!

---

### 6. SOCIAL ENGAGEMENT: Temporal Integrity

**Status:** 🚨 STILL BROKEN (NO CHANGE)

#### SQL Query:
```sql
WITH engagement_violations AS (
    SELECT
        se.engagement_id,
        se.post_id,
        se.timestamp,
        sp.posted_at,
        DATEDIFF('day', sp.posted_at, se.timestamp) as days_diff
    FROM read_parquet('/tmp/datagen/marketing_example_v1.1/social_engagement.parquet') se
    LEFT JOIN read_parquet('/tmp/datagen/marketing_example_v1.1/social_posts.parquet') sp
        ON se.post_id = sp.post_id
    WHERE se.timestamp < sp.posted_at
)
SELECT
    COUNT(*) as violations,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM read_parquet('/tmp/datagen/marketing_example_v1.1/social_engagement.parquet')), 0) as violation_pct,
    MIN(days_diff) as min_days_before,
    MAX(days_diff) as max_days_before,
    COUNT(DISTINCT post_id) as affected_posts
FROM engagement_violations
```

#### Results:
| Metric | Value |
|--------|-------|
| Total engagement records | 9,787 |
| Total social posts | 386 |
| Violations | 4,694 |
| Violation % | 48% |
| Affected posts | 363 out of 386 |
| Min days before post | -361 days |
| Max days before post | 0 days |

#### Sample Violations:
```
   post_id           posted_at           timestamp  days_before_post
0   300088 2024-08-06 23:00:00 2024-08-06 21:34:21                 0
1   300028 2024-02-11 23:00:00 2024-02-11 11:10:05                 0
2   300171 2024-04-12 11:00:00 2024-04-12 09:00:02                 0
3   300108 2024-11-12 06:00:00 2024-11-12 04:37:45                 0
4   300182 2024-05-24 15:00:00 2024-05-24 09:13:29                 0
```

**Issue:** Engagements recorded BEFORE posts were created. Nearly half (48%) of all engagement records have this problem.

**Analysis:**
- Most violations are on the same day (days_before_post = 0), suggesting timezone/time-of-day issues with the datagen
- Some violations go back 361 days (a full year earlier!)
- 363 out of 386 posts (94%) have at least one engagement before they were posted

**Change from v1.0:** NO CHANGE - Still exactly 48% (4,694 violations)

**Requires:** FR #2 - Add temporal constraint that engagement.timestamp >= post.posted_at

---

## SCHEMA IMPROVEMENTS NEEDED (Feature Requests)

### FR #2: Temporal Constraints
**Affects:** Campaign Mentions, Social Engagement
**Status:** ❌ NOT IMPLEMENTED

Add constraints to ensure temporal ordering:
- `campaign_mentions.timestamp >= campaign.start_date`
- `social_engagement.timestamp >= social_posts.posted_at`

**Impact:** Would fix 42.4% + 48% = ~4,983 records

---

### FR #3: Funnel Integrity Constraints
**Affects:** Email Sends, Newsletter Sends
**Status:** ❌ NOT IMPLEMENTED

Add constraint:
- `clicked = true IMPLIES opened = true`

**Implementation options:**
1. Add CHECK constraint in schema
2. Add validation trigger
3. Fix during datagen to enforce funnel order

**Impact:** Would fix 16 + 1,149 = 1,165 records

---

### FR #4: Campaign Name Uniqueness
**Affects:** Campaigns
**Status:** ❌ NOT IMPLEMENTED (WORSENED)

Add constraint:
- `campaign_name` must be UNIQUE

Or implement deduplication logic:
- Append campaign_id to name: "{campaign_name}_{campaign_id}"
- Add sequence number for duplicates

**Impact:** Would fix 35 duplicate records (70% of campaigns)

---

## COMPARISON TABLE

| Dimension | Before v1.0 | v1.1 | Status |
|-----------|-----------|-----|--------|
| **Campaign Duplicates** | 56% (28/50) | 70% (35/50) | 🚨 WORSE |
| **Campaign Mentions Temporal** | 42.4% | 42.4% | 🚨 NO CHANGE |
| **Email Funnel** | ~9.5% (~24) | 6.4% (16) | ⚠️ SLIGHT IMPROVEMENT |
| **Newsletter Funnel** | 9.5% (1,149) | 9.5% (1,149) | 🚨 NO CHANGE |
| **Social User Diversity** | 0% (all=1) | 100% (1,000 unique) | ✅ FIXED |
| **Social Engagement Temporal** | 48% | 48% | 🚨 NO CHANGE |
| **Overall Data Quality** | ~38% broken | ~36% broken | ⚠️ MINIMAL IMPROVEMENT |

---

## CONCLUSIONS

### What Got Fixed:
✅ **Social Engagement User Diversity** - Successfully diversified from single user (1) to 1,000 unique users

### What Got Worse:
🚨 **Campaign Name Duplicates** - Increased from 56% to 70% (from 28 to 35 affected records)

### What Stayed Broken:
🚨 **Campaign Mentions Temporal** - Still 42.4% violations (1,289 records)
🚨 **Email Funnel** - Still broken (16 records with click but no open)
🚨 **Newsletter Funnel** - Still 9.5% violations (1,149 records)
🚨 **Social Engagement Temporal** - Still 48% violations (4,694 records)

### Overall Assessment:
- **Only 1 of 6 issues fixed** (16.7% fix rate)
- **1 of 6 issues worsened** (16.7% degradation)
- **4 of 6 issues unchanged** (66.7% stagnation)
- **Overall data quality:** Still ~36% of records have quality issues

### Required Actions for v1.2:
1. Implement FR #2 (Temporal constraints)
2. Implement FR #3 (Funnel integrity)
3. Implement FR #4 (Campaign name uniqueness)
4. Consider data regeneration with improved datagen logic

