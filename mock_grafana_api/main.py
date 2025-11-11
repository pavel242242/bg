"""
Mock Grafana API Server

Provides mock endpoints for Grafana API testing in E2B sandboxes.
Uses DuckDB for in-memory data storage with sample fixtures.

Run with: uvicorn main:app --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI, HTTPException, Header, Query
from fastapi.responses import JSONResponse
from typing import Optional, List
import duckdb
from datetime import datetime
import json

from db import init_db, get_connection
from fixtures import load_fixtures

app = FastAPI(title="Mock Grafana API", version="1.0.0")

# Initialize database on startup
@app.on_event("startup")
async def startup():
    init_db()
    load_fixtures()

# ============================================================================
# Authentication Middleware
# ============================================================================

def verify_auth(authorization: Optional[str] = Header(None)):
    """Verify Bearer token authentication."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")

    # In mock, accept any token
    return True

# ============================================================================
# Health & Status
# ============================================================================

@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"database": "ok", "status": "ok"}

# ============================================================================
# Dashboard Endpoints
# ============================================================================

@app.get("/api/search")
async def search(
    query: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    type: Optional[str] = Query("dash-db"),
    starred: Optional[str] = Query(None),
    limit: int = Query(1000),
    _auth=verify_auth
):
    """Search for dashboards or folders."""
    conn = get_connection()

    if type == "dash-db":
        sql = "SELECT * FROM dashboards WHERE 1=1"
        params = []

        if query:
            sql += " AND (title LIKE ? OR uid LIKE ?)"
            params.extend([f"%{query}%", f"%{query}%"])

        if tag:
            sql += " AND tags LIKE ?"
            params.append(f"%{tag}%")

        if starred == "true":
            sql += " AND starred = true"

        sql += f" LIMIT {limit}"

        results = conn.execute(sql, params).fetchall()

        return [
            {
                "id": row[0],
                "uid": row[1],
                "title": row[2],
                "uri": f"db/{row[1]}",
                "url": f"/d/{row[1]}",
                "slug": row[1],
                "type": "dash-db",
                "tags": json.loads(row[3]) if row[3] else [],
                "isStarred": row[4],
                "folderId": row[5],
                "folderUid": row[6],
                "folderTitle": row[7]
            }
            for row in results
        ]

    elif type == "dash-folder":
        sql = "SELECT * FROM folders WHERE 1=1"
        params = []

        if query:
            sql += " AND (title LIKE ? OR uid LIKE ?)"
            params.extend([f"%{query}%", f"%{query}%"])

        sql += f" LIMIT {limit}"
        results = conn.execute(sql, params).fetchall()

        return [
            {
                "id": row[0],
                "uid": row[1],
                "title": row[2],
                "type": "dash-folder"
            }
            for row in results
        ]

    return []

@app.get("/api/dashboards/uid/{uid}")
async def get_dashboard_by_uid(uid: str, _auth=verify_auth):
    """Get dashboard by UID."""
    conn = get_connection()

    result = conn.execute(
        "SELECT * FROM dashboards WHERE uid = ?",
        [uid]
    ).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail=f"Dashboard not found: {uid}")

    # Get dashboard JSON
    dashboard_json = json.loads(result[8])  # json_model column

    return {
        "meta": {
            "type": "db",
            "canSave": True,
            "canEdit": True,
            "canAdmin": False,
            "canStar": True,
            "slug": result[1],
            "url": f"/d/{result[1]}",
            "expires": "0001-01-01T00:00:00Z",
            "created": result[9],
            "updated": result[10],
            "updatedBy": "admin",
            "createdBy": "admin",
            "version": result[11],
            "hasAcl": False,
            "isFolder": False,
            "folderId": result[5],
            "folderUid": result[6],
            "folderTitle": result[7],
            "isStarred": result[4]
        },
        "dashboard": dashboard_json
    }

@app.get("/api/dashboards/home")
async def get_home_dashboard(_auth=verify_auth):
    """Get home dashboard."""
    # Return first dashboard as home
    conn = get_connection()
    result = conn.execute("SELECT * FROM dashboards LIMIT 1").fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="No home dashboard configured")

    dashboard_json = json.loads(result[8])

    return {
        "meta": {
            "isHome": True,
            "slug": result[1]
        },
        "dashboard": dashboard_json
    }

# ============================================================================
# Data Source Endpoints
# ============================================================================

@app.get("/api/datasources")
async def list_datasources(_auth=verify_auth):
    """List all data sources."""
    conn = get_connection()
    results = conn.execute("SELECT * FROM datasources").fetchall()

    return [
        {
            "id": row[0],
            "uid": row[1],
            "name": row[2],
            "type": row[3],
            "url": row[4],
            "access": row[5],
            "isDefault": row[6],
            "jsonData": json.loads(row[7]) if row[7] else {}
        }
        for row in results
    ]

@app.get("/api/datasources/{datasource_id}")
async def get_datasource_by_id(datasource_id: int, _auth=verify_auth):
    """Get data source by ID."""
    conn = get_connection()
    result = conn.execute(
        "SELECT * FROM datasources WHERE id = ?",
        [datasource_id]
    ).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail=f"Data source not found: {datasource_id}")

    return {
        "id": result[0],
        "uid": result[1],
        "name": result[2],
        "type": result[3],
        "url": result[4],
        "access": result[5],
        "isDefault": result[6],
        "jsonData": json.loads(result[7]) if result[7] else {}
    }

@app.get("/api/datasources/name/{name}")
async def get_datasource_by_name(name: str, _auth=verify_auth):
    """Get data source by name."""
    conn = get_connection()
    result = conn.execute(
        "SELECT * FROM datasources WHERE name = ?",
        [name]
    ).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail=f"Data source not found: {name}")

    return {
        "id": result[0],
        "uid": result[1],
        "name": result[2],
        "type": result[3],
        "url": result[4],
        "access": result[5],
        "isDefault": result[6],
        "jsonData": json.loads(result[7]) if result[7] else {}
    }

@app.get("/api/datasources/uid/{uid}")
async def get_datasource_by_uid(uid: str, _auth=verify_auth):
    """Get data source by UID."""
    conn = get_connection()
    result = conn.execute(
        "SELECT * FROM datasources WHERE uid = ?",
        [uid]
    ).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail=f"Data source not found: {uid}")

    return {
        "id": result[0],
        "uid": result[1],
        "name": result[2],
        "type": result[3],
        "url": result[4],
        "access": result[5],
        "isDefault": result[6],
        "jsonData": json.loads(result[7]) if result[7] else {}
    }

# ============================================================================
# Annotation Endpoints
# ============================================================================

@app.get("/api/annotations")
async def get_annotations(
    from_param: Optional[int] = Query(None, alias="from"),
    to: Optional[int] = Query(None),
    dashboardId: Optional[int] = Query(None),
    panelId: Optional[int] = Query(None),
    tags: Optional[List[str]] = Query(None),
    limit: int = Query(100),
    _auth=verify_auth
):
    """Query annotations."""
    conn = get_connection()

    sql = "SELECT * FROM annotations WHERE 1=1"
    params = []

    if from_param:
        sql += " AND time >= ?"
        params.append(from_param)

    if to:
        sql += " AND time <= ?"
        params.append(to)

    if dashboardId:
        sql += " AND dashboard_id = ?"
        params.append(dashboardId)

    if panelId:
        sql += " AND panel_id = ?"
        params.append(panelId)

    if tags:
        # Simple tag matching (in production would be more sophisticated)
        for tag in tags:
            sql += " AND tags LIKE ?"
            params.append(f"%{tag}%")

    sql += f" LIMIT {limit}"

    results = conn.execute(sql, params).fetchall()

    return [
        {
            "id": row[0],
            "dashboardId": row[1],
            "panelId": row[2],
            "time": row[3],
            "timeEnd": row[4],
            "text": row[5],
            "tags": json.loads(row[6]) if row[6] else []
        }
        for row in results
    ]

@app.post("/api/annotations")
async def create_annotation(
    annotation: dict,
    _auth=verify_auth
):
    """Create an annotation."""
    conn = get_connection()

    time = annotation.get('time', int(datetime.now().timestamp() * 1000))

    conn.execute(
        """
        INSERT INTO annotations (dashboard_id, panel_id, time, time_end, text, tags)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            annotation.get('dashboardId'),
            annotation.get('panelId'),
            time,
            annotation.get('timeEnd'),
            annotation.get('text'),
            json.dumps(annotation.get('tags', []))
        ]
    )

    result = conn.execute("SELECT last_insert_rowid()").fetchone()

    return {
        "id": result[0],
        "message": "Annotation added"
    }

# ============================================================================
# Organization & User Endpoints
# ============================================================================

@app.get("/api/org")
async def get_current_org(_auth=verify_auth):
    """Get current organization."""
    return {
        "id": 1,
        "name": "Mock Organization",
        "address": {
            "address1": "",
            "address2": "",
            "city": "",
            "zipCode": "",
            "state": "",
            "country": ""
        }
    }

@app.get("/api/orgs")
async def list_orgs(_auth=verify_auth):
    """List all organizations."""
    return [
        {
            "id": 1,
            "name": "Mock Organization"
        }
    ]

@app.get("/api/user")
async def get_current_user(_auth=verify_auth):
    """Get current user."""
    return {
        "id": 1,
        "login": "admin",
        "email": "admin@localhost",
        "name": "Admin User",
        "isGrafanaAdmin": True,
        "orgId": 1
    }

# ============================================================================
# Folder Endpoints
# ============================================================================

@app.get("/api/folders")
async def list_folders(_auth=verify_auth):
    """List all folders."""
    conn = get_connection()
    results = conn.execute("SELECT * FROM folders").fetchall()

    return [
        {
            "id": row[0],
            "uid": row[1],
            "title": row[2]
        }
        for row in results
    ]

@app.get("/api/folders/{uid}")
async def get_folder_by_uid(uid: str, _auth=verify_auth):
    """Get folder by UID."""
    conn = get_connection()
    result = conn.execute(
        "SELECT * FROM folders WHERE uid = ?",
        [uid]
    ).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail=f"Folder not found: {uid}")

    return {
        "id": result[0],
        "uid": result[1],
        "title": result[2]
    }

# ============================================================================
# Alert Endpoints
# ============================================================================

@app.get("/api/alerts")
async def list_alerts(_auth=verify_auth):
    """List all alerts."""
    return []  # Simplified - no alerts in mock

@app.get("/api/alerts/{alert_id}")
async def get_alert_by_id(alert_id: int, _auth=verify_auth):
    """Get alert by ID."""
    raise HTTPException(status_code=404, detail=f"Alert not found: {alert_id}")

# ============================================================================
# Utility Endpoints
# ============================================================================

@app.get("/api/auth/keys")
async def get_api_keys(_auth=verify_auth):
    """List API keys."""
    return []  # Simplified

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
