# Keboola Storage

## Overview

Keboola Storage is the central data repository. All data flows through Storage - extracted data lands here, transformations read from and write to Storage, and writers pull data from Storage.

## Structure

### Buckets

Buckets are logical containers for tables. Naming convention:

- `in.c-<name>` - Input buckets (data coming in)
- `out.c-<name>` - Output buckets (data going out)
- `sys.c-<name>` - System buckets (internal use)

**Example bucket structure:**
```
in.c-sales/
  - sfdc_accounts
  - sfdc_opportunities
  - stripe_customers

in.c-marketing/
  - hubspot_contacts
  - google_analytics_sessions

out.c-analytics/
  - customers_enriched
  - revenue_summary
  - marketing_attribution
```

### Tables

Tables in Keboola are:
- Stored as CSV files
- Can have metadata (descriptions, tags)
- Support primary keys
- Track row counts and data size
- Version controlled (snapshots)

**Table Properties:**
- `id` - Unique identifier (e.g., `in.c-main.customers`)
- `name` - Table name
- `columns` - Array of column names
- `primaryKey` - Array of primary key columns
- `rowsCount` - Number of rows
- `dataSizeBytes` - Size in bytes
- `lastImportDate` - When last updated
- `metadata` - Key-value metadata

### Workspaces

Workspaces are temporary databases for complex transformations:

**Supported Backends:**
- Snowflake (most common)
- Redshift
- Synapse
- Teradata
- Exasol

**Workflow:**
1. Create workspace
2. Load tables from Storage
3. Run SQL transformations
4. Export results back to Storage
5. Destroy workspace

**Use workspaces when:**
- Multiple transformation steps
- Complex joins across many tables
- Need indexes for performance
- Iterative development/testing

## Storage API

### Authentication

All requests require token:
```bash
curl -X GET \
  https://connection.keboola.com/v2/storage/buckets \
  -H "X-StorageApi-Token: YOUR_TOKEN"
```

### Common Operations

#### List Buckets
```bash
GET /v2/storage/buckets
```

Response:
```json
[
  {
    "id": "in.c-main",
    "name": "c-main",
    "stage": "in",
    "description": "Main input bucket",
    "tables": ["customers", "orders"]
  }
]
```

#### Get Table
```bash
GET /v2/storage/tables/in.c-main.customers
```

Response:
```json
{
  "id": "in.c-main.customers",
  "name": "customers",
  "columns": ["id", "name", "email", "created_at"],
  "primaryKey": ["id"],
  "rowsCount": 15420,
  "dataSizeBytes": 1024000,
  "lastImportDate": "2024-01-15T10:30:00+0000"
}
```

#### Export Table
```bash
POST /v2/storage/tables/in.c-main.customers/export-async
```

Request body:
```json
{
  "limit": 1000,
  "changedSince": "-7 days"
}
```

Returns job ID. Use Job Queue API to monitor and get download URL.

#### Import Table
```bash
POST /v2/storage/tables/in.c-main.customers/import-async
```

Request body:
```json
{
  "dataFileId": "12345",
  "incremental": true,
  "delimiter": ",",
  "enclosure": "\""
}
```

## Best Practices

### Bucket Organization

**By Data Source:**
```
in.c-mysql/
in.c-salesforce/
in.c-hubspot/
```

**By Domain:**
```
in.c-sales/
in.c-marketing/
in.c-finance/
```

**Output by Purpose:**
```
out.c-reporting/
out.c-analytics/
out.c-ml-features/
```

### Table Design

**Use Primary Keys:**
```json
{
  "primaryKey": ["customer_id"]
}
```
Enables deduplication and updates.

**Add Metadata:**
```json
{
  "metadata": [
    {"key": "owner", "value": "data-team"},
    {"key": "pii", "value": "true"},
    {"key": "source", "value": "salesforce"}
  ]
}
```

**Descriptive Names:**
- Good: `sfdc_accounts`, `customers_enriched`, `revenue_daily`
- Bad: `table1`, `temp`, `data`

### Incremental Loading

Always use incremental when possible:

**Advantages:**
- Faster execution
- Lower costs
- Less data transfer
- Easier rollback

**Patterns:**

1. **Timestamp-based:**
```json
{
  "incremental": true,
  "incrementalFetchingColumn": "updated_at"
}
```

2. **ID-based:**
```json
{
  "incremental": true,
  "incrementalFetchingColumn": "id"
}
```

3. **Manual state:**
```sql
-- Get last processed ID from state table
SELECT MAX(id) FROM state_table;

-- Extract only new records
SELECT * FROM source WHERE id > ?last_id;
```

### Data Quality

**Validate on Import:**
```sql
-- Check for required fields
SELECT COUNT(*)
FROM "in.c-main.customers"
WHERE customer_id IS NULL;

-- Check for duplicates
SELECT customer_id, COUNT(*)
FROM "in.c-main.customers"
GROUP BY customer_id
HAVING COUNT(*) > 1;
```

**Add Metadata:**
```sql
-- Track lineage
INSERT INTO data_lineage VALUES (
  'in.c-main.customers',
  'salesforce',
  CURRENT_TIMESTAMP(),
  (SELECT COUNT(*) FROM "in.c-main.customers")
);
```

## Common Issues

### Table Not Found
- Check table ID format: `bucket.table`
- Verify bucket exists
- Check access permissions

### Import Failed
- Validate CSV format
- Check column count matches
- Verify delimiter and enclosure
- Ensure no quotes in data

### Performance Issues
- Use incremental loading
- Add primary keys
- Use workspaces for large joins
- Export only needed columns

### Data Type Mismatches
- Keboola storage is type-agnostic (stores as strings)
- Types enforced in transformations and writers
- Validate data types before writing

## Advanced Features

### Aliases
Create virtual tables pointing to another table:
```bash
POST /v2/storage/tables/in.c-main.customers/alias
{
  "name": "customers_view",
  "aliasFilter": {
    "column": "status",
    "values": ["active"]
  }
}
```

### Snapshots
Save table state at a point in time:
```bash
POST /v2/storage/tables/in.c-main.customers/snapshots
{
  "description": "Before migration"
}
```

### Sharing
Share tables across projects:
```bash
POST /v2/storage/tables/in.c-main.customers/share
{
  "sharing": "organization"
}
```

## Resources

- API Reference: https://developers.keboola.com/integrate/storage/api/
- Storage Documentation: https://help.keboola.com/storage/
- Best Practices: https://developers.keboola.com/extend/common-interface/
