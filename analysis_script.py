#!/usr/bin/env python3
"""
Comprehensive Product Engagement & User Behavior Analysis using DuckDB
Analyzes marketing data including sessions, events, campaigns, and conversions
"""

import duckdb
import json
import pandas as pd
from pathlib import Path
from datetime import datetime

# Data directory
DATA_DIR = Path('/home/user/bg/datagen/marketing_example')
OUTPUT_DIR = Path('/home/user/bg/analysis')
OUTPUT_DIR.mkdir(exist_ok=True)

# Initialize DuckDB connection
conn = duckdb.connect(':memory:')

print("=" * 80)
print("LOADING DATA INTO DUCKDB")
print("=" * 80)

# Load all CSV files
tables_to_load = [
    'user_sessions', 'session_events', 'newsletter_sends', 'transactions',
    'campaigns', 'product_events', 'people', 'companies', 'email_sends'
]

for table in tables_to_load:
    csv_path = DATA_DIR / f'{table}.csv'
    if csv_path.exists():
        conn.execute(f"CREATE TABLE {table} AS SELECT * FROM read_csv_auto('{csv_path}')")
        result = conn.execute(f"SELECT COUNT(*) as count FROM {table}")
        count = result.fetchall()[0][0]
        print(f"✓ {table}: {count:,} rows")

print("\n" + "=" * 80)
print("1. USER SESSION PATTERNS & OVERVIEW")
print("=" * 80)

# Basic session metrics
session_overview = conn.execute("""
SELECT
    COUNT(*) as total_sessions,
    COUNT(DISTINCT person_id) as unique_users,
    AVG(duration_seconds) as avg_duration_seconds,
    MIN(duration_seconds) as min_duration_seconds,
    MAX(duration_seconds) as max_duration_seconds,
    MEDIAN(duration_seconds) as median_duration_seconds,
    STDDEV_POP(duration_seconds) as stddev_duration_seconds,
    AVG(page_views) as avg_page_views,
    MIN(page_views) as min_page_views,
    MAX(page_views) as max_page_views,
    DATE_TRUNC('year', timestamp) as year
FROM user_sessions
GROUP BY year
ORDER BY year
""").fetchall()

for row in session_overview:
    print(f"\n{row[-1]}:")
    print(f"  Total Sessions: {row[0]:,}")
    print(f"  Unique Users: {row[1]:,}")
    print(f"  Avg Duration: {row[2]:.1f}s")
    print(f"  Duration Range: {row[3]:.0f}s - {row[4]:.0f}s (median: {row[5]:.0f}s, stddev: {row[6]:.0f}s)")
    print(f"  Avg Page Views: {row[7]:.2f}")
    print(f"  Page Views Range: {row[8]:.0f} - {row[9]:.0f}")

print("\n" + "=" * 80)
print("2. SESSION QUALITY METRICS BY DEVICE & GEOGRAPHY")
print("=" * 80)

# Device performance
device_metrics = conn.execute("""
SELECT
    device,
    COUNT(*) as sessions,
    COUNT(DISTINCT person_id) as unique_users,
    ROUND(AVG(duration_seconds), 2) as avg_duration_seconds,
    ROUND(AVG(page_views), 2) as avg_page_views,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as pct_of_total
FROM user_sessions
GROUP BY device
ORDER BY sessions DESC
""").fetchall()

print("\nBy Device:")
for device, sessions, users, duration, page_views, pct in device_metrics:
    print(f"  {device}: {sessions:,} sessions ({pct}%) | Users: {users:,} | Avg Duration: {duration}s | Avg Pages: {page_views}")

# Geographic performance
geo_metrics = conn.execute("""
SELECT
    country,
    COUNT(*) as sessions,
    COUNT(DISTINCT person_id) as unique_users,
    ROUND(AVG(duration_seconds), 2) as avg_duration_seconds,
    ROUND(AVG(page_views), 2) as avg_page_views,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as pct_of_total
FROM user_sessions
GROUP BY country
ORDER BY sessions DESC
LIMIT 15
""").fetchall()

print("\nTop 15 Countries:")
for country, sessions, users, duration, page_views, pct in geo_metrics:
    print(f"  {country}: {sessions:,} sessions ({pct}%) | Users: {users:,} | Avg Duration: {duration}s | Avg Pages: {page_views}")

print("\n" + "=" * 80)
print("3. TRAFFIC SOURCE EFFECTIVENESS ANALYSIS")
print("=" * 80)

# Source effectiveness
source_metrics = conn.execute("""
SELECT
    source,
    COUNT(*) as sessions,
    COUNT(DISTINCT person_id) as unique_users,
    ROUND(AVG(duration_seconds), 2) as avg_duration_seconds,
    ROUND(AVG(page_views), 2) as avg_page_views,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as pct_of_sessions,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(DISTINCT person_id)) OVER (), 2) as pct_of_users
FROM user_sessions
GROUP BY source
ORDER BY sessions DESC
""").fetchall()

print("\nTraffic Source Metrics:")
for source, sessions, users, duration, page_views, pct_sessions, pct_users in source_metrics:
    print(f"  {source}:")
    print(f"    Sessions: {sessions:,} ({pct_sessions}%)")
    print(f"    Users: {users:,} ({pct_users}%)")
    print(f"    Quality: {duration}s avg duration, {page_views} avg pages")

print("\n" + "=" * 80)
print("4. CAMPAIGN PERFORMANCE & USER JOURNEY")
print("=" * 80)

# Top campaigns by session volume
top_campaigns = conn.execute("""
SELECT
    us.campaign_id,
    c.campaign_name,
    c.channel,
    COUNT(*) as sessions,
    COUNT(DISTINCT us.person_id) as unique_users,
    ROUND(AVG(us.duration_seconds), 2) as avg_duration,
    ROUND(AVG(us.page_views), 2) as avg_page_views,
    ROUND(c.budget_usd, 2) as budget
FROM user_sessions us
LEFT JOIN campaigns c ON us.campaign_id = c.campaign_id
GROUP BY us.campaign_id, c.campaign_name, c.channel, c.budget_usd
ORDER BY sessions DESC
LIMIT 20
""").fetchall()

print("\nTop 20 Campaigns by Session Volume:")
for campaign_id, name, channel, sessions, users, duration, page_views, budget in top_campaigns:
    if name:
        print(f"  {name} (ID: {campaign_id})")
        print(f"    Channel: {channel}")
        print(f"    Sessions: {sessions:,} | Users: {users:,}")
        print(f"    Avg Duration: {duration}s | Avg Pages: {page_views}")
        print(f"    Budget: ${budget:,.0f}")

print("\n" + "=" * 80)
print("5. SESSION EVENTS & BEHAVIOR PATTERNS")
print("=" * 80)

# Event types distribution
event_analysis = conn.execute("""
SELECT
    event_type,
    COUNT(*) as event_count,
    COUNT(DISTINCT session_id) as sessions_with_event,
    COUNT(DISTINCT DATE(timestamp)) as days_with_events,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) as pct_of_events
FROM session_events
GROUP BY event_type
ORDER BY event_count DESC
""").fetchall()

print("\nEvent Type Distribution (179K events):")
for event_type, count, sessions, days, pct in event_analysis:
    print(f"  {event_type}: {count:,} events ({pct}%) in {sessions:,} sessions across {days} days")

# Page engagement
page_analysis = conn.execute("""
SELECT
    page_url,
    COUNT(*) as events,
    COUNT(DISTINCT session_id) as sessions,
    COUNT(DISTINCT DATE(timestamp)) as days
FROM session_events
GROUP BY page_url
ORDER BY events DESC
LIMIT 10
""").fetchall()

print("\nMost Engaged Pages:")
for page, events, sessions, days in page_analysis:
    print(f"  {page}: {events:,} events in {sessions:,} sessions")

# CTA and button engagement
cta_analysis = conn.execute("""
SELECT
    element_id,
    event_type,
    COUNT(*) as interactions,
    COUNT(DISTINCT session_id) as sessions
FROM session_events
WHERE element_id IN ('cta_button', 'sidebar', 'header')
GROUP BY element_id, event_type
ORDER BY interactions DESC
LIMIT 10
""").fetchall()

print("\nCTA & Button Engagement:")
for element, event_type, interactions, sessions in cta_analysis:
    print(f"  {element} ({event_type}): {interactions:,} interactions in {sessions:,} sessions")

print("\n" + "=" * 80)
print("6. CONVERSION FUNNEL ANALYSIS")
print("=" * 80)

# Transactions overview
trans_analysis = conn.execute("""
SELECT
    COUNT(*) as total_transactions,
    COUNT(DISTINCT company_id) as companies_converted,
    COUNT(DISTINCT person_id) as people_converted,
    ROUND(SUM(amount_usd), 2) as total_revenue_usd,
    ROUND(AVG(amount_usd), 2) as avg_transaction_usd,
    transaction_type,
    DATE_TRUNC('month', timestamp) as month
FROM transactions
GROUP BY transaction_type, month
ORDER BY month DESC, transaction_type
""").fetchall()

print("\nTransactions by Type (Monthly):")
trans_by_type = {}
for total, companies, people, revenue, avg_amount, trans_type, month in trans_analysis:
    if month not in trans_by_type:
        trans_by_type[month] = {}
    trans_by_type[month][trans_type] = {
        'count': total,
        'companies': companies,
        'people': people,
        'revenue': revenue,
        'avg': avg_amount
    }

for month in sorted(trans_by_type.keys(), reverse=True)[:6]:
    print(f"\n  {month}:")
    for trans_type, data in trans_by_type[month].items():
        print(f"    {trans_type}:")
        print(f"      Transactions: {data['count']:,}")
        print(f"      Companies: {data['companies']:,}")
        print(f"      People: {data['people']:,}")
        print(f"      Revenue: ${data['revenue']:,.2f}")

# Conversion funnel: Sessions -> Events -> Transactions
funnel = conn.execute("""
WITH funnel_data AS (
    SELECT
        'Sessions' as funnel_stage,
        COUNT(DISTINCT session_id) as count,
        1 as sort_order
    FROM user_sessions
    UNION ALL
    SELECT
        'With Events' as funnel_stage,
        COUNT(DISTINCT session_id) as count,
        2 as sort_order
    FROM session_events
    UNION ALL
    SELECT
        'With Conversions' as funnel_stage,
        COUNT(DISTINCT person_id) as count,
        3 as sort_order
    FROM transactions
)
SELECT funnel_stage, count FROM funnel_data ORDER BY sort_order
""").fetchall()

print("\n\nConversion Funnel:")
total_sessions = funnel[0][1]
for stage, count in funnel:
    pct = (count / total_sessions * 100) if stage == 'Sessions' else (count / total_sessions * 100)
    print(f"  {stage}: {count:,} ({pct:.2f}% of sessions)")

# Session -> Transaction conversion
session_conversion = conn.execute("""
SELECT
    us.source,
    COUNT(DISTINCT us.session_id) as sessions,
    COUNT(DISTINCT t.person_id) as converting_users,
    COUNT(DISTINCT t.transaction_id) as transactions,
    ROUND(100.0 * COUNT(DISTINCT t.person_id) / COUNT(DISTINCT us.person_id), 2) as user_conversion_pct,
    ROUND(SUM(t.amount_usd), 2) as revenue
FROM user_sessions us
LEFT JOIN transactions t ON us.person_id = t.person_id
    AND t.timestamp >= us.timestamp
    AND t.timestamp < us.timestamp + INTERVAL 30 DAY
GROUP BY us.source
ORDER BY transactions DESC NULLS LAST
""").fetchall()

print("\nSession -> Transaction Conversion by Source:")
for source, sessions, conv_users, trans, conv_pct, revenue in session_conversion:
    if trans and trans > 0:
        print(f"  {source}:")
        print(f"    Sessions: {sessions:,}")
        print(f"    Converted Users: {conv_users:,} ({conv_pct}%)")
        print(f"    Transactions: {trans:,}")
        print(f"    Revenue: ${revenue:,.2f}")

print("\n" + "=" * 80)
print("7. NEWSLETTER ENGAGEMENT ANALYSIS")
print("=" * 80)

# Newsletter metrics
newsletter_metrics = conn.execute("""
SELECT
    newsletter_type,
    COUNT(*) as sends,
    ROUND(100.0 * SUM(CASE WHEN opened THEN 1 ELSE 0 END) / COUNT(*), 2) as open_rate_pct,
    ROUND(100.0 * SUM(CASE WHEN clicked THEN 1 ELSE 0 END) / COUNT(*), 2) as click_rate_pct,
    SUM(CASE WHEN opened THEN 1 ELSE 0 END) as opened,
    SUM(CASE WHEN clicked THEN 1 ELSE 0 END) as clicked,
    COUNT(DISTINCT person_id) as unique_recipients
FROM newsletter_sends
GROUP BY newsletter_type
ORDER BY sends DESC
""").fetchall()

print("\nNewsletter Engagement Metrics (12K sends):")
for newsletter_type, sends, open_rate, click_rate, opened, clicked, recipients in newsletter_metrics:
    print(f"  {newsletter_type}:")
    print(f"    Sends: {sends:,} to {recipients:,} unique recipients")
    print(f"    Open Rate: {open_rate}%")
    print(f"    Click Rate: {click_rate}%")
    print(f"    Opened: {opened:,} | Clicked: {clicked:,}")

# Newsletter effectiveness by source
print("\nNewsletter Recipients by Source:")
newsletter_source = conn.execute("""
SELECT
    p.source_type,
    COUNT(DISTINCT ns.person_id) as recipients,
    COUNT(*) as sends,
    ROUND(100.0 * SUM(CASE WHEN ns.opened THEN 1 ELSE 0 END) / COUNT(*), 2) as open_rate_pct,
    ROUND(100.0 * SUM(CASE WHEN ns.clicked THEN 1 ELSE 0 END) / COUNT(*), 2) as click_rate_pct
FROM newsletter_sends ns
JOIN people p ON ns.person_id = p.person_id
GROUP BY p.source_type
ORDER BY sends DESC
""").fetchall()

for source_type, recipients, sends, open_rate, click_rate in newsletter_source:
    print(f"  {source_type}: {recipients:,} recipients ({sends:,} sends) - Open: {open_rate}%, Click: {click_rate}%")

print("\n" + "=" * 80)
print("8. USER SEGMENT BEHAVIOR ANALYSIS")
print("=" * 80)

# Segment by device and source combo
segment_analysis = conn.execute("""
SELECT
    device,
    source,
    COUNT(DISTINCT person_id) as users,
    COUNT(*) as sessions,
    ROUND(AVG(duration_seconds), 1) as avg_duration,
    ROUND(AVG(page_views), 2) as avg_pages,
    COUNT(DISTINCT campaign_id) as campaigns_reached
FROM user_sessions
GROUP BY device, source
ORDER BY sessions DESC
LIMIT 15
""").fetchall()

print("\nTop 15 User Segments (Device x Source):")
for device, source, users, sessions, duration, pages, campaigns in segment_analysis:
    print(f"  {device} + {source}:")
    print(f"    Users: {users:,} | Sessions: {sessions:,} | Campaigns: {campaigns}")
    print(f"    Engagement: {duration}s avg duration, {pages} avg pages")

print("\n" + "=" * 80)
print("9. TRAFFIC QUALITY SCORING BY SOURCE & CAMPAIGN")
print("=" * 80)

# Quality score: weighted combination of engagement metrics
quality_analysis = conn.execute("""
WITH source_quality AS (
    SELECT
        us.source as traffic_source,
        c.channel as campaign_channel,
        COUNT(DISTINCT us.session_id) as sessions,
        COUNT(DISTINCT us.person_id) as users,
        ROUND(AVG(us.duration_seconds), 1) as avg_duration,
        ROUND(AVG(us.page_views), 2) as avg_pages,
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY us.source), 2) as pct_of_source,
        AVG(us.duration_seconds) as raw_duration,
        AVG(us.page_views) as raw_pages,
        COUNT(DISTINCT EXTRACT(MONTH FROM us.timestamp)) as distinct_months
    FROM user_sessions us
    LEFT JOIN campaigns c ON us.campaign_id = c.campaign_id
    GROUP BY us.source, c.channel
)
SELECT
    traffic_source,
    campaign_channel,
    sessions,
    users,
    avg_duration,
    avg_pages,
    pct_of_source,
    ROUND(
        LEAST(raw_duration / 3000.0 * 100, 100) * 0.4 +
        LEAST(raw_pages / 10.0 * 100, 100) * 0.3 +
        LEAST(distinct_months / 12.0 * 100, 100) * 0.3,
        1
    ) as quality_score
FROM source_quality
ORDER BY quality_score DESC NULLS LAST
LIMIT 20
""").fetchall()

print("\nTraffic Quality Scores (Duration + Page Views + Monthly Reach):")
for source, channel, sessions, users, duration, pages, pct_source, quality in quality_analysis:
    channel_str = channel if channel else "N/A"
    print(f"  {source} (channel: {channel_str}):")
    print(f"    Sessions: {sessions:,} | Users: {users:,} | {pct_source}% of {source} traffic")
    print(f"    Quality Score: {quality:.1f}/100 | Duration: {duration}s, Pages: {pages}")

print("\n" + "=" * 80)
print("10. HIGH-ENGAGEMENT NON-CONVERTING SEGMENTS (FUNNEL LEAKS)")
print("=" * 80)

# High engagement sessions without conversion
high_engagement_no_conversion = conn.execute("""
WITH engaged_sessions AS (
    SELECT
        us.session_id,
        us.person_id,
        us.source,
        us.device,
        us.duration_seconds,
        us.page_views,
        COUNT(DISTINCT se.event_type) as event_types,
        COUNT(se.event_id) as event_count
    FROM user_sessions us
    LEFT JOIN session_events se ON us.session_id = se.session_id
    GROUP BY us.session_id, us.person_id, us.source, us.device, us.duration_seconds, us.page_views
)
SELECT
    source,
    device,
    COUNT(DISTINCT person_id) as high_engagement_users,
    COUNT(*) as high_engagement_sessions,
    ROUND(AVG(duration_seconds), 1) as avg_duration,
    ROUND(AVG(page_views), 2) as avg_pages,
    ROUND(AVG(event_count), 1) as avg_events,
    COUNT(DISTINCT person_id) as no_conversion
FROM engaged_sessions
WHERE
    duration_seconds > 300  -- More than 5 minutes
    AND page_views >= 3  -- At least 3 pages
    AND person_id NOT IN (SELECT DISTINCT person_id FROM transactions)
GROUP BY source, device
ORDER BY no_conversion DESC
LIMIT 15
""").fetchall()

print("\nHigh-Engagement Users NOT Converting (5+ min sessions, 3+ pages):")
for source, device, users, sessions, duration, pages, events, no_conv in high_engagement_no_conversion:
    print(f"  {device} + {source}: {users:,} users, {sessions:,} sessions")
    print(f"    Engagement: {duration}s, {pages} pages, {events} events avg")
    print(f"    OPPORTUNITY: {no_conv:,} users with high engagement but no conversion!")

print("\n" + "=" * 80)
print("11. EVENT PATTERNS PREDICTING CONVERSION")
print("=" * 80)

# Which event patterns are associated with conversion?
conversion_event_patterns = conn.execute("""
SELECT
    se.event_type,
    COUNT(DISTINCT CASE WHEN t.person_id IS NOT NULL THEN se.session_id END) as sessions_with_conversion,
    COUNT(DISTINCT se.session_id) as total_sessions,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN t.person_id IS NOT NULL THEN se.session_id END) /
          COUNT(DISTINCT se.session_id), 2) as conversion_rate_pct,
    COUNT(DISTINCT CASE WHEN t.person_id IS NOT NULL THEN t.amount_usd END) as converting_transactions,
    ROUND(AVG(CASE WHEN t.person_id IS NOT NULL THEN t.amount_usd END), 2) as avg_trans_value
FROM session_events se
LEFT JOIN user_sessions us ON se.session_id = us.session_id
LEFT JOIN transactions t ON us.person_id = t.person_id
    AND t.timestamp >= us.timestamp
    AND t.timestamp < us.timestamp + INTERVAL 30 DAY
GROUP BY se.event_type
ORDER BY conversion_rate_pct DESC NULLS LAST
""").fetchall()

print("\nEvent Types & Conversion Association:")
for event_type, conv_sessions, total_sessions, conv_rate, trans, avg_value in conversion_event_patterns:
    print(f"  {event_type}:")
    print(f"    Sessions: {total_sessions:,} | Converting: {conv_sessions:,} | Rate: {conv_rate}%")
    if trans and trans > 0:
        print(f"    Avg Transaction Value: ${avg_value:,.2f}")

print("\n" + "=" * 80)
print("12. DEVICE & GEOGRAPHY IMPACT ON CONVERSION")
print("=" * 80)

# Conversion by device and geography
device_geo_conversion = conn.execute("""
SELECT
    us.device,
    us.country,
    COUNT(DISTINCT us.session_id) as sessions,
    COUNT(DISTINCT us.person_id) as users,
    COUNT(DISTINCT t.person_id) as converted_users,
    ROUND(100.0 * COUNT(DISTINCT t.person_id) / COUNT(DISTINCT us.person_id), 2) as conversion_pct,
    COUNT(DISTINCT t.transaction_id) as transactions,
    ROUND(SUM(t.amount_usd), 2) as revenue
FROM user_sessions us
LEFT JOIN transactions t ON us.person_id = t.person_id
    AND t.timestamp >= us.timestamp
    AND t.timestamp < us.timestamp + INTERVAL 30 DAY
GROUP BY us.device, us.country
HAVING COUNT(DISTINCT us.session_id) >= 10  -- Minimum session threshold
ORDER BY conversion_pct DESC NULLS LAST
LIMIT 20
""").fetchall()

print("\nDevice x Country Conversion Performance (min 10 sessions):")
for device, country, sessions, users, conv_users, conv_pct, trans, revenue in device_geo_conversion:
    if conv_users and conv_users > 0:
        print(f"  {device} in {country}:")
        print(f"    Sessions: {sessions:,} | Users: {users:,} | Converted: {conv_users} ({conv_pct}%)")
        print(f"    Revenue: ${revenue:,.2f}")

print("\n" + "=" * 80)
print("13. CAMPAIGN TO CONVERSION LINKAGE")
print("=" * 80)

# Campaign effectiveness end-to-end
campaign_conversion = conn.execute("""
SELECT
    us.campaign_id,
    c.campaign_name,
    c.channel,
    COUNT(DISTINCT us.session_id) as sessions,
    COUNT(DISTINCT us.person_id) as users,
    COUNT(DISTINCT t.person_id) as converted_users,
    ROUND(100.0 * COUNT(DISTINCT t.person_id) / COUNT(DISTINCT us.person_id), 2) as user_conversion_pct,
    COUNT(DISTINCT t.transaction_id) as transactions,
    ROUND(SUM(t.amount_usd), 2) as revenue,
    ROUND(c.budget_usd, 2) as budget,
    ROUND(SUM(t.amount_usd) / c.budget_usd, 2) as roi
FROM user_sessions us
LEFT JOIN campaigns c ON us.campaign_id = c.campaign_id
LEFT JOIN transactions t ON us.person_id = t.person_id
    AND t.timestamp >= us.timestamp
    AND t.timestamp < us.timestamp + INTERVAL 60 DAY
GROUP BY us.campaign_id, c.campaign_name, c.channel, c.budget_usd
HAVING COUNT(DISTINCT us.session_id) >= 10
ORDER BY roi DESC NULLS LAST
LIMIT 15
""").fetchall()

print("\nTop Campaigns by ROI (budget to revenue conversion):")
for camp_id, name, channel, sessions, users, conv_users, conv_pct, trans, revenue, budget, roi in campaign_conversion:
    if name and revenue and revenue > 0:
        print(f"  {name} (ID: {camp_id})")
        print(f"    Channel: {channel}")
        print(f"    Sessions: {sessions:,} | Users: {users:,} | Converted: {conv_users} ({conv_pct}%)")
        print(f"    Revenue: ${revenue:,.2f} | Budget: ${budget:,.2f} | ROI: {roi}x")

print("\n" + "=" * 80)
print("14. RED FLAGS & OPPORTUNITIES")
print("=" * 80)

# Identify red flags and opportunities
red_flags = []

# Flag 1: Low engagement sources
low_engagement_sources = conn.execute("""
SELECT
    source,
    ROUND(AVG(duration_seconds), 1) as avg_duration,
    ROUND(AVG(page_views), 2) as avg_pages,
    COUNT(*) as sessions
FROM user_sessions
GROUP BY source
HAVING AVG(duration_seconds) < 60 OR AVG(page_views) < 2
ORDER BY avg_duration ASC
""").fetchall()

print("\nRED FLAG: Low-Engagement Traffic Sources:")
for source, duration, pages, sessions in low_engagement_sources:
    print(f"  {source}: {duration}s avg duration, {pages} avg pages ({sessions:,} sessions)")
    red_flags.append(f"  {source}: Low engagement - {duration}s duration, {pages} pages")

# Flag 2: High bounce rates (1 page view)
high_bounce_sources = conn.execute("""
SELECT
    source,
    COUNT(*) as total_sessions,
    COUNT(CASE WHEN page_views = 1 THEN 1 END) as bounces,
    ROUND(100.0 * COUNT(CASE WHEN page_views = 1 THEN 1 END) / COUNT(*), 2) as bounce_rate_pct
FROM user_sessions
GROUP BY source
HAVING COUNT(CASE WHEN page_views = 1 THEN 1 END) > 0
ORDER BY bounce_rate_pct DESC
LIMIT 5
""").fetchall()

print("\nRED FLAG: High Bounce Rate Sources:")
for source, total, bounces, bounce_rate in high_bounce_sources:
    if bounce_rate > 50:
        print(f"  {source}: {bounce_rate}% bounce rate ({bounces}/{total} sessions)")
        red_flags.append(f"  {source}: {bounce_rate}% bounce rate")

# Opportunity 1: Underutilized high-quality segments
underutilized = conn.execute("""
SELECT
    us.device,
    us.source,
    COUNT(*) as sessions,
    ROUND(AVG(us.duration_seconds), 1) as avg_duration,
    COUNT(DISTINCT us.person_id) as users,
    COUNT(DISTINCT ns.person_id) as newsletter_subscribers
FROM user_sessions us
LEFT JOIN newsletter_sends ns ON us.person_id = ns.person_id
GROUP BY us.device, us.source
HAVING AVG(us.duration_seconds) > 300  -- High engagement
    AND COUNT(DISTINCT us.person_id) > 50
    AND COUNT(DISTINCT ns.person_id) < COUNT(DISTINCT us.person_id) * 0.1  -- Low newsletter penetration
ORDER BY sessions DESC
LIMIT 5
""").fetchall()

print("\nOPPORTUNITY: High-Engagement Segments with Low Newsletter Penetration:")
for device, source, sessions, duration, users, newsletter_subs in underutilized:
    penetration = (newsletter_subs / users * 100) if users > 0 else 0
    print(f"  {device} + {source}: {users:,} users, {duration}s engagement, only {penetration:.1f}% on newsletter")

# Opportunity 2: Geographic expansion
geographic_opportunity = conn.execute("""
SELECT
    country,
    COUNT(DISTINCT person_id) as users,
    COUNT(*) as sessions,
    ROUND(AVG(duration_seconds), 1) as avg_duration,
    COUNT(DISTINCT CASE WHEN EXISTS (
        SELECT 1 FROM transactions t WHERE t.person_id = us.person_id
    ) THEN person_id END) as converted
FROM user_sessions us
GROUP BY country
HAVING COUNT(*) >= 20  -- Meaningful traffic
    AND COUNT(DISTINCT CASE WHEN EXISTS (
        SELECT 1 FROM transactions t WHERE t.person_id = us.person_id
    ) THEN person_id END) = 0  -- Zero conversions
ORDER BY sessions DESC
LIMIT 5
""").fetchall()

print("\nOPPORTUNITY: Geographies with Traffic but Zero Conversions:")
for country, users, sessions, duration, converted in geographic_opportunity:
    if converted == 0:
        print(f"  {country}: {users:,} users, {sessions:,} sessions, {duration}s engagement - NO CONVERSIONS YET")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE - GENERATING DETAILED REPORT")
print("=" * 80)

# Store all data for report generation
analysis_data = {
    'timestamp': datetime.now().isoformat(),
    'data_period': '2024',
    'total_sessions': conn.execute("SELECT COUNT(*) FROM user_sessions").fetchone()[0],
    'total_users': conn.execute("SELECT COUNT(DISTINCT person_id) FROM user_sessions").fetchone()[0],
    'total_events': conn.execute("SELECT COUNT(*) FROM session_events").fetchone()[0],
    'total_transactions': conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0],
    'total_revenue': conn.execute("SELECT SUM(amount_usd) FROM transactions").fetchone()[0],
    'red_flags': red_flags
}

print(f"\nDataset Summary:")
print(f"  Timestamp: {analysis_data['timestamp']}")
print(f"  Total Sessions: {analysis_data['total_sessions']:,}")
print(f"  Total Users: {analysis_data['total_users']:,}")
print(f"  Total Events: {analysis_data['total_events']:,}")
print(f"  Total Transactions: {analysis_data['total_transactions']:,}")
print(f"  Total Revenue: ${analysis_data['total_revenue']:,.2f}")

conn.close()
print("\n✓ Analysis complete!")
