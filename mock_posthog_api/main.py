"""
Mock PostHog API Server

Provides mock endpoints for PostHog API testing in E2B sandboxes.
Uses DuckDB for in-memory data storage with sample fixtures.

Run with: uvicorn main:app --host 0.0.0.0 --port 8001
"""

from fastapi import FastAPI, HTTPException, Header, Query
from typing import Optional, List
import duckdb
from datetime import datetime
import json

from db import init_db, get_connection
from fixtures import load_fixtures

app = FastAPI(title="Mock PostHog API", version="1.0.0")

@app.on_event("startup")
async def startup():
    init_db()
    load_fixtures()

def verify_auth(authorization: Optional[str] = Header(None)):
    """Verify Bearer token authentication."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    return True

# =======================================================================
# User & Organization
# =======================================================================

@app.get("/api/users/@me")
async def get_current_user(_auth=verify_auth):
    """Get current user."""
    return {
        "id": 1,
        "uuid": "user-123",
        "distinct_id": "user@example.com",
        "first_name": "Test",
        "email": "user@example.com",
        "organization": "org-123"
    }

# =======================================================================
# Projects
# =======================================================================

@app.get("/api/projects")
async def list_projects(_auth=verify_auth):
    """List all projects."""
    conn = get_connection()
    results = conn.execute("SELECT * FROM projects").fetchall()

    return {
        "results": [
            {
                "id": row[0],
                "uuid": row[1],
                "name": row[2],
                "organization": row[3]
            }
            for row in results
        ]
    }

@app.get("/api/projects/{project_id}")
async def get_project(project_id: int, _auth=verify_auth):
    """Get project details."""
    conn = get_connection()
    result = conn.execute("SELECT * FROM projects WHERE id = ?", [project_id]).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail=f"Project not found: {project_id}")

    return {
        "id": result[0],
        "uuid": result[1],
        "name": result[2],
        "organization": result[3]
    }

# =======================================================================
# Events
# =======================================================================

@app.get("/api/projects/{project_id}/events")
async def query_events(
    project_id: int,
    event: Optional[str] = Query(None),
    after: Optional[str] = Query(None),
    before: Optional[str] = Query(None),
    limit: int = Query(100),
    _auth=verify_auth
):
    """Query events."""
    conn = get_connection()

    sql = "SELECT * FROM events WHERE project_id = ?"
    params = [project_id]

    if event:
        sql += " AND event = ?"
        params.append(event)

    if after:
        sql += " AND timestamp >= ?"
        params.append(after)

    if before:
        sql += " AND timestamp <= ?"
        params.append(before)

    sql += f" ORDER BY timestamp DESC LIMIT {limit}"

    results = conn.execute(sql, params).fetchall()

    return {
        "results": [
            {
                "id": row[0],
                "event": row[2],
                "timestamp": row[3],
                "distinct_id": row[4],
                "properties": json.loads(row[5]) if row[5] else {}
            }
            for row in results
        ]
    }

@app.get("/api/projects/{project_id}/event_definitions")
async def get_event_definitions(project_id: int, _auth=verify_auth):
    """Get event definitions."""
    conn = get_connection()
    results = conn.execute(
        "SELECT * FROM event_definitions WHERE project_id = ?",
        [project_id]
    ).fetchall()

    return {
        "results": [
            {
                "id": row[0],
                "name": row[2],
                "volume_30_day": row[3],
                "query_usage_30_day": row[4]
            }
            for row in results
        ]
    }

# =======================================================================
# Feature Flags
# =======================================================================

@app.get("/api/projects/{project_id}/feature_flags")
async def list_feature_flags(project_id: int, _auth=verify_auth):
    """List feature flags."""
    conn = get_connection()
    results = conn.execute(
        "SELECT * FROM feature_flags WHERE project_id = ?",
        [project_id]
    ).fetchall()

    return {
        "results": [
            {
                "id": row[0],
                "key": row[2],
                "name": row[3],
                "active": bool(row[4]),
                "filters": json.loads(row[5]) if row[5] else {}
            }
            for row in results
        ]
    }

@app.get("/api/projects/{project_id}/feature_flags/{flag_id}")
async def get_feature_flag(project_id: int, flag_id: int, _auth=verify_auth):
    """Get feature flag."""
    conn = get_connection()
    result = conn.execute(
        "SELECT * FROM feature_flags WHERE project_id = ? AND id = ?",
        [project_id, flag_id]
    ).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail=f"Feature flag not found: {flag_id}")

    return {
        "id": result[0],
        "key": result[2],
        "name": result[3],
        "active": bool(result[4]),
        "filters": json.loads(result[5]) if result[5] else {}
    }

# =======================================================================
# Insights
# =======================================================================

@app.get("/api/projects/{project_id}/insights")
async def list_insights(project_id: int, limit: int = Query(100), _auth=verify_auth):
    """List insights."""
    conn = get_connection()
    results = conn.execute(
        f"SELECT * FROM insights WHERE project_id = ? LIMIT {limit}",
        [project_id]
    ).fetchall()

    return {
        "results": [
            {
                "id": row[0],
                "name": row[2],
                "filters": json.loads(row[3]) if row[3] else {},
                "created_at": row[4]
            }
            for row in results
        ]
    }

@app.get("/api/projects/{project_id}/insights/{insight_id}")
async def get_insight(project_id: int, insight_id: int, _auth=verify_auth):
    """Get insight."""
    conn = get_connection()
    result = conn.execute(
        "SELECT * FROM insights WHERE project_id = ? AND id = ?",
        [project_id, insight_id]
    ).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail=f"Insight not found: {insight_id}")

    return {
        "id": result[0],
        "name": result[2],
        "filters": json.loads(result[3]) if result[3] else {},
        "result": json.loads(result[5]) if result[5] else None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
