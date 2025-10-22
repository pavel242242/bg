# ELT Unit — {name}
## Source
RAW: {raw.schema}.{source_table}  
Owner: {owner} | Schedule: {cron}

## STAGED Table
Target: {staged.schema}.{staged_table}
Schema:
- {col} {type} {nullable?}

Transformations:
- dedupe keys: {keys}
- null policy: {policy}
- timezone normalization: {tz_policy}
- partitioning: {partition_cols}

## Validation (SQL)
-- Row count delta
{validation_rowcount_sql}

-- Duplicate keys
{validation_dupes_sql}

-- Freshness
{validation_freshness_sql}

## Notes
Idempotent logic, safe re-runs, comment decisions.
