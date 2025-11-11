# PostHog Driver - Complete Project Blueprint

Following the **e2b_mockup sandbox-isolated, discovery-first execution pattern**

---

## Project Structure

```
posthog_mockup/
├── posthog_driver/              # Main driver implementation
│   ├── __init__.py
│   ├── client.py                # PostHogClient class
│   ├── exceptions.py            # Custom exception hierarchy
│   ├── README.md
│   └── examples/
│       ├── basic_events.py
│       ├── user_analysis.py
│       ├── funnel_analysis.py
│       └── feature_flags.py
│
├── mock_api/                    # FastAPI mock server
│   ├── __init__.py
│   ├── main.py                  # FastAPI app with endpoints
│   ├── db.py                    # DuckDB connection manager
│   ├── query_parser.py          # PostHog query parser
│   └── requirements.txt
│
├── test_data/                   # Test database setup
│   ├── posthog_test.db          # DuckDB database file
│   └── setup.py                 # Database population script
│
├── agent_executor.py            # E2B orchestration
├── script_templates.py          # Pre-built script patterns
├── test_scenarios/              # Test cases
│   ├── test_events.py
│   ├── test_users.py
│   ├── test_cohorts.py
│   └── run_all_scenarios.py
│
├── web_ui/                      # Optional web interface
│   ├── app.py
│   └── static/
│
├── requirements.txt
├── README.md
└── .env.example
```

---

## 1. PostHog Driver Client (`posthog_driver/client.py`)

### Core Methods (Following PostHog API Structure)

```python
class PostHogClient:
    """
    PostHog API driver for event tracking and analytics

    Implements sandbox-isolated, discovery-first pattern
    """

    def __init__(self, api_url=None, api_key=None, project_id=None, timeout=30):
        """
        Initialize PostHog client

        Args:
            api_url: PostHog API endpoint (default: localhost:8000)
            api_key: Personal API key for authentication
            project_id: Project/Team ID
            timeout: Request timeout in seconds
        """

    # === DISCOVERY METHODS ===

    def list_projects(self) -> List[Dict]:
        """
        Enumerate available projects/teams
        Endpoint: GET /api/projects/
        Returns: [{'id': 1, 'name': 'My Project', ...}]
        """

    def get_event_definitions(self) -> List[Dict]:
        """
        List all event types with metadata
        Endpoint: GET /api/projects/{project_id}/event_definitions/
        Returns: [{'name': '$pageview', 'volume_30_day': 1000, ...}]
        """

    def get_property_definitions(self, type='event') -> List[Dict]:
        """
        List property definitions
        Args:
            type: 'event', 'person', or 'group'
        Endpoint: GET /api/projects/{project_id}/property_definitions/
        Returns: [{'name': 'browser', 'type': 'String', ...}]
        """

    def get_cohorts(self) -> List[Dict]:
        """
        List user cohorts
        Endpoint: GET /api/projects/{project_id}/cohorts/
        Returns: [{'id': 1, 'name': 'Active Users', 'count': 500}]
        """

    # === QUERY METHODS ===

    def query_events(self, filters: Dict, limit=100) -> List[Dict]:
        """
        Query events with filters

        Args:
            filters: {
                'event': 'event_name',
                'properties': {'key': 'value'},
                'date_from': '2024-01-01',
                'date_to': '2024-12-31'
            }
            limit: Max results

        Endpoint: POST /api/projects/{project_id}/events/
        Returns: [{'event': '$pageview', 'timestamp': '...', ...}]
        """

    def get_persons(self, filters: Dict = None, limit=100) -> List[Dict]:
        """
        Query persons (users)

        Args:
            filters: {
                'properties': {'key': 'value'},
                'cohort': 1
            }

        Endpoint: GET /api/projects/{project_id}/persons/
        Returns: [{'distinct_id': 'user123', 'properties': {...}}]
        """

    def get_insights(self, query: Dict) -> Dict:
        """
        Execute insight query (trends, funnels, retention, etc.)

        Args:
            query: {
                'kind': 'TrendsQuery',  # or FunnelsQuery, RetentionQuery
                'series': [...],
                'dateRange': {...}
            }

        Endpoint: POST /api/projects/{project_id}/query/
        Returns: Insight results with aggregations
        """

    def get_feature_flags(self) -> List[Dict]:
        """
        List feature flags
        Endpoint: GET /api/projects/{project_id}/feature_flags/
        Returns: [{'key': 'new-ui', 'active': true, 'filters': {...}}]
        """

    # === ANALYTICS HELPERS ===

    def get_event_count(self, event_name: str, date_from=None, date_to=None) -> int:
        """Quick count of specific event"""

    def get_active_users(self, date_from=None, date_to=None) -> int:
        """Count distinct active users"""

    def get_funnel_conversion(self, steps: List[str]) -> Dict:
        """Calculate funnel conversion rates"""

    # === LIFECYCLE ===

    def close(self):
        """Close HTTP session"""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
```

### Exception Hierarchy (`posthog_driver/exceptions.py`)

```python
class PostHogError(Exception):
    """Base exception for PostHog client errors"""
    pass

class ConnectionError(PostHogError):
    """API server unreachable, network issues"""
    pass

class AuthError(PostHogError):
    """Invalid API key or project access denied"""
    pass

class ProjectNotFoundError(PostHogError):
    """Non-existent project ID"""
    pass

class QueryError(PostHogError):
    """Invalid query structure or parameters"""
    pass

class RateLimitError(PostHogError):
    """API rate limit exceeded"""
    pass
```

---

## 2. Mock API Server (`mock_api/main.py`)

### FastAPI Endpoints

```python
from fastapi import FastAPI, HTTPException, Query
from typing import Optional, List, Dict
import uvicorn

app = FastAPI(title="PostHog Mock API")

# === PROJECT DISCOVERY ===

@app.get("/api/projects/")
async def list_projects():
    """Return available projects"""
    return {
        "results": [
            {"id": 1, "name": "Production", "uuid": "proj-123"},
            {"id": 2, "name": "Staging", "uuid": "proj-456"}
        ]
    }

@app.get("/api/projects/{project_id}/event_definitions/")
async def get_event_definitions(project_id: int):
    """List all event types"""
    # Query DuckDB for distinct events
    return {
        "results": [
            {
                "name": "$pageview",
                "volume_30_day": 1500,
                "query_usage_30_day": 25
            },
            {
                "name": "signup_completed",
                "volume_30_day": 42,
                "query_usage_30_day": 10
            }
        ]
    }

@app.get("/api/projects/{project_id}/property_definitions/")
async def get_property_definitions(
    project_id: int,
    type: str = Query("event", regex="^(event|person|group)$")
):
    """List property definitions by type"""
    return {
        "results": [
            {"name": "browser", "type": "String", "is_numerical": False},
            {"name": "screen_width", "type": "Numeric", "is_numerical": True}
        ]
    }

# === EVENTS ===

@app.post("/api/projects/{project_id}/events/")
async def query_events(project_id: int, filters: Dict):
    """
    Query events with filters

    Request body:
    {
        "event": "event_name",
        "properties": {"key": "value"},
        "date_from": "2024-01-01",
        "date_to": "2024-12-31",
        "limit": 100
    }
    """
    # Parse filters and query DuckDB
    # Convert to SQL WHERE clause
    return {
        "results": [...],
        "next": None
    }

# === PERSONS ===

@app.get("/api/projects/{project_id}/persons/")
async def get_persons(
    project_id: int,
    properties: Optional[str] = None,
    cohort: Optional[int] = None,
    limit: int = 100
):
    """Query persons with filters"""
    return {
        "results": [
            {
                "distinct_id": "user_123",
                "properties": {
                    "email": "user@example.com",
                    "name": "John Doe"
                },
                "created_at": "2024-01-01T00:00:00Z"
            }
        ]
    }

# === INSIGHTS / QUERIES ===

@app.post("/api/projects/{project_id}/query/")
async def execute_query(project_id: int, query: Dict):
    """
    Execute insight query

    Supports:
    - TrendsQuery: Event trends over time
    - FunnelsQuery: Multi-step conversion funnels
    - RetentionQuery: User retention analysis
    - PathsQuery: User journey paths
    """
    query_kind = query.get("kind")

    if query_kind == "TrendsQuery":
        # Execute trend aggregation
        return {
            "results": [
                {"label": "$pageview", "data": [10, 15, 20, 25]},
                {"label": "signup", "data": [2, 3, 5, 4]}
            ],
            "dates": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"]
        }

    elif query_kind == "FunnelsQuery":
        # Execute funnel calculation
        return {
            "results": [
                {"name": "Step 1", "count": 1000, "conversion_rate": 100},
                {"name": "Step 2", "count": 500, "conversion_rate": 50},
                {"name": "Step 3", "count": 250, "conversion_rate": 25}
            ]
        }

    # ... other query types

# === COHORTS ===

@app.get("/api/projects/{project_id}/cohorts/")
async def get_cohorts(project_id: int):
    """List user cohorts"""
    return {
        "results": [
            {"id": 1, "name": "Active Users", "count": 500},
            {"id": 2, "name": "Power Users", "count": 50}
        ]
    }

# === FEATURE FLAGS ===

@app.get("/api/projects/{project_id}/feature_flags/")
async def get_feature_flags(project_id: int):
    """List feature flags"""
    return {
        "results": [
            {
                "id": 1,
                "key": "new-dashboard",
                "active": True,
                "filters": {"groups": [{"rollout_percentage": 50}]}
            }
        ]
    }

# === HEALTH ===

@app.get("/health")
async def health_check():
    """Verify API and database are running"""
    return {"status": "ok", "project_count": 2}
```

---

## 3. Database Setup (`test_data/setup.py`)

### DuckDB Schema

```python
import duckdb

def setup_database(db_path="test_data/posthog_test.db"):
    """Create and populate PostHog test database"""

    conn = duckdb.connect(db_path)

    # === EVENTS TABLE ===
    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            uuid VARCHAR PRIMARY KEY,
            event VARCHAR NOT NULL,
            distinct_id VARCHAR NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            properties JSON,
            project_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # === PERSONS TABLE ===
    conn.execute("""
        CREATE TABLE IF NOT EXISTS persons (
            id VARCHAR PRIMARY KEY,
            distinct_id VARCHAR UNIQUE NOT NULL,
            properties JSON,
            created_at TIMESTAMP NOT NULL,
            project_id INTEGER NOT NULL
        )
    """)

    # === COHORTS TABLE ===
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cohorts (
            id INTEGER PRIMARY KEY,
            name VARCHAR NOT NULL,
            description TEXT,
            filters JSON,
            project_id INTEGER NOT NULL
        )
    """)

    # === COHORT MEMBERS ===
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cohort_members (
            cohort_id INTEGER,
            person_id VARCHAR,
            PRIMARY KEY (cohort_id, person_id)
        )
    """)

    # === FEATURE FLAGS ===
    conn.execute("""
        CREATE TABLE IF NOT EXISTS feature_flags (
            id INTEGER PRIMARY KEY,
            key VARCHAR NOT NULL,
            active BOOLEAN,
            filters JSON,
            project_id INTEGER NOT NULL
        )
    """)

    # Populate with test data
    populate_test_data(conn)

    conn.close()

def populate_test_data(conn):
    """Generate realistic PostHog test data"""

    # Insert 1000+ events
    events = [
        ('evt_001', '$pageview', 'user_123', '2024-11-01 10:00:00',
         '{"url": "/home", "browser": "Chrome"}', 1),
        ('evt_002', 'signup_completed', 'user_123', '2024-11-01 10:05:00',
         '{"plan": "pro"}', 1),
        # ... 1000 more events
    ]

    conn.executemany("""
        INSERT INTO events (uuid, event, distinct_id, timestamp, properties, project_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, events)

    # Insert 200 persons
    persons = [
        ('per_001', 'user_123', '{"email": "user@example.com", "name": "John"}',
         '2024-11-01 09:00:00', 1),
        # ... 200 more persons
    ]

    conn.executemany("""
        INSERT INTO persons (id, distinct_id, properties, created_at, project_id)
        VALUES (?, ?, ?, ?, ?)
    """, persons)

    # Insert cohorts and feature flags
    # ...
```

---

## 4. Agent Executor (`agent_executor.py`)

```python
from e2b_code_interpreter import Sandbox
import json

class PostHogAgentExecutor:
    """
    Orchestrates PostHog operations in E2B sandbox

    Lifecycle:
    1. Create sandbox
    2. Upload driver, API, database
    3. Start mock API server
    4. Execute discovery
    5. Run user scripts
    6. Clean up
    """

    def __init__(self, auto_setup=False):
        self.sandbox = None
        self.api_process = None
        self.schema_cache = {}

        if auto_setup:
            self.create_sandbox()
            self.upload_files()
            self.start_mock_api()
            self.run_discovery()

    def create_sandbox(self):
        """Create E2B cloud VM"""
        self.sandbox = Sandbox()
        return self.sandbox

    def upload_files(self):
        """Upload all components to sandbox"""
        # Upload posthog_driver/
        # Upload mock_api/
        # Upload test_data/posthog_test.db

    def start_mock_api(self):
        """Start FastAPI server on localhost:8000"""
        install_cmd = "pip install fastapi uvicorn duckdb"
        self.sandbox.run_code(install_cmd)

        start_cmd = """
cd /home/user/mock_api
uvicorn main:app --host 0.0.0.0 --port 8000 &
"""
        self.api_process = self.sandbox.run_code(start_cmd)

        # Verify with health check
        health = self.sandbox.run_code("""
import requests
print(requests.get('http://localhost:8000/health').json())
""")

    def run_discovery(self):
        """Cache project schema"""
        discovery_script = """
from posthog_driver.client import PostHogClient
import json

client = PostHogClient(
    api_url='http://localhost:8000',
    api_key='test_key',
    project_id=1
)

schema = {
    'events': client.get_event_definitions(),
    'properties': client.get_property_definitions(),
    'cohorts': client.get_cohorts()
}

print(json.dumps(schema))
"""
        result = self.sandbox.run_code(discovery_script)
        self.schema_cache = json.loads(result.stdout)

    def execute(self, request: str) -> Dict:
        """
        Main orchestration: natural language → results

        Args:
            request: "Show me pageview trends for last 7 days"

        Returns:
            {
                "success": True,
                "description": "Retrieved pageview trends",
                "data": {...},
                "output": "..."
            }
        """
        # 1. Parse request
        # 2. Generate script using templates
        # 3. Execute in sandbox
        # 4. Parse results
        # 5. Return structured response

    def execute_script(self, script: str) -> Dict:
        """Execute arbitrary Python script in sandbox"""
        result = self.sandbox.run_code(script)

        return {
            "success": result.error is None,
            "output": result.stdout,
            "error": result.error
        }

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.api_process:
            self.api_process.kill()
        if self.sandbox:
            self.sandbox.close()
```

---

## 5. Script Templates (`script_templates.py`)

```python
class PostHogScriptTemplates:
    """Pre-built script patterns for common operations"""

    @staticmethod
    def get_event_trends(event_name, days=7):
        return f'''
from posthog_driver.client import PostHogClient
from datetime import datetime, timedelta
import json

client = PostHogClient(
    api_url='http://localhost:8000',
    api_key='test_key',
    project_id=1
)

# Calculate date range
end_date = datetime.now()
start_date = end_date - timedelta(days={days})

# Query events
events = client.query_events({{
    'event': '{event_name}',
    'date_from': start_date.isoformat(),
    'date_to': end_date.isoformat()
}})

# Aggregate by date
from collections import Counter
by_date = Counter(e['timestamp'][:10] for e in events)

print(json.dumps({{
    'total': len(events),
    'by_date': dict(by_date)
}}))
'''

    @staticmethod
    def get_funnel_conversion(steps):
        return f'''
from posthog_driver.client import PostHogClient
import json

client = PostHogClient(
    api_url='http://localhost:8000',
    api_key='test_key',
    project_id=1
)

# Define funnel steps
steps = {steps}

# Execute funnel query
funnel = client.get_insights({{
    'kind': 'FunnelsQuery',
    'series': [
        {{'event': step}} for step in steps
    ],
    'funnelsFilter': {{
        'funnelWindowInterval': 7,
        'funnelWindowIntervalUnit': 'day'
    }}
}})

print(json.dumps(funnel))
'''

    @staticmethod
    def get_active_users(cohort_id=None):
        return f'''
from posthog_driver.client import PostHogClient
import json

client = PostHogClient(
    api_url='http://localhost:8000',
    api_key='test_key',
    project_id=1
)

filters = {{}}
{f"filters['cohort'] = {cohort_id}" if cohort_id else ""}

persons = client.get_persons(filters=filters)

print(json.dumps({{
    'total': len(persons),
    'sample': persons[:10]
}}))
'''
```

---

## 6. Key Configuration Files

### `requirements.txt`
```
requests>=2.31.0
python-dotenv>=1.0.0
fastapi>=0.104.0
uvicorn>=0.24.0
duckdb>=0.9.0
e2b-code-interpreter>=0.0.8
pydantic>=2.5.0
```

### `.env.example`
```
POSTHOG_API_URL=http://localhost:8000
POSTHOG_API_KEY=phc_test_key_12345
POSTHOG_PROJECT_ID=1
E2B_API_KEY=your_e2b_key_here
```

---

## 7. Implementation Checklist

### Phase 1: Core Driver
- [ ] Create `posthog_driver/client.py` with all methods
- [ ] Implement exception hierarchy
- [ ] Add context manager support
- [ ] Write comprehensive docstrings

### Phase 2: Mock API
- [ ] Create FastAPI endpoints (7+ routes)
- [ ] Implement query parser for PostHog filters
- [ ] Set up DuckDB connection manager
- [ ] Add request validation

### Phase 3: Database
- [ ] Design schema (5 tables minimum)
- [ ] Create setup script
- [ ] Generate 1000+ test records
- [ ] Add realistic event/user data

### Phase 4: Orchestration
- [ ] Implement `PostHogAgentExecutor`
- [ ] Add sandbox lifecycle management
- [ ] Create discovery workflow
- [ ] Build result parsing

### Phase 5: Templates & Examples
- [ ] Create 6+ script templates
- [ ] Write 10+ usage examples
- [ ] Add test scenarios
- [ ] Create documentation

### Phase 6: Testing
- [ ] Unit tests for driver methods
- [ ] Integration tests with mock API
- [ ] E2E tests with sandbox
- [ ] Error handling tests

---

## 8. PostHog-Specific Considerations

### API Differences vs Salesforce
1. **Query Structure**: PostHog uses JSON queries, not SOQL
2. **Time-Series Focus**: Heavy emphasis on date ranges and aggregations
3. **Real-Time Data**: Events stream continuously
4. **Complex Insights**: Funnels, retention, paths require special handling

### Driver Advantages
- **Unified Interface**: Hide PostHog API complexity
- **Type Safety**: Validate query structures
- **Error Handling**: Graceful degradation
- **Testing**: Mock data without API costs
- **Iteration Speed**: Local development without cloud dependencies

### Discovery-First Workflow
```python
# 1. Discover available events
events = client.get_event_definitions()
# Returns: ['$pageview', 'signup', 'purchase', ...]

# 2. Discover properties
props = client.get_property_definitions()
# Returns: ['browser', 'country', 'plan', ...]

# 3. Validate query before execution
if '$pageview' in events:
    results = client.query_events({'event': '$pageview'})
```

---

## 9. Success Metrics

The PostHog driver project will be successful when:

1. ✅ All API methods work with mock data
2. ✅ Complete isolation in E2B sandbox
3. ✅ Discovery workflow prevents invalid queries
4. ✅ Script templates cover 80% of use cases
5. ✅ Comprehensive error messages guide debugging
6. ✅ Context managers ensure proper cleanup
7. ✅ Examples demonstrate real-world scenarios
8. ✅ Tests provide 90%+ code coverage

---

## Next Steps

1. **Start with Driver**: Implement `PostHogClient` class first
2. **Add Mock API**: Create FastAPI server with 3-4 endpoints
3. **Test Integration**: Verify driver → API → database flow
4. **Expand Coverage**: Add remaining endpoints and features
5. **Create Templates**: Build script generation patterns
6. **Add E2B**: Integrate sandbox orchestration
7. **Write Docs**: Comprehensive README and examples

---

This blueprint provides everything needed to build a production-ready PostHog driver following the proven e2b_mockup architecture!
