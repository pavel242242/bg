# Debugging Cheatsheet (Pipelines & Apps)

## Quick Triage Flow
1) **Is it auth?** Test `SELECT 1` from the workspace.  
2) **Is it freshness?** Compare `MAX(ingested_at)` vs now.  
3) **Is it schema?** Diff expected vs actual columns/types.  
4) **Is it volume?** Row deltas vs trailing median.  
5) **Is it compute?** Inspect query plan / job utilization.

## Useful SQL Snippets
- Freshness minutes:
```sql
SELECT TIMESTAMPDIFF(MINUTE, MAX(ingested_at), CURRENT_TIMESTAMP) AS freshness_m;
```
- Duplicate keys:
```sql
SELECT key_col, COUNT(*) c FROM table GROUP BY 1 HAVING c>1;
```
- Distribution drift (KS proxy):
```sql
-- Compare quantiles between windows (approximate)
```

## Streamlit Tips
- Cache data with TTL (`@st.cache_data(ttl=60)`)
- Use parameterized queries for filters
- Surface errors with `st.warning` and link to runbook
