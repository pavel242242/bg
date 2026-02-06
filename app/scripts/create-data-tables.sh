#!/bin/sh
set -e

echo "[create-tables] Starting PostgreSQL tables creation..."

# Wait for PostgreSQL to be ready
echo "[create-tables] Waiting for PostgreSQL..."
sleep 5

echo "[create-tables] Creating PostgreSQL tables..."

# Create subscribers and events tables
psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" << EOF
-- Create subscribers table
CREATE TABLE IF NOT EXISTS subscribers (
  id SERIAL PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  telegram TEXT,
  token TEXT,
  token_expiry TIMESTAMP,
  email_verified BOOLEAN DEFAULT false,
  telegram_verified BOOLEAN DEFAULT false,
  active BOOLEAN DEFAULT false,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Create events table
CREATE TABLE IF NOT EXISTS events (
  id SERIAL PRIMARY KEY,
  url TEXT NOT NULL UNIQUE,
  title TEXT,
  start_date DATE,
  end_date DATE,
  location TEXT,
  venue TEXT,
  speakers TEXT,
  summary TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
EOF

if [ $? -eq 0 ]; then
    echo "[create-tables]   ✓ PostgreSQL tables created successfully"
else
    echo "[create-tables]   ✗ Failed to create tables"
    exit 1
fi

echo "[create-tables] Complete!"
exit 0
