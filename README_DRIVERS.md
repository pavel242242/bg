# API Driver Migration Framework

A simple but capable driver framework for API-based data extraction, featuring implementations for Grafana and PostHog.

## Overview

This framework provides a generalized base driver component that handles:
- Session management with connection pooling
- Pluggable authentication strategies
- Request abstraction with comprehensive error handling
- Pagination support for large datasets
- Context manager support for resource cleanup

## Architecture

```
base_driver.py          # Base driver framework and utilities
├── BaseAPIDriver       # Core driver with session management
├── PaginatedDriver     # Extended driver with pagination
├── AuthConfig          # Authentication configuration
└── Exception Hierarchy # Consistent error handling

grafana_driver.py       # Grafana API implementation
└── GrafanaDriver       # Dashboards, data sources, annotations

posthog_driver.py       # PostHog API implementation
└── PostHogDriver       # Events, insights, feature flags
```

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### Grafana Driver

```python
from grafana_driver import GrafanaDriver

# Using environment variable (GRAFANA_TOKEN)
driver = GrafanaDriver.from_env('https://my-instance.grafana.net')

# List dashboards
dashboards = driver.search_dashboards()
for dash in dashboards:
    print(f"{dash['title']} - {dash['uid']}")

# Export specific dashboard
dashboard = driver.export_dashboard('dashboard-uid')

# Query annotations
from datetime import datetime, timedelta
annotations = driver.get_annotations(
    from_time=datetime.now() - timedelta(days=7),
    to_time=datetime.now()
)

driver.close()
```

### PostHog Driver

```python
from posthog_driver import PostHogDriver

# Using environment variables (POSTHOG_API_KEY, POSTHOG_PROJECT_ID)
driver = PostHogDriver.from_env()

# Get event definitions
events = driver.get_event_definitions()
for event in events:
    print(f"{event['name']}: {event['volume_30_day']} events/month")

# Query events
pageviews = driver.query_events(
    event='$pageview',
    date_from=datetime.now() - timedelta(days=7)
)

# List feature flags
flags = driver.list_feature_flags()

driver.close()
```

## Authentication

### Grafana

Set environment variable:
```bash
export GRAFANA_TOKEN="glsa_your_token_here"
```

Or use explicit configuration:
```python
from base_driver import AuthConfig, AuthStrategy

auth = AuthConfig(
    AuthStrategy.BEARER_TOKEN,
    {'token': 'glsa_your_token_here'}
)
driver = GrafanaDriver('https://my-instance.grafana.net', auth)
```

### PostHog

Set environment variables:
```bash
export POSTHOG_API_KEY="phc_your_key_here"
export POSTHOG_PROJECT_ID="12345"
```

Or use explicit configuration:
```python
auth = AuthConfig(
    AuthStrategy.BEARER_TOKEN,
    {'token': 'phc_your_key_here'}
)
driver = PostHogDriver('https://app.posthog.com', auth, project_id=12345)
```

## Context Manager Usage

Both drivers support context managers for automatic resource cleanup:

```python
with GrafanaDriver.from_env('https://my-instance.grafana.net') as driver:
    dashboards = driver.search_dashboards()
    # Process dashboards...
# Session automatically closed
```

## Error Handling

The framework provides a comprehensive exception hierarchy:

```python
from base_driver import (
    DriverError,           # Base exception
    ConnectionError,       # Network issues
    AuthError,            # Authentication failures
    ResourceNotFoundError, # 404 errors
    QueryError,           # Query failures
    RateLimitError        # Rate limiting
)

try:
    driver = GrafanaDriver.from_env('https://my-instance.grafana.net')
    dashboard = driver.get_dashboard_by_uid('some-uid')

except ResourceNotFoundError as e:
    print(f"Dashboard not found: {e}")

except AuthError as e:
    print(f"Authentication failed: {e}")
    print("Check your API token")

except ConnectionError as e:
    print(f"Network error: {e}")

except DriverError as e:
    print(f"General error: {e}")

finally:
    driver.close()
```

## Features

### Grafana Driver

**Dashboard Operations:**
- `search_dashboards()` - Search with filters
- `get_dashboard_by_uid()` - Get specific dashboard
- `export_dashboard()` - Export JSON model
- `export_all_dashboards()` - Bulk export

**Data Source Operations:**
- `list_datasources()` - List all data sources
- `get_datasource_by_id()` - Get by ID
- `get_datasource_by_name()` - Get by name
- `query_datasource()` - Direct query

**Annotation Operations:**
- `get_annotations()` - Query with filters
- `create_annotation()` - Create new

**Organization & User:**
- `get_current_org()` - Current organization
- `get_current_user()` - User profile
- `list_orgs()` - All organizations

**Folder & Alert Operations:**
- `list_folders()` - List folders
- `search_folders()` - Search folders
- `list_alerts()` - List alerts
- `get_alert_by_id()` - Get alert details

### PostHog Driver

**Project Operations:**
- `list_projects()` - List accessible projects
- `get_project()` - Get project details

**Event Operations:**
- `query_events()` - Query with filters
- `get_event_definitions()` - All event types
- `get_event_properties()` - Event property metadata

**Insight Operations:**
- `list_insights()` - Saved insights
- `get_insight()` - Specific insight
- `query_insight()` - Ad-hoc query

**Dashboard Operations:**
- `list_dashboards()` - All dashboards
- `get_dashboard()` - Specific dashboard with tiles

**Feature Flag Operations:**
- `list_feature_flags()` - All flags
- `get_feature_flag()` - Specific flag
- `evaluate_feature_flag()` - Evaluate for user

**Cohort Operations:**
- `list_cohorts()` - All cohorts
- `get_cohort()` - Specific cohort

**Person Operations:**
- `list_persons()` - User list
- `get_person()` - Specific user
- `get_person_properties()` - Property definitions

**Session Recording Operations:**
- `list_session_recordings()` - Recording metadata
- `get_session_recording()` - Specific recording

**Experiment Operations:**
- `list_experiments()` - All experiments
- `get_experiment()` - Experiment results

## Pagination

The framework supports automatic pagination for large datasets:

```python
from base_driver import PaginationStrategy

# Automatic pagination through events
for event in driver._paginate(
    endpoint='events',
    strategy=PaginationStrategy.OFFSET_LIMIT,
    page_size=100,
    max_pages=10
):
    process_event(event)
```

## Advanced Usage

### Custom Authentication Strategies

```python
from base_driver import AuthConfig, AuthStrategy

# API Key authentication
auth = AuthConfig(
    AuthStrategy.API_KEY,
    {'api_key': 'your-key'},
    header_name='X-Custom-API-Key'
)

# Basic authentication
auth = AuthConfig(
    AuthStrategy.BASIC_AUTH,
    {'username': 'user', 'password': 'pass'}
)

# OAuth2
auth = AuthConfig(
    AuthStrategy.OAUTH2,
    {'access_token': 'token'}
)
```

### SSL Configuration

```python
driver = GrafanaDriver(
    base_url='https://my-instance.grafana.net',
    auth_config=auth,
    verify_ssl=False,  # Disable SSL verification (not recommended)
    timeout=60         # Custom timeout
)
```

### Multi-Driver Operations

```python
# Correlate monitoring and analytics data
with GrafanaDriver.from_env('https://grafana.net') as grafana, \
     PostHogDriver.from_env() as posthog:

    # Get Grafana incidents
    incidents = grafana.get_annotations(
        tags=['incident'],
        from_time=datetime.now() - timedelta(days=7)
    )

    # Check corresponding user behavior in PostHog
    for incident in incidents:
        events = posthog.query_events(
            date_from=incident['time'],
            date_to=incident['timeEnd']
        )
        # Analyze correlation...
```

## Testing

See `example_usage.py` for comprehensive examples of all features.

```bash
# Set environment variables
export GRAFANA_TOKEN="your-token"
export POSTHOG_API_KEY="your-key"
export POSTHOG_PROJECT_ID="12345"

# Run examples
python example_usage.py
```

## Extending the Framework

To create a new driver for another API:

1. **Inherit from BaseAPIDriver or PaginatedDriver:**

```python
from base_driver import PaginatedDriver, AuthConfig

class MyAPIDriver(PaginatedDriver):
    def __init__(self, base_url, auth_config, timeout=30):
        super().__init__(base_url, auth_config, timeout)

    def test_connection(self):
        # Implement connection test
        response = self._get('health')
        return response.get('status') == 'ok'
```

2. **Implement resource-specific methods:**

```python
    def list_resources(self):
        """List all resources."""
        return self._get('resources')

    def get_resource(self, resource_id):
        """Get specific resource."""
        return self._get(f'resources/{resource_id}')

    def query_data(self, filters):
        """Query with filters."""
        return self._post('query', json=filters)
```

3. **Handle API-specific errors:**

```python
    def _make_request(self, method, endpoint, **kwargs):
        try:
            return super()._make_request(method, endpoint, **kwargs)
        except DriverError as e:
            # Handle API-specific error codes
            if 'custom_error' in str(e):
                raise QueryError(f"Custom error: {e}")
            raise
```

## Migration from Salesforce Driver Pattern

This framework is based on the Salesforce driver pattern from the e2b_mockup project. Key improvements:

1. **Generalized Authentication:** Support for multiple auth strategies
2. **Pagination Support:** Built-in pagination for large datasets
3. **Enhanced Error Handling:** More granular exception types
4. **Resource-Oriented Design:** Consistent patterns across drivers
5. **Context Manager Support:** Automatic cleanup
6. **Extensibility:** Easy to add new drivers

## Documentation

For detailed architecture analysis, see:
- `DRIVER_ARCHITECTURE_ANALYSIS.md` - Comprehensive architecture documentation
- `example_usage.py` - Working examples for all features

## License

See main repository license.

## Contributing

To add a new driver:
1. Inherit from `BaseAPIDriver` or `PaginatedDriver`
2. Implement `test_connection()` method
3. Add resource-specific methods following REST patterns
4. Add examples to `example_usage.py`
5. Update this README with API-specific documentation
