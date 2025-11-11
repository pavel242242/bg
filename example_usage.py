"""
Example usage of Grafana and PostHog drivers.

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
from grafana_driver import GrafanaDriver
from posthog_driver import PostHogDriver


# ============================================================================
# Grafana Examples
# ============================================================================

def grafana_example_basic():
    """Basic Grafana usage with environment variables."""
    print("=== Grafana Basic Example ===\n")

    # Create driver from environment variable (GRAFANA_TOKEN)
    driver = GrafanaDriver.from_env('https://my-instance.grafana.net')

    try:
        # Test connection
        if driver.test_connection():
            print("✓ Connected to Grafana successfully\n")

        # List all dashboards
        print("Dashboards:")
        dashboards = driver.search_dashboards()
        for dash in dashboards[:5]:  # Show first 5
            print(f"  - {dash['title']} (UID: {dash['uid']})")

        print("\nData Sources:")
        datasources = driver.list_datasources()
        for ds in datasources:
            print(f"  - {ds['name']}: {ds['type']}")

        # Get annotations from last 7 days
        print("\nRecent Annotations:")
        annotations = driver.get_annotations(
            from_time=datetime.now() - timedelta(days=7),
            to_time=datetime.now(),
            limit=5
        )
        for ann in annotations:
            print(f"  - {ann['text']} ({ann.get('tags', [])})")

    except AuthError as e:
        print(f"Authentication failed: {e}")
    except DriverError as e:
        print(f"Error: {e}")
    finally:
        driver.close()


def grafana_example_context_manager():
    """Using Grafana driver with context manager."""
    print("\n=== Grafana Context Manager Example ===\n")

    # Using explicit auth config
    auth = AuthConfig(
        AuthStrategy.BEARER_TOKEN,
        {'token': os.getenv('GRAFANA_TOKEN')}
    )

    with GrafanaDriver('https://my-instance.grafana.net', auth) as driver:
        # Export specific dashboard
        dashboard_uid = 'abc123'
        try:
            dashboard = driver.export_dashboard(dashboard_uid)
            print(f"Exported dashboard: {dashboard['title']}")
            print(f"Panels: {len(dashboard.get('panels', []))}")
        except Exception as e:
            print(f"Could not export dashboard: {e}")

        # Search for dashboards by tag
        prod_dashboards = driver.search_dashboards(tag='production')
        print(f"\nProduction dashboards: {len(prod_dashboards)}")


def grafana_example_bulk_export():
    """Export all dashboards for backup."""
    print("\n=== Grafana Bulk Export Example ===\n")

    driver = GrafanaDriver.from_env('https://my-instance.grafana.net')

    try:
        print("Exporting all dashboards...")
        count = 0

        for dashboard in driver.export_all_dashboards():
            filename = f"backups/grafana_{dashboard['uid']}.json"
            # Would save to file here
            print(f"  Exported: {dashboard['title']}")
            count += 1

        print(f"\nTotal dashboards exported: {count}")

    finally:
        driver.close()


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


# ============================================================================
# Error Handling Examples
# ============================================================================

def error_handling_example():
    """Demonstrate comprehensive error handling."""
    print("\n=== Error Handling Example ===\n")

    from base_driver import ConnectionError, ResourceNotFoundError

    driver = GrafanaDriver.from_env('https://my-instance.grafana.net')

    try:
        # Try to get non-existent dashboard
        dashboard = driver.get_dashboard_by_uid('nonexistent-uid')

    except ResourceNotFoundError as e:
        print(f"✓ Handled resource not found: {e}")

    except ConnectionError as e:
        print(f"✗ Connection error: {e}")
        print("  Check network connectivity and API endpoint")

    except AuthError as e:
        print(f"✗ Authentication error: {e}")
        print("  Verify API token is valid and has proper permissions")

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

    with PostHogDriver.from_env() as driver:
        print("Fetching all events (with pagination)...")

        total_events = 0
        for event in driver._paginate(
            f'projects/{driver.project_id}/events',
            PaginationStrategy.OFFSET_LIMIT,
            page_size=100,
            max_pages=5  # Limit to 5 pages for demo
        ):
            total_events += 1

        print(f"Processed {total_events} events")


def multi_driver_example():
    """Using multiple drivers together."""
    print("\n=== Multi-Driver Example ===\n")

    # Initialize both drivers
    grafana = GrafanaDriver.from_env('https://my-instance.grafana.net')
    posthog = PostHogDriver.from_env()

    try:
        # Get Grafana dashboard metadata
        dashboards = grafana.search_dashboards(limit=5)
        print(f"Grafana dashboards: {len(dashboards)}")

        # Get PostHog event definitions
        events = posthog.get_event_definitions()
        print(f"PostHog events: {len(events)}")

        # Could correlate data here...
        print("\nCorrelation analysis possible between monitoring and analytics")

    finally:
        grafana.close()
        posthog.close()


# ============================================================================
# Main
# ============================================================================

if __name__ == '__main__':
    print("Driver Usage Examples")
    print("=" * 60)

    # Run examples (comment out as needed)

    # Grafana examples
    # grafana_example_basic()
    # grafana_example_context_manager()
    # grafana_example_bulk_export()

    # PostHog examples
    # posthog_example_basic()
    # posthog_example_feature_flags()
    # posthog_example_insights()
    # posthog_example_cohorts()

    # Other examples
    # error_handling_example()
    # advanced_pagination_example()
    # multi_driver_example()

    print("\n" + "=" * 60)
    print("To run examples, uncomment the desired function calls above")
    print("and ensure environment variables are set:")
    print("  - GRAFANA_TOKEN")
    print("  - POSTHOG_API_KEY")
    print("  - POSTHOG_PROJECT_ID")
