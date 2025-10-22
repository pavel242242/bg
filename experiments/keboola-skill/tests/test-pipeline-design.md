# Test: Pipeline Design

## Test Prompt

> "Help me extract data from PostgreSQL orders table and load it to Snowflake"

## Expected Behavior

Claude should:
1. Ask discovery questions (incremental? SLOs? PII?)
2. Recommend architecture with specific components
3. Provide PostgreSQL extractor JSON config (using `docs-repos/connection-docs/components/extractors/database/postgresql/index.md`)
4. Provide Snowflake writer JSON config
5. Include data quality validations
6. Suggest incremental loading strategy

## Expected Output Elements

✅ Discovery questions (at least 3)
✅ Flow configuration (YAML or JSON)
✅ PostgreSQL extractor config with `incremental: true`
✅ Data validation SQL (duplicate check, null check, freshness check)
✅ Snowflake writer config
✅ Data contract with SLOs

## Regression Indicators

❌ No validation steps
❌ Full refresh instead of incremental
❌ Missing SLOs or data contract
❌ Generic advice without Keboola-specific configs
❌ Incorrect component names
