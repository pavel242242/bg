-- TEMPORAL CONSISTENCY ANALYSIS v1.1 - SQL EVIDENCE QUERIES
-- Marketing Data Quality Assessment
-- Data location: /tmp/datagen/marketing_example_v1.1/

-- ============================================================================
-- VIOLATION 1: Sessions Before Person Registration
-- ============================================================================

-- Count total violations
SELECT 
    COUNT(*) as total_violations,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM user_sessions), 2) as percentage
FROM user_sessions us
INNER JOIN people p ON us.person_id = p.person_id
WHERE us.timestamp < p.first_seen_date;

-- Detailed severity analysis
SELECT 
    COUNT(*) as total_violations,
    COUNT(*) FILTER (WHERE datediff('day', p.first_seen_date, us.timestamp) < -180) 
        as more_than_6_months_early,
    COUNT(*) FILTER (WHERE datediff('day', p.first_seen_date, us.timestamp) >= -30) 
        as less_than_30_days_early,
    MIN(datediff('day', p.first_seen_date, us.timestamp)) as earliest_violation_days,
    ROUND(AVG(datediff('day', p.first_seen_date, us.timestamp)), 2) as avg_days_before_registration
FROM user_sessions us
INNER JOIN people p ON us.person_id = p.person_id
WHERE us.timestamp < p.first_seen_date;

-- Sample violations
SELECT 
    us.session_id,
    us.person_id,
    us.timestamp as session_time,
    p.first_seen_date as person_registration,
    datediff('day', p.first_seen_date, us.timestamp) as days_before
FROM user_sessions us
INNER JOIN people p ON us.person_id = p.person_id
WHERE us.timestamp < p.first_seen_date
ORDER BY datediff('day', p.first_seen_date, us.timestamp) ASC
LIMIT 5;

-- ============================================================================
-- VIOLATION 2: Campaign Mentions Before Campaign Start
-- ============================================================================

-- Count total violations
SELECT 
    COUNT(*) as total_violations,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM campaign_mentions), 2) as percentage
FROM campaign_mentions cm
INNER JOIN campaigns c ON cm.campaign_id = c.campaign_id
WHERE CAST(cm.timestamp AS DATE) < c.start_date;

-- Detailed severity analysis
SELECT 
    COUNT(*) as total_violations,
    COUNT(*) FILTER (WHERE datediff('day', c.start_date, cm.timestamp) < -180) 
        as more_than_6_months_early,
    COUNT(*) FILTER (WHERE datediff('day', c.start_date, cm.timestamp) >= -30) 
        as less_than_30_days_early,
    MIN(datediff('day', c.start_date, cm.timestamp)) as earliest_violation_days,
    ROUND(AVG(datediff('day', c.start_date, cm.timestamp)), 2) as avg_days_before_campaign_start
FROM campaign_mentions cm
INNER JOIN campaigns c ON cm.campaign_id = c.campaign_id
WHERE CAST(cm.timestamp AS DATE) < c.start_date;

-- Sample violations
SELECT 
    cm.mention_id,
    cm.campaign_id,
    cm.timestamp as mention_time,
    c.start_date as campaign_start,
    datediff('day', c.start_date, cm.timestamp) as days_before
FROM campaign_mentions cm
INNER JOIN campaigns c ON cm.campaign_id = c.campaign_id
WHERE CAST(cm.timestamp AS DATE) < c.start_date
ORDER BY datediff('day', c.start_date, cm.timestamp) ASC
LIMIT 5;

-- ============================================================================
-- VIOLATION 3: Transactions Before Company Signed
-- ============================================================================

-- Count total violations
SELECT 
    COUNT(*) as total_violations,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM transactions), 2) as percentage
FROM transactions t
INNER JOIN companies c ON t.company_id = c.company_id
WHERE t.timestamp < c.signed_date;

-- Detailed severity analysis
SELECT 
    COUNT(*) as total_violations,
    COUNT(*) FILTER (WHERE datediff('day', c.signed_date, t.timestamp) < -180) 
        as more_than_6_months_early,
    COUNT(*) FILTER (WHERE datediff('day', c.signed_date, t.timestamp) >= -30) 
        as less_than_30_days_early,
    MIN(datediff('day', c.signed_date, t.timestamp)) as earliest_violation_days,
    ROUND(AVG(datediff('day', c.signed_date, t.timestamp)), 2) as avg_days_before_signing
FROM transactions t
INNER JOIN companies c ON t.company_id = c.company_id
WHERE t.timestamp < c.signed_date;

-- Sample violations
SELECT 
    t.transaction_id,
    t.company_id,
    t.timestamp as transaction_date,
    c.signed_date as company_signed,
    datediff('day', c.signed_date, t.timestamp) as days_before
FROM transactions t
INNER JOIN companies c ON t.company_id = c.company_id
WHERE t.timestamp < c.signed_date
ORDER BY datediff('day', c.signed_date, t.timestamp) ASC
LIMIT 5;

-- ============================================================================
-- VIOLATION 4: Engagement Before Posts
-- ============================================================================

-- Count total violations
SELECT 
    COUNT(*) as total_violations,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM social_engagement), 2) as percentage
FROM social_engagement se
INNER JOIN social_posts sp ON se.post_id = sp.post_id
WHERE se.timestamp < sp.posted_at;

-- Detailed severity analysis (with hours)
SELECT 
    COUNT(*) as total_violations,
    COUNT(*) FILTER (WHERE datediff('hour', sp.posted_at, se.timestamp) < -168) 
        as more_than_7_days_early,
    COUNT(*) FILTER (WHERE datediff('hour', sp.posted_at, se.timestamp) >= -1) 
        as less_than_1_hour_early,
    MIN(datediff('hour', sp.posted_at, se.timestamp)) as earliest_violation_hours,
    ROUND(AVG(datediff('hour', sp.posted_at, se.timestamp)), 2) as avg_hours_before_post
FROM social_engagement se
INNER JOIN social_posts sp ON se.post_id = sp.post_id
WHERE se.timestamp < sp.posted_at;

-- Sample violations
SELECT 
    se.engagement_id,
    se.post_id,
    se.timestamp as engagement_time,
    sp.posted_at as post_time,
    datediff('hour', sp.posted_at, se.timestamp) as hours_before
FROM social_engagement se
INNER JOIN social_posts sp ON se.post_id = sp.post_id
WHERE se.timestamp < sp.posted_at
ORDER BY datediff('hour', sp.posted_at, se.timestamp) ASC
LIMIT 5;

-- ============================================================================
-- VIOLATION 5: Tickets Resolved Before Created
-- ============================================================================

-- Count total violations
SELECT 
    COUNT(*) as total_violations,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM support_tickets), 2) as percentage
FROM support_tickets st
WHERE st.resolved_at < st.created_at;

-- Detailed severity analysis (with hours)
SELECT 
    COUNT(*) as total_violations,
    COUNT(*) FILTER (WHERE datediff('hour', st.created_at, st.resolved_at) < -24) 
        as more_than_1_day_early,
    COUNT(*) FILTER (WHERE datediff('hour', st.created_at, st.resolved_at) >= 0) 
        as resolved_same_time_or_later,
    MIN(datediff('hour', st.created_at, st.resolved_at)) as earliest_violation_hours,
    ROUND(AVG(datediff('hour', st.created_at, st.resolved_at)), 2) as avg_hours_before_creation
FROM support_tickets st
WHERE st.resolved_at < st.created_at;

-- Sample violations
SELECT 
    st.ticket_id,
    st.created_at,
    st.resolved_at,
    datediff('hour', st.created_at, st.resolved_at) as hours_before_creation
FROM support_tickets st
WHERE st.resolved_at < st.created_at
ORDER BY datediff('hour', st.created_at, st.resolved_at) ASC
LIMIT 5;

-- ============================================================================
-- COMPREHENSIVE SUMMARY
-- ============================================================================

-- Total violations across all violation types
SELECT 
    'Sessions before registration' as violation_type,
    COUNT(*) as violations,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM user_sessions), 2) as percentage
FROM user_sessions us
INNER JOIN people p ON us.person_id = p.person_id
WHERE us.timestamp < p.first_seen_date
UNION ALL
SELECT 
    'Mentions before campaign start',
    COUNT(*) as violations,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM campaign_mentions), 2) as percentage
FROM campaign_mentions cm
INNER JOIN campaigns c ON cm.campaign_id = c.campaign_id
WHERE CAST(cm.timestamp AS DATE) < c.start_date
UNION ALL
SELECT 
    'Transactions before company signed',
    COUNT(*) as violations,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM transactions), 2) as percentage
FROM transactions t
INNER JOIN companies c ON t.company_id = c.company_id
WHERE t.timestamp < c.signed_date
UNION ALL
SELECT 
    'Engagement before posts',
    COUNT(*) as violations,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM social_engagement), 2) as percentage
FROM social_engagement se
INNER JOIN social_posts sp ON se.post_id = sp.post_id
WHERE se.timestamp < sp.posted_at
UNION ALL
SELECT 
    'Tickets resolved before created',
    COUNT(*) as violations,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM support_tickets), 2) as percentage
FROM support_tickets st
WHERE st.resolved_at < st.created_at;

-- ============================================================================
-- SEVERITY DISTRIBUTION ANALYSIS
-- ============================================================================

-- Violation severity breakdown
SELECT 
    'Sessions before registration' as violation_type,
    COUNT(*) FILTER (WHERE datediff('day', p.first_seen_date, us.timestamp) < -180) as severe_180plus_days,
    COUNT(*) FILTER (WHERE datediff('day', p.first_seen_date, us.timestamp) < -90 
                     AND datediff('day', p.first_seen_date, us.timestamp) >= -180) as severe_90to180_days,
    COUNT(*) as total,
    ROUND(100.0 * COUNT(*) FILTER (WHERE datediff('day', p.first_seen_date, us.timestamp) < -180) / COUNT(*), 1) as severe_pct
FROM user_sessions us
INNER JOIN people p ON us.person_id = p.person_id
WHERE us.timestamp < p.first_seen_date
UNION ALL
SELECT 
    'Mentions before campaign start',
    COUNT(*) FILTER (WHERE datediff('day', c.start_date, cm.timestamp) < -180),
    COUNT(*) FILTER (WHERE datediff('day', c.start_date, cm.timestamp) < -90 
                     AND datediff('day', c.start_date, cm.timestamp) >= -180),
    COUNT(*),
    ROUND(100.0 * COUNT(*) FILTER (WHERE datediff('day', c.start_date, cm.timestamp) < -180) / COUNT(*), 1)
FROM campaign_mentions cm
INNER JOIN campaigns c ON cm.campaign_id = c.campaign_id
WHERE CAST(cm.timestamp AS DATE) < c.start_date
UNION ALL
SELECT 
    'Transactions before company signed',
    COUNT(*) FILTER (WHERE datediff('day', c.signed_date, t.timestamp) < -180),
    COUNT(*) FILTER (WHERE datediff('day', c.signed_date, t.timestamp) < -90 
                     AND datediff('day', c.signed_date, t.timestamp) >= -180),
    COUNT(*),
    ROUND(100.0 * COUNT(*) FILTER (WHERE datediff('day', c.signed_date, t.timestamp) < -180) / COUNT(*), 1)
FROM transactions t
INNER JOIN companies c ON t.company_id = c.company_id
WHERE t.timestamp < c.signed_date
UNION ALL
SELECT 
    'Engagement before posts',
    COUNT(*) FILTER (WHERE datediff('hour', sp.posted_at, se.timestamp) < -168),
    COUNT(*) FILTER (WHERE datediff('hour', sp.posted_at, se.timestamp) < -84 
                     AND datediff('hour', sp.posted_at, se.timestamp) >= -168),
    COUNT(*),
    ROUND(100.0 * COUNT(*) FILTER (WHERE datediff('hour', sp.posted_at, se.timestamp) < -168) / COUNT(*), 1)
FROM social_engagement se
INNER JOIN social_posts sp ON se.post_id = sp.post_id
WHERE se.timestamp < sp.posted_at
UNION ALL
SELECT 
    'Tickets resolved before created',
    COUNT(*) FILTER (WHERE datediff('hour', st.created_at, st.resolved_at) < -24),
    COUNT(*) FILTER (WHERE datediff('hour', st.created_at, st.resolved_at) < -12 
                     AND datediff('hour', st.created_at, st.resolved_at) >= -24),
    COUNT(*),
    ROUND(100.0 * COUNT(*) FILTER (WHERE datediff('hour', st.created_at, st.resolved_at) < -24) / COUNT(*), 1)
FROM support_tickets st
WHERE st.resolved_at < st.created_at;
