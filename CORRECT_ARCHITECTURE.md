# CORRECT Architecture: Claude Agent SDK in E2B

> **NOTE:** This document contains Grafana examples for illustration purposes. Grafana driver
> was removed from the repository (V1 focuses on PostHog only). However, the architecture
> patterns shown here apply equally to PostHog or any other API driver. Simply replace
> `GrafanaDriver` with `PostHogDriver` in the examples.

## I Was Wrong - Here's the Real Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ E2B SANDBOX (Single Isolated VM)                           │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐│
│  │ Claude Agent SDK Instance                              ││
│  │                                                         ││
│  │  Can directly:                                         ││
│  │    from posthog_driver import PostHogDriver           ││
│  │                                                         ││
│  │  Can modify drivers on the fly:                       ││
│  │    - Add new methods                                   ││
│  │    - Extend functionality                              ││
│  │    - Create custom queries                             ││
│  │    - Build complex workflows                           ││
│  └────────────────────────────────────────────────────────┘│
│                            ↓                                 │
│  ┌────────────────────────────────────────────────────────┐│
│  │ Driver Code (in same sandbox)                          ││
│  │   /home/user/base_driver.py                            ││
│  │   /home/user/posthog_driver.py                         ││
│  │   /home/user/driver_recipes.py                         ││
│  └────────────────────────────────────────────────────────┘│
│                            ↓                                 │
│  ┌────────────────────────────────────────────────────────┐│
│  │ Mock API (localhost:8001) OR Real API                  ││
│  │  https://app.posthog.com                               ││
│  └────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

## The Real Question

**How should drivers be structured so Claude Agent SDK (in same sandbox) can:**
1. **Easily use them** - Simple, clear API
2. **Easily modify them** - Extensible, well-documented
3. **Build on them** - Create new functionality to fulfill user intent

---

## Answer: Driver Structure for Easy Agent Use

### 1. Drivers Should Be "Building Blocks"

```python
# Claude Agent SDK can import and use directly:
from grafana_driver import GrafanaDriver
from base_driver import AuthConfig, AuthStrategy

# Simple instantiation
driver = GrafanaDriver.from_env('http://localhost:8000')

# OR custom auth
auth = AuthConfig(AuthStrategy.BEARER_TOKEN, {'token': 'xxx'})
driver = GrafanaDriver('http://localhost:8000', auth)

# Use methods
dashboards = driver.search_dashboards(tag='production')
dashboard = driver.get_dashboard_by_uid('abc123')
```

**Why this works:**
- No complex setup
- Clear, predictable methods
- Can be used in one line

### 2. Drivers Should Be Easily Extendable

```python
# Claude Agent can extend drivers to add new functionality:
class CustomGrafanaDriver(GrafanaDriver):
    """Extended driver with user-specific methods."""

    def get_production_dashboards_with_errors(self):
        """Custom method: Get production dashboards that have error panels."""
        # Get all production dashboards
        dashboards = self.search_dashboards(tag='production')

        results = []
        for dash in dashboards:
            # Get full dashboard
            full_dash = self.get_dashboard_by_uid(dash['uid'])

            # Check if any panels query errors
            dashboard_json = full_dash['dashboard']
            for panel in dashboard_json.get('panels', []):
                for target in panel.get('targets', []):
                    if 'error' in target.get('expr', '').lower():
                        results.append(dash)
                        break

        return results

# Use extended driver
custom_driver = CustomGrafanaDriver.from_env('http://localhost:8000')
error_dashboards = custom_driver.get_production_dashboards_with_errors()
```

**Why this works:**
- Inherits all base functionality
- Can add domain-specific methods
- Agent creates what user needs

### 3. Drivers Should Have Helper Recipes

```python
# driver_recipes.py - Common patterns Claude can use or modify
"""
Recipe collection for common driver operations.

Claude Agent SDK can import these as examples or modify them for specific needs.
"""

from grafana_driver import GrafanaDriver
from posthog_driver import PostHogDriver
from datetime import datetime, timedelta

def find_unused_dashboards(driver: GrafanaDriver, days=30):
    """
    Find Grafana dashboards that haven't been viewed recently.

    Args:
        driver: GrafanaDriver instance
        days: Number of days to check

    Returns:
        List of dashboard UIDs that appear unused
    """
    all_dashboards = driver.search_dashboards()

    # Get annotations (proxy for dashboard views)
    cutoff = datetime.now() - timedelta(days=days)
    annotations = driver.get_annotations(from_time=cutoff)

    # Dashboards with annotations are being used
    used_dashboard_ids = set(a['dashboardId'] for a in annotations if a.get('dashboardId'))

    # Find dashboards NOT in the used set
    unused = [d for d in all_dashboards if d['id'] not in used_dashboard_ids]

    return unused


def correlate_deployments_with_errors(
    grafana_driver: GrafanaDriver,
    posthog_driver: PostHogDriver,
    hours=24
):
    """
    Find if deployments correlate with error spikes.

    Args:
        grafana_driver: GrafanaDriver instance
        posthog_driver: PostHogDriver instance
        hours: Hours to analyze

    Returns:
        Dict with deployment times and error counts
    """
    cutoff = datetime.now() - timedelta(hours=hours)

    # Get deployment annotations from Grafana
    annotations = grafana_driver.get_annotations(
        from_time=cutoff,
        tags=['deployment']
    )

    # Get error events from PostHog
    error_events = posthog_driver.query_events(
        event='error_occurred',
        date_from=cutoff
    )

    # Correlate: for each deployment, count errors in next hour
    results = []
    for annotation in annotations:
        deploy_time = datetime.fromtimestamp(annotation['time'] / 1000)
        errors_after = [
            e for e in error_events
            if deploy_time < datetime.fromisoformat(e['timestamp']) < deploy_time + timedelta(hours=1)
        ]

        results.append({
            'deployment': annotation['text'],
            'time': deploy_time,
            'errors_in_next_hour': len(errors_after)
        })

    return results


def export_all_dashboards_to_files(driver: GrafanaDriver, output_dir='./dashboards'):
    """
    Export all Grafana dashboards to JSON files.

    Args:
        driver: GrafanaDriver instance
        output_dir: Directory to save files

    Returns:
        List of saved file paths
    """
    import os
    import json

    os.makedirs(output_dir, exist_ok=True)

    dashboards = driver.search_dashboards()
    saved_files = []

    for dash in dashboards:
        dashboard_json = driver.export_dashboard(dash['uid'])

        filename = f"{dash['uid']}.json"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, 'w') as f:
            json.dump(dashboard_json, f, indent=2)

        saved_files.append(filepath)

    return saved_files


# Claude Agent can use these directly:
# >>> from driver_recipes import find_unused_dashboards
# >>> unused = find_unused_dashboards(driver, days=60)
# >>> print(f"Found {len(unused)} unused dashboards")
```

**Why this works:**
- Provides ready-made patterns
- Shows how to combine driver methods
- Agent can modify recipes for specific needs
- Demonstrates best practices

### 4. Drivers Should Be Well-Documented

```python
class GrafanaDriver(PaginatedDriver):
    """
    Driver for Grafana API data extraction.

    This driver provides methods to interact with Grafana's REST API
    for querying dashboards, data sources, annotations, and more.

    Basic Usage:
        >>> driver = GrafanaDriver.from_env('http://localhost:8000')
        >>> dashboards = driver.search_dashboards()
        >>> for dash in dashboards:
        ...     print(dash['title'])

    Advanced Usage:
        >>> # Search with filters
        >>> prod_dashboards = driver.search_dashboards(
        ...     query='api',
        ...     tag='production',
        ...     limit=50
        ... )
        >>>
        >>> # Get dashboard details
        >>> dashboard = driver.get_dashboard_by_uid('abc123')
        >>> print(dashboard['dashboard']['title'])
        >>>
        >>> # Query annotations
        >>> from datetime import datetime, timedelta
        >>> annotations = driver.get_annotations(
        ...     from_time=datetime.now() - timedelta(days=7),
        ...     tags=['deployment']
        ... )

    Extension Example:
        >>> class MyGrafanaDriver(GrafanaDriver):
        ...     def get_alerts_for_dashboard(self, uid):
        ...         '''Custom method to get alerts.'''
        ...         dashboard = self.get_dashboard_by_uid(uid)
        ...         # ... custom logic ...
        ...         return alerts
        >>>
        >>> my_driver = MyGrafanaDriver.from_env('http://localhost:8000')
        >>> alerts = my_driver.get_alerts_for_dashboard('abc123')

    Error Handling:
        >>> from base_driver import ResourceNotFoundError
        >>> try:
        ...     driver.get_dashboard_by_uid('nonexistent')
        ... except ResourceNotFoundError as e:
        ...     print(f"Dashboard not found: {e}")

    All methods raise specific exceptions (ResourceNotFoundError,
    AuthError, ConnectionError, etc.) for granular error handling.
    """

    def search_dashboards(
        self,
        query: Optional[str] = None,
        tag: Optional[str] = None,
        starred: bool = False,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Search for dashboards.

        Args:
            query: Search query string to filter dashboard titles
                   Example: 'sales' finds "Sales Dashboard", "Q4 Sales", etc.
            tag: Filter by tag
                 Example: 'production' finds dashboards tagged "production"
            starred: If True, return only starred dashboards
            limit: Maximum number of results (default: 1000)

        Returns:
            List of dashboard dictionaries with structure:
            [
                {
                    'id': 1,
                    'uid': 'abc123',
                    'title': 'Sales Dashboard',
                    'tags': ['business', 'sales'],
                    'isStarred': True,
                    'folderTitle': 'Business Metrics'
                },
                ...
            ]

        Raises:
            ConnectionError: If cannot connect to Grafana
            AuthError: If authentication fails

        Example:
            >>> # Find all dashboards
            >>> all_dashboards = driver.search_dashboards()
            >>>
            >>> # Find dashboards about APIs
            >>> api_dashboards = driver.search_dashboards(query='api')
            >>>
            >>> # Find production dashboards
            >>> prod = driver.search_dashboards(tag='production')
            >>>
            >>> # Find starred dashboards
            >>> starred = driver.search_dashboards(starred=True)
            >>>
            >>> # Combine filters
            >>> result = driver.search_dashboards(
            ...     query='sales',
            ...     tag='production',
            ...     limit=10
            ... )
        """
        # Implementation...
```

**Why this works:**
- Claude can read docstrings to understand methods
- Examples show common patterns
- Extension examples show how to build on it
- Clear parameter descriptions

### 5. Drivers Should Have Configuration Examples

```python
# examples/driver_config.py
"""
Configuration examples for different scenarios.

Claude Agent can use these as templates.
"""

from grafana_driver import GrafanaDriver
from posthog_driver import PostHogDriver
from base_driver import AuthConfig, AuthStrategy
import os

# Example 1: Mock mode for testing
def create_mock_grafana():
    """Create Grafana driver for testing (mock API)."""
    auth = AuthConfig(AuthStrategy.BEARER_TOKEN, {'token': 'mock'})
    return GrafanaDriver('http://localhost:8000', auth)

# Example 2: Production with environment variables
def create_production_grafana():
    """Create Grafana driver for production."""
    return GrafanaDriver.from_env(
        base_url=os.getenv('GRAFANA_URL', 'https://grafana.com'),
        env_var='GRAFANA_TOKEN'
    )

# Example 3: Custom auth with API key
def create_custom_grafana(url, api_key):
    """Create Grafana driver with custom credentials."""
    auth = AuthConfig(
        AuthStrategy.API_KEY,
        {'api_key': api_key},
        header_name='Authorization'  # Custom header if needed
    )
    return GrafanaDriver(url, auth)

# Example 4: PostHog with project ID
def create_posthog(project_id=12345):
    """Create PostHog driver."""
    auth = AuthConfig(
        AuthStrategy.BEARER_TOKEN,
        {'token': os.getenv('POSTHOG_API_KEY')}
    )
    return PostHogDriver(
        'http://localhost:8001',
        auth,
        project_id=project_id
    )

# Example 5: Multiple drivers for correlation
def create_all_drivers():
    """Create all drivers for cross-platform analysis."""
    return {
        'grafana': create_production_grafana(),
        'posthog': create_posthog()
    }
```

---

## How Claude Agent SDK Uses the Drivers

### Scenario 1: Direct Use

```python
# Claude Agent SDK code (in E2B sandbox):

# User: "Show me my Grafana dashboards"

from grafana_driver import GrafanaDriver

driver = GrafanaDriver.from_env('http://localhost:8000')
dashboards = driver.search_dashboards()

print(f"Found {len(dashboards)} dashboards:")
for dash in dashboards:
    print(f"- {dash['title']} ({dash['uid']})")
```

### Scenario 2: Agent Modifies Driver

```python
# Claude Agent SDK code (in E2B sandbox):

# User: "Find Grafana dashboards that mention 'API' and are in production"

from grafana_driver import GrafanaDriver

class SmartGrafanaDriver(GrafanaDriver):
    def find_api_dashboards_in_production(self):
        """Custom method created by agent to fulfill user request."""
        # Search by query
        query_results = self.search_dashboards(query='api')

        # Filter by tag
        production_results = [
            d for d in query_results
            if 'production' in [tag.lower() for tag in d.get('tags', [])]
        ]

        return production_results

driver = SmartGrafanaDriver.from_env('http://localhost:8000')
results = driver.find_api_dashboards_in_production()

for dash in results:
    print(f"{dash['title']}: {dash['tags']}")
```

### Scenario 3: Agent Creates Complex Workflow

```python
# Claude Agent SDK code (in E2B sandbox):

# User: "Which dashboards were created recently and have error panels?"

from grafana_driver import GrafanaDriver
from datetime import datetime, timedelta

driver = GrafanaDriver.from_env('http://localhost:8000')

# Step 1: Get all dashboards
all_dashboards = driver.search_dashboards()

# Step 2: Filter recent ones
recent_dashboards = []
cutoff = datetime.now() - timedelta(days=30)

for dash in all_dashboards:
    full_dash = driver.get_dashboard_by_uid(dash['uid'])
    updated = datetime.fromisoformat(full_dash['meta']['updated'])

    if updated > cutoff:
        # Step 3: Check for error panels
        dashboard_json = full_dash['dashboard']
        has_errors = any(
            'error' in panel.get('title', '').lower()
            for panel in dashboard_json.get('panels', [])
        )

        if has_errors:
            recent_dashboards.append({
                'title': dash['title'],
                'uid': dash['uid'],
                'updated': updated,
                'url': f"/d/{dash['uid']}"
            })

print(f"Found {len(recent_dashboards)} recent dashboards with error panels:")
for dash in recent_dashboards:
    print(f"- {dash['title']} (updated {dash['updated']})")
```

---

## Summary: What Makes Drivers Easy for Claude Agent

1. **Simple API** - Clear methods with obvious names
2. **Well-documented** - Docstrings with examples
3. **Extensible** - Easy to subclass and add methods
4. **Modular** - Base functionality separated from specific operations
5. **Recipe library** - Common patterns ready to use/modify
6. **Clear errors** - Specific exceptions for different failures
7. **Context managers** - Easy resource cleanup
8. **Configuration examples** - Templates for different scenarios

**The key insight:** Drivers are **libraries** not **services**. Claude Agent SDK imports them directly and can modify/extend them as needed to fulfill user intent.
