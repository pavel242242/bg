"""Database module for mock PostHog API."""

import duckdb
from typing import Optional

_conn: Optional[duckdb.DuckDBPyConnection] = None

def get_connection() -> duckdb.DuckDBPyConnection:
    global _conn
    if _conn is None:
        raise RuntimeError("Database not initialized")
    return _conn

def init_db():
    global _conn
    _conn = duckdb.connect(database=':memory:')

    _conn.execute("""
        CREATE TABLE projects (
            id INTEGER PRIMARY KEY,
            uuid VARCHAR UNIQUE,
            name VARCHAR,
            organization VARCHAR
        )
    """)

    _conn.execute("""
        CREATE TABLE events (
            id INTEGER PRIMARY KEY,
            project_id INTEGER,
            event VARCHAR,
            timestamp TIMESTAMP,
            distinct_id VARCHAR,
            properties VARCHAR
        )
    """)

    _conn.execute("""
        CREATE TABLE event_definitions (
            id INTEGER PRIMARY KEY,
            project_id INTEGER,
            name VARCHAR,
            volume_30_day INTEGER,
            query_usage_30_day INTEGER
        )
    """)

    _conn.execute("""
        CREATE TABLE feature_flags (
            id INTEGER PRIMARY KEY,
            project_id INTEGER,
            key VARCHAR,
            name VARCHAR,
            active BOOLEAN,
            filters VARCHAR
        )
    """)

    _conn.execute("""
        CREATE TABLE insights (
            id INTEGER PRIMARY KEY,
            project_id INTEGER,
            name VARCHAR,
            filters VARCHAR,
            created_at TIMESTAMP,
            result VARCHAR
        )
    """)

    print("✓ PostHog database initialized")
