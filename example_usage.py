"""
Example usage of PostHog driver.

Demonstrates:
- Driver initialization
- Authentication
- Common operations
- Error handling
- Context manager usage
"""

import os
from datetime import datetime, timedelta

from base_driver import AuthConfig, AuthStrategy, DriverError, AuthError
from posthog_driver import PostHogDriver


# ============================================================================
# PostHog Examples
# ============================================================================

def posthog_example_basic():
    """Basic PostHog usage."""
    print("\n=== PostHog Basic Example ===\n")

    # Create driver from environment (POSTHOG_API_KEY, POSTHOG_PROJECT_ID)
    driver = PostHogDriver.from_env()

    try:
        # Test connection
        if driver.test_connection():
            print("✓ Connected to PostHog successfully\n")

        # List projects
        print("Projects:")
        projects = driver.list_projects()
        for project in projects:
            print(f"  - {project['name']} (ID: {project['id']})")

        # Get event definitions
        print("\nEvent Definitions:")
        events = driver.get_event_definitions()
        for event in events[:10]:  # Show first 10
            volume = event.get('volume_30_day', 0)
            print(f"  - {event['name']}: {volume:,} events/month")

        # Query recent pageview events
        print("\nRecent Pageview Events:")
        pageviews = driver.query_events(
            event='$pageview',
            date_from=datetime.now() - timedelta(days=1),
            limit=5
        )
        for event in pageviews:
            url = event.get('properties', {}).get('$current_url', 'N/A')
            print(f"  - {url}")

    except AuthError as e:
        print(f"Authentication failed: {e}")
    except DriverError as e:
        print(f"Error: {e}")
    finally:
        driver.close()


def posthog_example_context_manager():
    """Using PostHog driver with context manager."""
    print("\n=== PostHog Context Manager Example ===\n")

    # Using explicit auth config
    auth = AuthConfig(
        AuthStrategy.BEARER_TOKEN,
        {'token': os.getenv('POSTHOG_API_KEY')}
    )

    with PostHogDriver('https://app.posthog.com', auth, project_id=12345) as driver:
        # Get event definitions
        events = driver.get_event_definitions()
        print(f"Event types: {len(events)}")

        # Query recent events
        recent_events = driver.query_events(
            date_from=datetime.now() - timedelta(days=1),
            limit=10
        )
        print(f"Recent events: {len(recent_events)}")


def posthog_example_feature_flags():
    """Working with PostHog feature flags."""
    print("\n=== PostHog Feature Flags Example ===\n")

    # Using explicit configuration
    auth = AuthConfig(
        AuthStrategy.BEARER_TOKEN,
        {'token': os.getenv('POSTHOG_API_KEY')}
    )

    with PostHogDriver('https://app.posthog.com', auth, project_id=12345) as driver:
        # List all feature flags
        print("Feature Flags:")
        flags = driver.list_feature_flags()
        for flag in flags:
            status = "✓ Active" if flag['active'] else "✗ Inactive"
            print(f"  - {flag['key']}: {status}")

        # Get specific flag details
        if flags:
            flag_id = flags[0]['id']
            flag_detail = driver.get_feature_flag(flag_id)
            print(f"\nFlag Details: {flag_detail['key']}")
            print(f"  Filters: {flag_detail.get('filters', {})}")


def posthog_example_insights():
    """Query PostHog insights and analytics."""
    print("\n=== PostHog Insights Example ===\n")

    driver = PostHogDriver.from_env()

    try:
        # List saved insights
        print("Saved Insights:")
        insights = driver.list_insights(limit=5)
        for insight in insights:
            print(f"  - {insight['name']} ({insight.get('insight', 'N/A')})")

        # Execute ad-hoc trend query
        print("\nPageview Trend (Last 7 Days):")
        trend_results = driver.query_insight({
            'insight': 'TRENDS',
            'events': [{'id': '$pageview'}],
            'date_from': '-7d',
            'date_to': 'now',
            'interval': 'day'
        })

        # Parse and display results
        if 'result' in trend_results:
            for series in trend_results['result']:
                print(f"  Data: {series.get('data', [])}")

    finally:
        driver.close()


def posthog_example_cohorts():
    """Working with PostHog cohorts."""
    print("\n=== PostHog Cohorts Example ===\n")

    with PostHogDriver.from_env() as driver:
        # List cohorts
        cohorts = driver.list_cohorts()
        print(f"Total cohorts: {len(cohorts)}\n")

        for cohort in cohorts:
            print(f"  - {cohort['name']}")
            print(f"    Count: {cohort.get('count', 'N/A')}")
            print(f"    Filters: {cohort.get('filters', {})}")


def posthog_example_persons():
    """Working with PostHog persons (users)."""
    print("\n=== PostHog Persons Example ===\n")

    with PostHogDriver.from_env() as driver:
        # Get person properties
        print("Person Properties:")
        properties = driver.get_person_properties()
        for prop in properties[:10]:
            print(f"  - {prop}")

        # List persons (limit to 5 for demo)
        print("\nRecent Persons:")
        persons = driver.list_persons(limit=5)
        for person in persons:
            print(f"  - {person.get('distinct_ids', ['Unknown'])[0]}")
            if person.get('properties'):
                print(f"    Properties: {list(person['properties'].keys())[:3]}")


def posthog_example_dashboards():
    """Working with PostHog dashboards."""
    print("\n=== PostHog Dashboards Example ===\n")

    with PostHogDriver.from_env() as driver:
        # List dashboards
        dashboards = driver.list_dashboards()
        print(f"Total dashboards: {len(dashboards)}\n")

        for dash in dashboards[:5]:  # Show first 5
            print(f"  - {dash['name']}")
            print(f"    Description: {dash.get('description', 'N/A')}")
            print(f"    Tiles: {len(dash.get('tiles', []))}")


# ============================================================================
# Error Handling Examples
# ============================================================================

def error_handling_example():
    """Demonstrate comprehensive error handling."""
    print("\n=== Error Handling Example ===\n")

    from base_driver import ConnectionError, ResourceNotFoundError

    driver = PostHogDriver.from_env()

    try:
        # Try to get non-existent person
        person = driver.get_person('nonexistent-id')

    except ResourceNotFoundError as e:
        print(f"✓ Handled resource not found: {e}")

    except ConnectionError as e:
        print(f"✗ Connection error: {e}")
        print("  Check network connectivity and API endpoint")

    except AuthError as e:
        print(f"✗ Authentication error: {e}")
        print("  Verify API key is valid and has proper permissions")

    except DriverError as e:
        print(f"✗ General driver error: {e}")

    finally:
        driver.close()


# ============================================================================
# Advanced Examples
# ============================================================================

def advanced_pagination_example():
    """Demonstrate pagination for large datasets."""
    print("\n=== Advanced Pagination Example ===\n")

    from base_driver import PaginationStrategy

    with PostHogDriver.from_env() as driver:
        print("Fetching events (with pagination)...")

        total_events = 0
        for event in driver._paginate(
            f'projects/{driver.project_id}/events',
            PaginationStrategy.OFFSET_LIMIT,
            page_size=100,
            max_pages=5  # Limit to 5 pages for demo
        ):
            total_events += 1

        print(f"Processed {total_events} events")


def advanced_event_querying():
    """Advanced event querying with filters."""
    print("\n=== Advanced Event Querying Example ===\n")

    with PostHogDriver.from_env() as driver:
        # Query events with property filters
        print("Querying events with filters...")

        events = driver.query_events(
            event='$pageview',
            date_from=datetime.now() - timedelta(days=7),
            date_to=datetime.now(),
            properties=[
                {
                    'key': '$browser',
                    'value': 'Chrome',
                    'operator': 'exact'
                }
            ],
            limit=10
        )

        print(f"Found {len(events)} Chrome pageview events")

        for event in events[:3]:
            print(f"  - {event['timestamp']}: {event.get('properties', {}).get('$current_url', 'N/A')}")


def recipe_example_power_users():
    """Example using a recipe from driver_recipes.py."""
    print("\n=== Recipe Example: Power Users ===\n")

    # This demonstrates how recipes can be used
    from driver_recipes import find_power_users

    with PostHogDriver.from_env() as driver:
        # Find users who did $pageview at least 10 times in last 7 days
        power_users = find_power_users(
            driver,
            action='$pageview',
            frequency=10,
            weeks=1
        )

        print(f"Found {len(power_users)} power users")
        for user in power_users[:5]:
            print(f"  - {user['user_id']}: {user['event_count']} events")


# ============================================================================
# Main
# ============================================================================

if __name__ == '__main__':
    print("PostHog Driver Usage Examples")
    print("=" * 60)

    # Run examples (comment out as needed)

    # Basic examples
    # posthog_example_basic()
    # posthog_example_context_manager()

    # Feature-specific examples
    # posthog_example_feature_flags()
    # posthog_example_insights()
    # posthog_example_cohorts()
    # posthog_example_persons()
    # posthog_example_dashboards()

    # Advanced examples
    # error_handling_example()
    # advanced_pagination_example()
    # advanced_event_querying()
    # recipe_example_power_users()

    print("\n" + "=" * 60)
    print("To run examples, uncomment the desired function calls above")
    print("and ensure environment variables are set:")
    print("  - POSTHOG_API_KEY")
    print("  - POSTHOG_PROJECT_ID")
