# PostHog API Driver

A simple but capable driver framework for PostHog API-based data extraction.

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

posthog_driver.py       # PostHog API implementation
└── PostHogDriver       # Events, insights, feature flags, cohorts
```

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### PostHog Driver

```python
from posthog_driver import PostHogDriver
from datetime import datetime, timedelta

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

# List cohorts
cohorts = driver.list_cohorts()

driver.close()
```

## Authentication

### PostHog

Set environment variables:
```bash
export POSTHOG_API_KEY="phc_your_key_here"
export POSTHOG_PROJECT_ID="12345"
```

Or use explicit configuration:
```python
from base_driver import AuthConfig, AuthStrategy

auth = AuthConfig(
    AuthStrategy.BEARER_TOKEN,
    {'token': 'phc_your_key_here'}
)
driver = PostHogDriver('https://app.posthog.com', auth, project_id=12345)
```

## Context Manager Usage

The driver supports context managers for automatic resource cleanup:

```python
with PostHogDriver.from_env() as driver:
    events = driver.get_event_definitions()
    # Process events...
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
    driver = PostHogDriver.from_env()
    events = driver.query_events(event='$pageview')

except ResourceNotFoundError as e:
    print(f"Resource not found: {e}")

except AuthError as e:
    print(f"Authentication failed: {e}")
    print("Check your API key")

except ConnectionError as e:
    print(f"Network error: {e}")

except DriverError as e:
    print(f"General error: {e}")

finally:
    driver.close()
```

## Features

### PostHog Driver

**Project Operations:**
- `list_projects()` - List accessible projects
- `get_project()` - Get project details

**Event Operations:**
- `query_events()` - Query with filters (date range, event name, properties)
- `get_event_definitions()` - All event types with volume metrics
- `get_event_properties()` - Event property metadata

**Insight Operations:**
- `list_insights()` - Saved insights
- `get_insight()` - Specific insight
- `query_insight()` - Ad-hoc query (trends, funnels, etc.)

**Dashboard Operations:**
- `list_dashboards()` - All dashboards
- `get_dashboard()` - Specific dashboard with tiles

**Feature Flag Operations:**
- `list_feature_flags()` - All flags
- `get_feature_flag()` - Specific flag
- `evaluate_feature_flag()` - Evaluate for user

**Cohort Operations:**
- `list_cohorts()` - All cohorts (user segments)
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
driver = PostHogDriver(
    base_url='https://app.posthog.com',
    auth_config=auth,
    project_id=12345,
    verify_ssl=False,  # Disable SSL verification (not recommended)
    timeout=60         # Custom timeout
)
```

## Testing

See `example_usage.py` for comprehensive examples of all features.

```bash
# Set environment variables
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

For detailed information, see:
- `DRIVER_ARCHITECTURE_ANALYSIS.md` - Comprehensive architecture documentation
- `driver_recipes.py` - Common PostHog analysis patterns
- `example_usage.py` - Working examples for all features
- `V1_PLAN_REFINED.md` - Implementation plan and use cases

## E2B Integration

This driver is designed to run in E2B sandboxes with Claude Agent SDK:

```python
# Claude Agent SDK code (in E2B sandbox):
from posthog_driver import PostHogDriver

driver = PostHogDriver.from_env('http://localhost:8001')  # Mock API
events = driver.query_events(event='$pageview', limit=10)

# Or extend the driver:
class CustomPostHogDriver(PostHogDriver):
    def find_power_users(self, action, frequency=5):
        # Custom analysis method
        pass
```

See `CORRECT_ARCHITECTURE.md` for details on Claude Agent SDK integration patterns.

## License

See main repository license.

## Contributing

To add features to the PostHog driver:
1. Implement new methods in `posthog_driver.py`
2. Follow the existing patterns (resource-oriented, error handling)
3. Add examples to `example_usage.py`
4. Add recipes to `driver_recipes.py` for common use cases
5. Update this README with new functionality
