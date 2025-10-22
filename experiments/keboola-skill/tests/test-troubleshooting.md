# Test: Troubleshooting with Runbooks

## Test Prompt

> "My pipeline is failing with duplicate key errors"

## Expected Behavior

Claude should:
1. Reference `resources/runbooks/common_issues.md`
2. Follow systematic debug approach
3. Provide SQL to identify duplicates
4. Suggest root cause analysis
5. Recommend fixes (upsert pattern, deduplication)
6. Propose prevention strategies

## Expected Output Elements

✅ Reference to common_issues runbook
✅ SQL query to find duplicate rows
✅ Root cause analysis (source has dupes? transformation creates dupes?)
✅ Fix options (MERGE/UPSERT, ROW_NUMBER deduplication)
✅ Prevention (unique constraints, validation tests)
✅ Example SQL using MERGE or ROW_NUMBER

## Regression Indicators

❌ Generic troubleshooting without Keboola context
❌ Doesn't use runbook guidance
❌ No SQL provided to diagnose issue
❌ Doesn't suggest both fix AND prevention
