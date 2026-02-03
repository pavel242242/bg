#!/bin/sh
set -e

echo "[create-tables] Starting Data Tables creation..."

# Wait for PostgreSQL to be ready
echo "[create-tables] Waiting for PostgreSQL..."
sleep 5

# Get project ID from database
PROJECT_ID=$(psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -c "SELECT id FROM project LIMIT 1;" 2>/dev/null | tr -d ' \n')

if [ -z "$PROJECT_ID" ]; then
    echo "[create-tables]   ⚠ No project found, waiting for owner setup..."
    sleep 10
    PROJECT_ID=$(psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -c "SELECT id FROM project LIMIT 1;" | tr -d ' \n')
fi

if [ -z "$PROJECT_ID" ]; then
    echo "[create-tables]   ✗ Still no project found, exiting"
    exit 1
fi

echo "[create-tables]   Project ID: $PROJECT_ID"

# Check if tables already exist
EXISTING=$(psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -c "SELECT COUNT(*) FROM data_table WHERE name IN ('subscribers', 'events');" | tr -d ' ')

if [ "$EXISTING" -eq "2" ]; then
    echo "[create-tables]   ℹ Data Tables already exist, skipping"
    exit 0
fi

echo "[create-tables] Creating Data Tables..."

# Create subscribers table
psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" << EOF
-- Create subscribers table (if not exists)
INSERT INTO data_table (id, name, "projectId", "createdAt", "updatedAt")
SELECT 'subscribers', 'subscribers', '$PROJECT_ID', NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM data_table WHERE id = 'subscribers');

-- Create subscribers columns
INSERT INTO data_table_column (id, name, type, index, "dataTableId", "createdAt", "updatedAt")
SELECT * FROM (VALUES
  ('sub-col-1', 'email', 'string', 0, 'subscribers', NOW(), NOW()),
  ('sub-col-2', 'telegram', 'string', 1, 'subscribers', NOW(), NOW()),
  ('sub-col-3', 'token', 'string', 2, 'subscribers', NOW(), NOW()),
  ('sub-col-4', 'token_expiry', 'string', 3, 'subscribers', NOW(), NOW()),
  ('sub-col-5', 'email_verified', 'boolean', 4, 'subscribers', NOW(), NOW()),
  ('sub-col-6', 'telegram_verified', 'boolean', 5, 'subscribers', NOW(), NOW()),
  ('sub-col-7', 'active', 'boolean', 6, 'subscribers', NOW(), NOW()),
  ('sub-col-8', 'created_at', 'string', 7, 'subscribers', NOW(), NOW())
) AS v(id, name, type, index, "dataTableId", "createdAt", "updatedAt")
WHERE NOT EXISTS (SELECT 1 FROM data_table_column WHERE "dataTableId" = 'subscribers');

-- Create events table (if not exists)
INSERT INTO data_table (id, name, "projectId", "createdAt", "updatedAt")
SELECT 'events', 'events', '$PROJECT_ID', NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM data_table WHERE id = 'events');

-- Create events columns
INSERT INTO data_table_column (id, name, type, index, "dataTableId", "createdAt", "updatedAt")
SELECT * FROM (VALUES
  ('evt-col-1', 'title', 'string', 0, 'events', NOW(), NOW()),
  ('evt-col-2', 'summary', 'string', 1, 'events', NOW(), NOW()),
  ('evt-col-3', 'location', 'string', 2, 'events', NOW(), NOW()),
  ('evt-col-4', 'venue', 'string', 3, 'events', NOW(), NOW()),
  ('evt-col-5', 'speakers', 'string', 4, 'events', NOW(), NOW()),
  ('evt-col-6', 'start_date', 'string', 5, 'events', NOW(), NOW()),
  ('evt-col-7', 'end_date', 'string', 6, 'events', NOW(), NOW()),
  ('evt-col-8', 'url', 'string', 7, 'events', NOW(), NOW()),
  ('evt-col-9', 'created_at', 'string', 8, 'events', NOW(), NOW())
) AS v(id, name, type, index, "dataTableId", "createdAt", "updatedAt")
WHERE NOT EXISTS (SELECT 1 FROM data_table_column WHERE "dataTableId" = 'events');
EOF

echo "[create-tables]   ✓ Data Tables created successfully"
echo "[create-tables] Complete!"
exit 0
