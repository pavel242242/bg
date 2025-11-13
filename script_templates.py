"""
Script templates for Claude Agent SDK code generation.

These templates are used to generate Python code that runs inside E2B sandboxes.
Each template includes:
- Proper imports
- Error handling
- JSON output formatting
- Sandbox path configuration
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

POSTHOG_LIST_COHORTS = """
import sys
sys.path.insert(0, '/home/user')

import json
from posthog_driver import PostHogDriver
from base_driver import AuthConfig, AuthStrategy, DriverError

try:
    auth = AuthConfig(AuthStrategy.BEARER_TOKEN, {{'token': '{api_token}'}})
    driver = PostHogDriver('{base_url}', auth, project_id={project_id})

    cohorts = driver.list_cohorts()

    print(json.dumps({{
        'success': True,
        'data': cohorts,
        'count': len(cohorts)
    }}, indent=2))

except DriverError as e:
    print(json.dumps({{
        'success': False,
        'error': str(e),
        'error_type': type(e).__name__
    }}, indent=2))
"""

POSTHOG_LIST_PERSONS = """
import sys
sys.path.insert(0, '/home/user')

import json
from posthog_driver import PostHogDriver
from base_driver import AuthConfig, AuthStrategy, DriverError

try:
    auth = AuthConfig(AuthStrategy.BEARER_TOKEN, {{'token': '{api_token}'}})
    driver = PostHogDriver('{base_url}', auth, project_id={project_id})

    persons = driver.list_persons(limit={limit})

    print(json.dumps({{
        'success': True,
        'data': persons,
        'count': len(persons)
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
            POSTHOG_QUERY_EVENTS,
            api_token="token",
            base_url="http://localhost:8001",
            project_id=12345,
            event_repr=repr("$pageview"),
            date_from_repr=repr(datetime.now() - timedelta(days=7)),
            date_to_repr=repr(datetime.now()),
            limit=100
        )
    """
    return template.format(**kwargs)


# Template Catalog
# =============================================================================

POSTHOG_TEMPLATES = {
    "list_projects": POSTHOG_LIST_PROJECTS,
    "query_events": POSTHOG_QUERY_EVENTS,
    "get_event_definitions": POSTHOG_GET_EVENT_DEFINITIONS,
    "list_feature_flags": POSTHOG_LIST_FEATURE_FLAGS,
    "list_insights": POSTHOG_LIST_INSIGHTS,
    "list_cohorts": POSTHOG_LIST_COHORTS,
    "list_persons": POSTHOG_LIST_PERSONS
}

ALL_TEMPLATES = {
    "posthog": POSTHOG_TEMPLATES
}


def get_template(service: str, operation: str) -> str:
    """
    Get a template by service and operation name.

    Args:
        service: "posthog"
        operation: Operation name (e.g., "query_events", "list_feature_flags")

    Returns:
        Template string

    Raises:
        KeyError: If service or operation not found

    Example:
        template = get_template("posthog", "query_events")
    """
    return ALL_TEMPLATES[service][operation]
