"""
Script templates for Claude Code agent code generation.

These templates are used by the agent executor to generate Python code
that runs inside E2B sandboxes. Each template includes:
- Proper imports
- Error handling
- JSON output formatting
- Sandbox path configuration
"""

# Grafana Templates
# =============================================================================

GRAFANA_LIST_DASHBOARDS = """
import sys
sys.path.insert(0, '/home/user')

import json
from grafana_driver import GrafanaDriver
from base_driver import AuthConfig, AuthStrategy, DriverError

try:
    auth = AuthConfig(AuthStrategy.BEARER_TOKEN, {{'token': '{api_token}'}})
    driver = GrafanaDriver('{base_url}', auth)

    dashboards = driver.search_dashboards(
        query={query_repr},
        tag={tag_repr},
        limit={limit}
    )

    print(json.dumps({{
        'success': True,
        'data': dashboards,
        'count': len(dashboards)
    }}, indent=2))

except DriverError as e:
    print(json.dumps({{
        'success': False,
        'error': str(e),
        'error_type': type(e).__name__
    }}, indent=2))
"""

GRAFANA_GET_DASHBOARD = """
import sys
sys.path.insert(0, '/home/user')

import json
from grafana_driver import GrafanaDriver
from base_driver import AuthConfig, AuthStrategy, DriverError

try:
    auth = AuthConfig(AuthStrategy.BEARER_TOKEN, {{'token': '{api_token}'}})
    driver = GrafanaDriver('{base_url}', auth)

    dashboard = driver.get_dashboard_by_uid('{uid}')

    print(json.dumps({{
        'success': True,
        'data': dashboard
    }}, indent=2))

except DriverError as e:
    print(json.dumps({{
        'success': False,
        'error': str(e),
        'error_type': type(e).__name__
    }}, indent=2))
"""

GRAFANA_EXPORT_DASHBOARD = """
import sys
sys.path.insert(0, '/home/user')

import json
from grafana_driver import GrafanaDriver
from base_driver import AuthConfig, AuthStrategy, DriverError

try:
    auth = AuthConfig(AuthStrategy.BEARER_TOKEN, {{'token': '{api_token}'}})
    driver = GrafanaDriver('{base_url}', auth)

    dashboard = driver.export_dashboard('{uid}')

    print(json.dumps({{
        'success': True,
        'data': dashboard,
        'title': dashboard.get('title'),
        'panels': len(dashboard.get('panels', []))
    }}, indent=2))

except DriverError as e:
    print(json.dumps({{
        'success': False,
        'error': str(e),
        'error_type': type(e).__name__
    }}, indent=2))
"""

GRAFANA_LIST_DATASOURCES = """
import sys
sys.path.insert(0, '/home/user')

import json
from grafana_driver import GrafanaDriver
from base_driver import AuthConfig, AuthStrategy, DriverError

try:
    auth = AuthConfig(AuthStrategy.BEARER_TOKEN, {{'token': '{api_token}'}})
    driver = GrafanaDriver('{base_url}', auth)

    datasources = driver.list_datasources()

    print(json.dumps({{
        'success': True,
        'data': datasources,
        'count': len(datasources)
    }}, indent=2))

except DriverError as e:
    print(json.dumps({{
        'success': False,
        'error': str(e),
        'error_type': type(e).__name__
    }}, indent=2))
"""

GRAFANA_GET_ANNOTATIONS = """
import sys
sys.path.insert(0, '/home/user')

import json
from datetime import datetime, timedelta
from grafana_driver import GrafanaDriver
from base_driver import AuthConfig, AuthStrategy, DriverError

try:
    auth = AuthConfig(AuthStrategy.BEARER_TOKEN, {{'token': '{api_token}'}})
    driver = GrafanaDriver('{base_url}', auth)

    annotations = driver.get_annotations(
        from_time={from_time_repr},
        to_time={to_time_repr},
        tags={tags_repr},
        limit={limit}
    )

    print(json.dumps({{
        'success': True,
        'data': annotations,
        'count': len(annotations)
    }}, indent=2))

except DriverError as e:
    print(json.dumps({{
        'success': False,
        'error': str(e),
        'error_type': type(e).__name__
    }}, indent=2))
"""

# PostHog Templates
# =============================================================================

POSTHOG_LIST_PROJECTS = """
import sys
sys.path.insert(0, '/home/user')

import json
from posthog_driver import PostHogDriver
from base_driver import AuthConfig, AuthStrategy, DriverError

try:
    auth = AuthConfig(AuthStrategy.BEARER_TOKEN, {{'token': '{api_token}'}})
    driver = PostHogDriver('{base_url}', auth)

    projects = driver.list_projects()

    print(json.dumps({{
        'success': True,
        'data': projects,
        'count': len(projects)
    }}, indent=2))

except DriverError as e:
    print(json.dumps({{
        'success': False,
        'error': str(e),
        'error_type': type(e).__name__
    }}, indent=2))
"""

POSTHOG_QUERY_EVENTS = """
import sys
sys.path.insert(0, '/home/user')

import json
from datetime import datetime, timedelta
from posthog_driver import PostHogDriver
from base_driver import AuthConfig, AuthStrategy, DriverError

try:
    auth = AuthConfig(AuthStrategy.BEARER_TOKEN, {{'token': '{api_token}'}})
    driver = PostHogDriver('{base_url}', auth, project_id={project_id})

    events = driver.query_events(
        event={event_repr},
        date_from={date_from_repr},
        date_to={date_to_repr},
        limit={limit}
    )

    print(json.dumps({{
        'success': True,
        'data': events,
        'count': len(events)
    }}, indent=2))

except DriverError as e:
    print(json.dumps({{
        'success': False,
        'error': str(e),
        'error_type': type(e).__name__
    }}, indent=2))
"""

POSTHOG_GET_EVENT_DEFINITIONS = """
import sys
sys.path.insert(0, '/home/user')

import json
from posthog_driver import PostHogDriver
from base_driver import AuthConfig, AuthStrategy, DriverError

try:
    auth = AuthConfig(AuthStrategy.BEARER_TOKEN, {{'token': '{api_token}'}})
    driver = PostHogDriver('{base_url}', auth, project_id={project_id})

    events = driver.get_event_definitions()

    print(json.dumps({{
        'success': True,
        'data': events,
        'count': len(events)
    }}, indent=2))

except DriverError as e:
    print(json.dumps({{
        'success': False,
        'error': str(e),
        'error_type': type(e).__name__
    }}, indent=2))
"""

POSTHOG_LIST_FEATURE_FLAGS = """
import sys
sys.path.insert(0, '/home/user')

import json
from posthog_driver import PostHogDriver
from base_driver import AuthConfig, AuthStrategy, DriverError

try:
    auth = AuthConfig(AuthStrategy.BEARER_TOKEN, {{'token': '{api_token}'}})
    driver = PostHogDriver('{base_url}', auth, project_id={project_id})

    flags = driver.list_feature_flags()

    print(json.dumps({{
        'success': True,
        'data': flags,
        'count': len(flags)
    }}, indent=2))

except DriverError as e:
    print(json.dumps({{
        'success': False,
        'error': str(e),
        'error_type': type(e).__name__
    }}, indent=2))
"""

POSTHOG_LIST_INSIGHTS = """
import sys
sys.path.insert(0, '/home/user')

import json
from posthog_driver import PostHogDriver
from base_driver import AuthConfig, AuthStrategy, DriverError

try:
    auth = AuthConfig(AuthStrategy.BEARER_TOKEN, {{'token': '{api_token}'}})
    driver = PostHogDriver('{base_url}', auth, project_id={project_id})

    insights = driver.list_insights(limit={limit})

    print(json.dumps({{
        'success': True,
        'data': insights,
        'count': len(insights)
    }}, indent=2))

except DriverError as e:
    print(json.dumps({{
        'success': False,
        'error': str(e),
        'error_type': type(e).__name__
    }}, indent=2))
"""

# Template Utilities
# =============================================================================

def format_template(template: str, **kwargs) -> str:
    """
    Format a template with parameters, handling repr() for complex types.

    Args:
        template: Template string with {param} placeholders
        **kwargs: Parameters to substitute

    Returns:
        Formatted script ready to execute

    Example:
        script = format_template(
            GRAFANA_LIST_DASHBOARDS,
            api_token="token",
            base_url="http://localhost:8000",
            query_repr=repr("sales"),
            tag_repr=repr("production"),
            limit=100
        )
    """
    return template.format(**kwargs)


# Template Catalog
# =============================================================================

GRAFANA_TEMPLATES = {
    "list_dashboards": GRAFANA_LIST_DASHBOARDS,
    "get_dashboard": GRAFANA_GET_DASHBOARD,
    "export_dashboard": GRAFANA_EXPORT_DASHBOARD,
    "list_datasources": GRAFANA_LIST_DATASOURCES,
    "get_annotations": GRAFANA_GET_ANNOTATIONS
}

POSTHOG_TEMPLATES = {
    "list_projects": POSTHOG_LIST_PROJECTS,
    "query_events": POSTHOG_QUERY_EVENTS,
    "get_event_definitions": POSTHOG_GET_EVENT_DEFINITIONS,
    "list_feature_flags": POSTHOG_LIST_FEATURE_FLAGS,
    "list_insights": POSTHOG_LIST_INSIGHTS
}

ALL_TEMPLATES = {
    "grafana": GRAFANA_TEMPLATES,
    "posthog": POSTHOG_TEMPLATES
}


def get_template(service: str, operation: str) -> str:
    """
    Get a template by service and operation name.

    Args:
        service: "grafana" or "posthog"
        operation: Operation name (e.g., "list_dashboards")

    Returns:
        Template string

    Raises:
        KeyError: If service or operation not found
    """
    return ALL_TEMPLATES[service][operation]
