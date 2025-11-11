"""
Database module for mock Grafana API.
Uses DuckDB for in-memory data storage.
"""

import duckdb
from typing import Optional

# Global connection
_conn: Optional[duckdb.DuckDBPyConnection] = None

def get_connection() -> duckdb.DuckDBPyConnection:
    """Get the database connection."""
    global _conn
    if _conn is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _conn

def init_db():
    """Initialize the database with required tables."""
    global _conn

    # Create in-memory database
    _conn = duckdb.connect(database=':memory:')

    # Create dashboards table
    _conn.execute("""
        CREATE TABLE dashboards (
            id INTEGER PRIMARY KEY,
            uid VARCHAR NOT NULL UNIQUE,
            title VARCHAR NOT NULL,
            tags VARCHAR,  -- JSON array as string
            starred BOOLEAN DEFAULT FALSE,
            folder_id INTEGER,
            folder_uid VARCHAR,
            folder_title VARCHAR,
            json_model VARCHAR NOT NULL,  -- Full dashboard JSON
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
            version INTEGER DEFAULT 1
        )
    """)

    # Create datasources table
    _conn.execute("""
        CREATE TABLE datasources (
            id INTEGER PRIMARY KEY,
            uid VARCHAR NOT NULL UNIQUE,
            name VARCHAR NOT NULL,
            type VARCHAR NOT NULL,
            url VARCHAR,
            access VARCHAR DEFAULT 'proxy',
            is_default BOOLEAN DEFAULT FALSE,
            json_data VARCHAR  -- Additional configuration as JSON
        )
    """)

    # Create annotations table
    _conn.execute("""
        CREATE TABLE annotations (
            id INTEGER PRIMARY KEY,
            dashboard_id INTEGER,
            panel_id INTEGER,
            time BIGINT NOT NULL,  -- Unix timestamp in milliseconds
            time_end BIGINT,
            text VARCHAR NOT NULL,
            tags VARCHAR  -- JSON array as string
        )
    """)

    # Create folders table
    _conn.execute("""
        CREATE TABLE folders (
            id INTEGER PRIMARY KEY,
            uid VARCHAR NOT NULL UNIQUE,
            title VARCHAR NOT NULL
        )
    """)

    # Enable auto-increment for primary keys
    # DuckDB handles this automatically with INTEGER PRIMARY KEY

    print("✓ Database initialized successfully")

def reset_db():
    """Reset the database (drop and recreate all tables)."""
    global _conn

    if _conn is not None:
        _conn.close()
        _conn = None

    init_db()

def close_db():
    """Close the database connection."""
    global _conn

    if _conn is not None:
        _conn.close()
        _conn = None
