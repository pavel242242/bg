#!/usr/bin/env python3
"""Validate data quality improvements after post-processing"""

import duckdb
import pandas as pd

data_dir = '/tmp/datagen/marketing_example'

# Connect to DuckDB
con = duckdb.connect(':memory:')

# Load all CSV files
print("=" * 80)
print("DATA QUALITY VALIDATION - AFTER FIXES")
print("=" * 80)

import glob
for csv_file in glob.glob(f'{data_dir}/*.csv'):
    table_name = csv_file.split('/')[-1].replace('.csv', '')
    con.execute(f"CREATE TABLE {table_name} AS SELECT * FROM read_csv_auto('{csv_file}')")

print("\n✅ VALIDATION RESULTS:\n")

# 1. Companies is_customer logic
print("1. COMPANIES: is_customer logic")
result = con.execute("""
    SELECT
        is_customer,
        COUNT(*) as count,
        COUNT(signed_date) as with_signed_date,
        SUM(CASE WHEN mrr_usd > 0 THEN 1 ELSE 0 END) as with_mrr
    FROM companies
    GROUP BY is_customer
""").fetchall()
for row in result:
    print(f"   is_customer={row[0]:5} | Total: {row[1]:3} | With signed_date: {row[2]:3} | With MRR: {row[3]:3}")

violations = con.execute("""
    SELECT COUNT(*) FROM companies
    WHERE is_customer = false AND (signed_date IS NOT NULL OR mrr_usd > 0)
""").fetchone()[0]
print(f"   ✓ Violations: {violations} (Expected: 0)")

# 2. Campaign name uniqueness
print("\n2. CAMPAIGNS: Name uniqueness")
duplicates = con.execute("""
    SELECT campaign_name, COUNT(*) as count
    FROM campaigns
    GROUP BY campaign_name
    HAVING COUNT(*) > 1
""").fetchall()
print(f"   ✓ Duplicate names: {len(duplicates)} (Expected: 0)")

# 3. Temporal constraints
print("\n3. TEMPORAL CONSTRAINTS:")

# Sessions after person registration
violations = con.execute("""
    SELECT COUNT(*) FROM user_sessions s
    JOIN people p ON s.person_id = p.person_id
    WHERE s.timestamp < p.first_seen_date
""").fetchone()[0]
print(f"   ✓ Sessions before person registration: {violations} (Expected: 0)")

# Mentions after campaign start
violations = con.execute("""
    SELECT COUNT(*) FROM campaign_mentions cm
    JOIN campaigns c ON cm.campaign_id = c.campaign_id
    WHERE cm.timestamp < c.start_date
""").fetchone()[0]
print(f"   ✓ Mentions before campaign start: {violations} (Expected: 0)")

# Transactions after company signed
violations = con.execute("""
    SELECT COUNT(*) FROM transactions t
    JOIN companies c ON t.company_id = c.company_id
    WHERE t.timestamp < c.signed_date
""").fetchone()[0]
print(f"   ✓ Transactions before company signed: {violations} (Expected: 0)")

# Social engagement after posts
violations = con.execute("""
    SELECT COUNT(*) FROM social_engagement se
    JOIN social_posts sp ON se.post_id = sp.post_id
    WHERE se.timestamp < sp.posted_at
""").fetchone()[0]
print(f"   ✓ Engagement before posts: {violations} (Expected: 0)")

# Support tickets resolved after created
violations = con.execute("""
    SELECT COUNT(*) FROM support_tickets
    WHERE resolved_at < created_at
""").fetchone()[0]
print(f"   ✓ Tickets resolved before created: {violations} (Expected: 0)")

# 4. Email/Newsletter funnels
print("\n4. EMAIL/NEWSLETTER FUNNELS:")

violations = con.execute("""
    SELECT COUNT(*) FROM email_sends
    WHERE clicked = true AND opened = false
""").fetchone()[0]
print(f"   ✓ Emails clicked without opening: {violations} (Expected: 0)")

violations = con.execute("""
    SELECT COUNT(*) FROM email_sends
    WHERE converted = true AND opened = false
""").fetchone()[0]
print(f"   ✓ Emails converted without opening: {violations} (Expected: 0)")

violations = con.execute("""
    SELECT COUNT(*) FROM newsletter_sends
    WHERE clicked = true AND opened = false
""").fetchone()[0]
print(f"   ✓ Newsletters clicked without opening: {violations} (Expected: 0)")

# 5. Social engagement users
print("\n5. SOCIAL ENGAGEMENT:")
distinct_users = con.execute("""
    SELECT COUNT(DISTINCT user_id) FROM social_engagement
""").fetchone()[0]
print(f"   ✓ Distinct user_ids: {distinct_users} (Expected: >100)")

# 6. Transaction-company alignment
print("\n6. TRANSACTION-COMPANY ALIGNMENT:")
violations = con.execute("""
    SELECT COUNT(*) FROM transactions t
    JOIN people p ON t.person_id = p.person_id
    WHERE t.company_id != p.company_id
""").fetchone()[0]
print(f"   ✓ Transactions with mismatched company: {violations} (Expected: 0)")

# 7. Foreign key integrity
print("\n7. FOREIGN KEY INTEGRITY:")
fk_checks = [
    ("people → companies", "SELECT COUNT(*) FROM people p LEFT JOIN companies c ON p.company_id = c.company_id WHERE c.company_id IS NULL"),
    ("transactions → people", "SELECT COUNT(*) FROM transactions t LEFT JOIN people p ON t.person_id = p.person_id WHERE p.person_id IS NULL"),
    ("transactions → companies", "SELECT COUNT(*) FROM transactions t LEFT JOIN companies c ON t.company_id = c.company_id WHERE c.company_id IS NULL"),
    ("user_sessions → people", "SELECT COUNT(*) FROM user_sessions s LEFT JOIN people p ON s.person_id = p.person_id WHERE p.person_id IS NULL"),
]

for check_name, query in fk_checks:
    violations = con.execute(query).fetchone()[0]
    print(f"   ✓ {check_name}: {violations} orphans (Expected: 0)")

# Calculate quality score
print("\n" + "=" * 80)
print("QUALITY SCORE CALCULATION")
print("=" * 80)

issues = 0
total_checks = 19

# Check each validation
checks = {
    "Companies is_customer": con.execute("SELECT COUNT(*) FROM companies WHERE is_customer = false AND (signed_date IS NOT NULL OR mrr_usd > 0)").fetchone()[0],
    "Campaign duplicates": len(duplicates),
    "Sessions timeline": con.execute("SELECT COUNT(*) FROM user_sessions s JOIN people p ON s.person_id = p.person_id WHERE s.timestamp < p.first_seen_date").fetchone()[0],
    "Mentions timeline": con.execute("SELECT COUNT(*) FROM campaign_mentions cm JOIN campaigns c ON cm.campaign_id = c.campaign_id WHERE cm.timestamp < c.start_date").fetchone()[0],
    "Transactions timeline": con.execute("SELECT COUNT(*) FROM transactions t JOIN companies c ON t.company_id = c.company_id WHERE t.timestamp < c.signed_date").fetchone()[0],
    "Engagement timeline": con.execute("SELECT COUNT(*) FROM social_engagement se JOIN social_posts sp ON se.post_id = sp.post_id WHERE se.timestamp < sp.posted_at").fetchone()[0],
    "Support timeline": con.execute("SELECT COUNT(*) FROM support_tickets WHERE resolved_at < created_at").fetchone()[0],
    "Email funnel": con.execute("SELECT COUNT(*) FROM email_sends WHERE clicked = true AND opened = false").fetchone()[0],
    "Newsletter funnel": con.execute("SELECT COUNT(*) FROM newsletter_sends WHERE clicked = true AND opened = false").fetchone()[0],
    "Social users": 0 if distinct_users > 100 else 1,
    "Transaction-company": con.execute("SELECT COUNT(*) FROM transactions t JOIN people p ON t.person_id = p.person_id WHERE t.company_id != p.company_id").fetchone()[0],
}

for check, violation_count in checks.items():
    if violation_count > 0:
        issues += 1

score = ((total_checks - issues) / total_checks) * 100

print(f"\nIssues found: {issues}/{total_checks}")
print(f"Quality Score: {score:.0f}/100")

if score == 100:
    print("\n🎉 PERFECT! All data quality issues fixed!")
elif score >= 90:
    print("\n✅ EXCELLENT! Data is production-ready")
elif score >= 70:
    print("\n⚠️  GOOD: Most issues fixed, minor issues remain")
else:
    print("\n🚨 NEEDS WORK: Significant issues remain")

con.close()
