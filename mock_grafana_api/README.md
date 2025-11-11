# Mock Grafana API

A FastAPI-based mock implementation of the Grafana API for testing and development in E2B sandboxes.

## Features

- **In-Memory DuckDB Database**: Fast, ephemeral data storage
- **Realistic Sample Data**: Pre-loaded dashboards, datasources, and annotations
- **Complete API Coverage**: All endpoints used by GrafanaDriver
- **No External Dependencies**: Runs entirely in sandbox

## Endpoints Implemented

### Health & Status
- `GET /api/health` - Health check

### Dashboards
- `GET /api/search` - Search dashboards/folders
- `GET /api/dashboards/uid/{uid}` - Get dashboard by UID
- `GET /api/dashboards/home` - Get home dashboard

### Data Sources
- `GET /api/datasources` - List all data sources
- `GET /api/datasources/{id}` - Get by ID
- `GET /api/datasources/name/{name}` - Get by name
- `GET /api/datasources/uid/{uid}` - Get by UID

### Annotations
- `GET /api/annotations` - Query annotations
- `POST /api/annotations` - Create annotation

### Organizations & Users
- `GET /api/org` - Current organization
- `GET /api/orgs` - List organizations
- `GET /api/user` - Current user

### Folders
- `GET /api/folders` - List folders
- `GET /api/folders/{uid}` - Get folder by UID

### Alerts
- `GET /api/alerts` - List alerts (empty in mock)
- `GET /api/alerts/{id}` - Get alert by ID

## Sample Data

The mock API comes preloaded with:

**Folders:**
- General
- Monitoring
- Business Metrics

**Data Sources:**
- Prometheus (default)
- PostgreSQL
- Loki

**Dashboards:**
1. **System Overview** (starred)
   - CPU Usage panel
   - Memory Usage panel
   - Tags: system, production

2. **API Metrics**
   - Request Rate panel
   - Error Rate panel
   - Response Time (p95) panel
   - Tags: api, production, http

3. **Sales Dashboard** (starred)
   - Total Revenue stat
   - Orders Today stat
   - Tags: business, sales

4. **Database Monitoring**
   - Query Performance panel
   - Tags: database, postgres, production

**Annotations:**
- Deployment events
- Incidents
- Maintenance windows
- Business events

## Installation

```bash
pip install fastapi uvicorn duckdb
```

## Running

### Standalone
```bash
cd mock_grafana_api
uvicorn main:app --host 0.0.0.0 --port 8000
```

### In E2B Sandbox
```python
# Upload files to sandbox
sandbox.upload_file("mock_grafana_api/main.py", "/home/user/mock_grafana_api/main.py")
sandbox.upload_file("mock_grafana_api/db.py", "/home/user/mock_grafana_api/db.py")
sandbox.upload_file("mock_grafana_api/fixtures.py", "/home/user/mock_grafana_api/fixtures.py")

# Start server in background
process = sandbox.process.start(
    "cd /home/user/mock_grafana_api && uvicorn main:app --host 0.0.0.0 --port 8000"
)
```

## Testing with GrafanaDriver

```python
from grafana_driver import GrafanaDriver
from base_driver import AuthConfig, AuthStrategy

# Point driver to mock API
auth = AuthConfig(AuthStrategy.BEARER_TOKEN, {'token': 'any-token'})
driver = GrafanaDriver('http://localhost:8000', auth)

# Test endpoints
dashboards = driver.search_dashboards()
print(f"Found {len(dashboards)} dashboards")

dashboard = driver.get_dashboard_by_uid('system-overview')
print(f"Dashboard: {dashboard['dashboard']['title']}")

datasources = driver.list_datasources()
print(f"Data sources: {[ds['name'] for ds in datasources]}")
```

## Authentication

The mock API accepts any Bearer token. No validation is performed.

```bash
curl -H "Authorization: Bearer any-token" http://localhost:8000/api/health
```

## Database Schema

### Dashboards
```sql
CREATE TABLE dashboards (
    id INTEGER PRIMARY KEY,
    uid VARCHAR NOT NULL UNIQUE,
    title VARCHAR NOT NULL,
    tags VARCHAR,  -- JSON array
    starred BOOLEAN,
    folder_id INTEGER,
    folder_uid VARCHAR,
    folder_title VARCHAR,
    json_model VARCHAR NOT NULL,  -- Full dashboard JSON
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    version INTEGER
)
```

### Data Sources
```sql
CREATE TABLE datasources (
    id INTEGER PRIMARY KEY,
    uid VARCHAR NOT NULL UNIQUE,
    name VARCHAR NOT NULL,
    type VARCHAR NOT NULL,
    url VARCHAR,
    access VARCHAR,
    is_default BOOLEAN,
    json_data VARCHAR  -- Additional config as JSON
)
```

### Annotations
```sql
CREATE TABLE annotations (
    id INTEGER PRIMARY KEY,
    dashboard_id INTEGER,
    panel_id INTEGER,
    time BIGINT NOT NULL,  -- Unix timestamp (ms)
    time_end BIGINT,
    text VARCHAR NOT NULL,
    tags VARCHAR  -- JSON array
)
```

### Folders
```sql
CREATE TABLE folders (
    id INTEGER PRIMARY KEY,
    uid VARCHAR NOT NULL UNIQUE,
    title VARCHAR NOT NULL
)
```

## Extending

To add more sample data, edit `fixtures.py`:

```python
def load_fixtures():
    conn = get_connection()

    # Add your custom dashboards
    conn.execute(
        "INSERT INTO dashboards (...) VALUES (...)"
    )
```

## Limitations

- No persistent storage (data resets on restart)
- No user/permission management
- No actual data source querying
- Simplified search and filtering
- No dashboard creation/update (read-only except annotations)

## Use Cases

1. **Development**: Test driver without Grafana instance
2. **CI/CD**: Run integration tests
3. **Demos**: Show functionality without credentials
4. **E2B Sandboxes**: Isolated testing environment
