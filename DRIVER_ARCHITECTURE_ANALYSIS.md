# Driver Architecture Analysis - E2B Mockup Pattern

> **NOTE:** Foundation document analyzing Salesforce driver pattern. Contains Grafana examples
> (removed in V1). The patterns apply to PostHog and any API driver.

## Executive Summary

Analysis of the Salesforce driver implementation from `ng_component/examples/e2b_mockup` reveals a robust, resource-oriented client pattern suitable for migration to other API-based extractors (Grafana, PostHog). This document outlines the architecture, identifies migration opportunities, and proposes a generalized driver framework.

---

## Current Architecture Overview

### Core Pattern: Resource-Oriented Client with Session-Based HTTP

```
┌─────────────────────────────────────────────────┐
│           User Script / Agent Executor          │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│         SalesforceClient (Driver)               │
│  ┌───────────────────────────────────────────┐  │
│  │  Authentication Layer (API Key)           │  │
│  └───────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────┐  │
│  │  Request Abstraction (_make_request)     │  │
│  └───────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────┐  │
│  │  Resource Methods (query, list, get)     │  │
│  └───────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────┐  │
│  │  Exception Handling (Custom Exceptions)   │  │
│  └───────────────────────────────────────────┘  │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│         requests.Session                        │
│         (Persistent HTTP Connection)            │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│         Target API (Mock/Real Service)          │
└─────────────────────────────────────────────────┘
```

---

## Key Architectural Components

### 1. Authentication Layer

**Current Implementation (Salesforce):**
- API Key-based authentication
- Environment variable fallback (`SF_API_KEY`)
- `X-API-Key` header injection
- 401 detection → `AuthError`

**Generalization Opportunities:**
- Support multiple auth methods (API Key, OAuth2, Bearer Token)
- Pluggable auth strategies
- Token refresh mechanisms

### 2. Request Abstraction

**Current Implementation:**
```python
def _make_request(self, method, endpoint, **kwargs):
    url = self.base_url.rstrip('/') + '/' + endpoint.lstrip('/')
    response = self.session.request(method, url, **kwargs)
    # Error handling and JSON parsing
```

**Strengths:**
- Single point of control for all HTTP operations
- Consistent error handling
- Session reuse for connection pooling

**Migration Value:**
- Can be extracted to base class with minimal changes
- Supports RESTful patterns used by Grafana and PostHog

### 3. Exception Hierarchy

**Current Structure:**
```
SalesforceError (base)
├── ConnectionError
├── AuthError
├── ObjectNotFoundError
└── QueryError
```

**Generalization Strategy:**
- Rename base to `ExtractorError` or `DriverError`
- Keep subclasses generic: `ConnectionError`, `AuthError`, `ResourceNotFoundError`, `QueryError`
- Allow driver-specific extensions

### 4. Resource Methods

**Current Salesforce-Specific Methods:**
- `list_objects()` - List available Salesforce objects
- `get_fields(object_name)` - Get object schema
- `query(soql)` - Execute SOQL query
- `get_object_count(object_name)` - Count records

**Pattern Recognition:**
These follow a common REST pattern:
- **Discovery**: What resources are available?
- **Schema**: What fields/structure do resources have?
- **Query**: How do I retrieve data?
- **Metadata**: What are the resource characteristics?

---

## Migration Framework Design

### Base Driver Component

```python
class BaseAPIDriver:
    """
    Generalized driver for API-based data extraction.

    Provides:
    - Session management
    - Authentication handling
    - Request abstraction
    - Error handling
    - Context manager support
    """

    def __init__(self, base_url, auth_config, timeout=30):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        self._setup_auth(auth_config)

    def _setup_auth(self, auth_config):
        """Configure authentication based on strategy"""

    def _make_request(self, method, endpoint, **kwargs):
        """Abstract HTTP request handling"""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
```

### Driver-Specific Implementations

Each extractor inherits and implements:
- **Discovery methods**: Resource enumeration
- **Schema methods**: Metadata retrieval
- **Query methods**: Data extraction
- **Transformation methods**: Format standardization

---

## Grafana Extractor Design

### API Characteristics
- **Base URL**: `https://<instance>.grafana.net/api`
- **Auth**: Bearer Token or API Key
- **Key Endpoints**:
  - `/datasources` - List data sources
  - `/dashboards/uid/{uid}` - Get dashboard
  - `/search` - Search dashboards/folders
  - `/annotations` - Query annotations

### Driver Methods

```python
class GrafanaDriver(BaseAPIDriver):
    def list_datasources(self):
        """GET /datasources"""

    def get_dashboard(self, uid):
        """GET /dashboards/uid/{uid}"""

    def search(self, query, type='dash-db'):
        """GET /search"""

    def get_annotations(self, from_time, to_time, **filters):
        """GET /annotations"""
```

### Authentication Strategy
- API Key: `Authorization: Bearer <token>`
- Support for Grafana Cloud and self-hosted instances

---

## PostHog Extractor Design

### API Characteristics
- **Base URL**: `https://app.posthog.com/api` or self-hosted
- **Auth**: Personal API Key
- **Key Endpoints**:
  - `/projects` - List projects
  - `/events` - Query events
  - `/insights` - Get insights/analytics
  - `/feature_flags` - List feature flags

### Driver Methods

```python
class PostHogDriver(BaseAPIDriver):
    def list_projects(self):
        """GET /projects"""

    def query_events(self, event_name, date_from, date_to, **filters):
        """GET /events with filtering"""

    def get_insights(self, insight_id):
        """GET /insights/{id}"""

    def list_feature_flags(self, project_id):
        """GET /projects/{id}/feature_flags"""
```

### Authentication Strategy
- Header: `Authorization: Bearer <personal_api_key>`
- Project-scoped queries require project ID

---

## Sandbox Integration Pattern

### Current Agent Executor Flow

```
1. Create E2B Sandbox
2. Upload Mock API + Driver
3. Start API Service (uvicorn)
4. Generate execution script
5. Run script in sandbox
6. Parse results
```

### Migration Considerations

**Unified Driver Upload:**
- Package base driver + specific drivers
- Upload to sandbox filesystem
- Ensure importability via sys.path

**Template Generation:**
- Extend script_templates.py for Grafana/PostHog
- Map common operations (list, query, export)
- Handle pagination and rate limiting

**Mock API Extension:**
- Create Grafana mock endpoints
- Create PostHog mock endpoints
- Reuse DuckDB backend pattern

---

## Implementation Roadmap

### Phase 1: Base Driver Extraction
- [ ] Extract common patterns from SalesforceClient
- [ ] Create BaseAPIDriver with auth strategies
- [ ] Implement generalized exception hierarchy
- [ ] Add comprehensive tests

### Phase 2: Grafana Driver
- [ ] Implement GrafanaDriver(BaseAPIDriver)
- [ ] Add Grafana-specific methods
- [ ] Create mock Grafana API
- [ ] Add script templates
- [ ] Test in sandbox environment

### Phase 3: PostHog Driver
- [ ] Implement PostHogDriver(BaseAPIDriver)
- [ ] Add PostHog-specific methods
- [ ] Create mock PostHog API
- [ ] Add script templates
- [ ] Test in sandbox environment

### Phase 4: Agent Integration
- [ ] Extend agent_executor.py for multi-driver support
- [ ] Add driver selection logic
- [ ] Update prompt handling
- [ ] Comprehensive integration tests

---

## Key Benefits of Migration

1. **Code Reusability**: 60-70% of driver code can be shared
2. **Consistency**: Uniform error handling and patterns
3. **Maintainability**: Single point for common features
4. **Extensibility**: Easy to add new extractors
5. **Testability**: Shared test utilities and mocks

---

## Comparison Matrix

| Feature | Salesforce | Grafana | PostHog | Generalization |
|---------|-----------|---------|---------|----------------|
| Auth Method | API Key | Bearer Token | Personal API Key | Pluggable Auth |
| Main Resource | Objects | Dashboards | Events | Resource Interface |
| Query Language | SOQL | N/A | Filter API | Query Abstraction |
| Pagination | Cursor | Page/Limit | Offset | Pagination Strategy |
| Rate Limiting | Yes | Yes | Yes | Retry/Backoff Logic |

---

## Conclusion

The current Salesforce driver provides an excellent foundation for a generalized extractor framework. By extracting common patterns into a base class and implementing driver-specific methods for Grafana and PostHog, we can create a maintainable, scalable extraction architecture that works seamlessly with the E2B sandbox environment.

The key to successful migration is identifying the universal patterns (auth, requests, errors) while allowing flexibility for API-specific behaviors (query languages, resource models, response formats).
