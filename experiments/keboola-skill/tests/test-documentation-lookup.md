# Test: Documentation Lazy-Loading

## Test Prompt

> "How do I configure MySQL CDC extractor?"

## Expected Behavior

Claude should:
1. Search KNOWLEDGE_MAP.md for "MySQL"
2. Find path: `docs-repos/connection-docs/components/extractors/database/mysql/index.md`
3. Use Read tool to fetch the documentation
4. Provide specific CDC configuration details (Debezium, binlog setup)
5. Include supported versions (MySQL 5.7, 8.0.x, 8.2)

## Expected Output Elements

✅ Reference to MySQL CDC connector (kds-team.ex-mysql-cdc)
✅ Binlog configuration requirements
✅ Supported MySQL versions mentioned
✅ Snapshot behavior explained
✅ Example JSON configuration

## Regression Indicators

❌ Doesn't use Read tool to fetch docs
❌ Provides outdated or incorrect information
❌ Doesn't mention Debezium or binlog
❌ Guesses instead of checking documentation
