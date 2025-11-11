"""
Driver Recipe Collection - Common Patterns for Claude Agent SDK

These are ready-to-use patterns that Claude Agent SDK can import and use directly,
or modify to fulfill specific user requests. Think of these as examples that show
how to combine driver methods to accomplish common tasks.

Claude Agent SDK runs in the same E2B sandbox as the drivers, so it can:
- Import these recipes directly
- Modify them for specific needs
- Use them as templates for new functionality
- Combine multiple recipes

Usage:
    from driver_recipes import find_unused_dashboards
    from grafana_driver import GrafanaDriver

    driver = GrafanaDriver.from_env('http://localhost:8000')
    unused = find_unused_dashboards(driver, days=60)
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import os

from grafana_driver import GrafanaDriver
from posthog_driver import PostHogDriver


# =============================================================================
# Grafana Recipes
# =============================================================================

def find_unused_dashboards(
    driver: GrafanaDriver,
    days: int = 30
) -> List[Dict[str, Any]]:
    """
    Find Grafana dashboards that haven't been accessed recently.

    Heuristic: Dashboards without recent annotations are likely unused.

    Args:
        driver: GrafanaDriver instance
        days: Number of days to check

    Returns:
        List of potentially unused dashboards

    Example:
        driver = GrafanaDriver.from_env('http://localhost:8000')
        unused = find_unused_dashboards(driver, days=60)
        print(f"Found {len(unused)} unused dashboards")
    """
    all_dashboards = driver.search_dashboards()

    # Get recent annotations (proxy for dashboard activity)
    cutoff = datetime.now() - timedelta(days=days)
    annotations = driver.get_annotations(from_time=cutoff)

    # Dashboards with annotations are being used
    used_dashboard_ids = set(
        a['dashboardId'] for a in annotations
        if a.get('dashboardId')
    )

    # Find dashboards NOT in the used set
    unused = [
        d for d in all_dashboards
        if d['id'] not in used_dashboard_ids
    ]

    return unused


def find_dashboards_with_alerts(driver: GrafanaDriver) -> List[Dict[str, Any]]:
    """
    Find all dashboards that have alerts configured.

    Args:
        driver: GrafanaDriver instance

    Returns:
        List of dashboards with alerts

    Example:
        driver = GrafanaDriver.from_env('http://localhost:8000')
        alert_dashboards = find_dashboards_with_alerts(driver)
    """
    all_dashboards = driver.search_dashboards()
    dashboards_with_alerts = []

    for dash in all_dashboards:
        full_dash = driver.get_dashboard_by_uid(dash['uid'])
        dashboard_json = full_dash['dashboard']

        # Check if any panels have alerts
        has_alerts = any(
            panel.get('alert') is not None
            for panel in dashboard_json.get('panels', [])
        )

        if has_alerts:
            dashboards_with_alerts.append(dash)

    return dashboards_with_alerts


def export_all_dashboards_to_directory(
    driver: GrafanaDriver,
    output_dir: str = './grafana_backups'
) -> List[str]:
    """
    Export all Grafana dashboards to JSON files.

    Useful for backup, migration, or analysis.

    Args:
        driver: GrafanaDriver instance
        output_dir: Directory to save files

    Returns:
        List of saved file paths

    Example:
        driver = GrafanaDriver.from_env('http://localhost:8000')
        files = export_all_dashboards_to_directory(driver)
        print(f"Exported {len(files)} dashboards")
    """
    os.makedirs(output_dir, exist_ok=True)

    dashboards = driver.search_dashboards()
    saved_files = []

    for dash in dashboards:
        try:
            dashboard_json = driver.export_dashboard(dash['uid'])

            # Safe filename
            filename = f"{dash['uid']}.json"
            filepath = os.path.join(output_dir, filename)

            with open(filepath, 'w') as f:
                json.dump(dashboard_json, f, indent=2)

            saved_files.append(filepath)

        except Exception as e:
            print(f"Failed to export {dash['uid']}: {e}")

    return saved_files


def get_dashboard_summary(
    driver: GrafanaDriver,
    uid: str
) -> Dict[str, Any]:
    """
    Get a comprehensive summary of a dashboard.

    Args:
        driver: GrafanaDriver instance
        uid: Dashboard UID

    Returns:
        Summary dictionary with key metrics

    Example:
        driver = GrafanaDriver.from_env('http://localhost:8000')
        summary = get_dashboard_summary(driver, 'abc123')
        print(f"Dashboard has {summary['panel_count']} panels")
    """
    full_dash = driver.get_dashboard_by_uid(uid)
    dashboard_json = full_dash['dashboard']
    meta = full_dash['meta']

    panels = dashboard_json.get('panels', [])

    summary = {
        'uid': uid,
        'title': dashboard_json['title'],
        'tags': dashboard_json.get('tags', []),
        'panel_count': len(panels),
        'has_alerts': any(p.get('alert') for p in panels),
        'data_sources': list(set(
            target.get('datasource', {}).get('uid')
            for panel in panels
            for target in panel.get('targets', [])
            if target.get('datasource')
        )),
        'created': meta.get('created'),
        'updated': meta.get('updated'),
        'version': meta.get('version'),
        'is_starred': meta.get('isStarred', False),
        'folder': meta.get('folderTitle', 'General')
    }

    return summary


def find_dashboards_using_datasource(
    driver: GrafanaDriver,
    datasource_name: str
) -> List[Dict[str, Any]]:
    """
    Find all dashboards that use a specific data source.

    Args:
        driver: GrafanaDriver instance
        datasource_name: Name of data source

    Returns:
        List of dashboards using that data source

    Example:
        driver = GrafanaDriver.from_env('http://localhost:8000')
        dashboards = find_dashboards_using_datasource(driver, 'Prometheus')
    """
    # Get data source details
    datasource = driver.get_datasource_by_name(datasource_name)
    datasource_uid = datasource['uid']

    all_dashboards = driver.search_dashboards()
    using_dashboards = []

    for dash in all_dashboards:
        full_dash = driver.get_dashboard_by_uid(dash['uid'])
        dashboard_json = full_dash['dashboard']

        # Check all panels for this datasource
        uses_datasource = any(
            target.get('datasource', {}).get('uid') == datasource_uid
            for panel in dashboard_json.get('panels', [])
            for target in panel.get('targets', [])
        )

        if uses_datasource:
            using_dashboards.append(dash)

    return using_dashboards


# =============================================================================
# PostHog Recipes
# =============================================================================

def get_top_events(
    driver: PostHogDriver,
    days: int = 7,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Get the most frequent events in the last N days.

    Args:
        driver: PostHogDriver instance
        days: Number of days to analyze
        limit: Number of top events to return

    Returns:
        List of events sorted by volume

    Example:
        driver = PostHogDriver.from_env()
        top_events = get_top_events(driver, days=7)
        for event in top_events:
            print(f"{event['name']}: {event['volume_30_day']:,} events/month")
    """
    event_definitions = driver.get_event_definitions()

    # Sort by volume
    sorted_events = sorted(
        event_definitions,
        key=lambda e: e.get('volume_30_day', 0),
        reverse=True
    )

    return sorted_events[:limit]


def find_active_feature_flags(driver: PostHogDriver) -> List[Dict[str, Any]]:
    """
    Get all active feature flags.

    Args:
        driver: PostHogDriver instance

    Returns:
        List of active feature flags

    Example:
        driver = PostHogDriver.from_env()
        active_flags = find_active_feature_flags(driver)
        print(f"{len(active_flags)} active feature flags")
    """
    all_flags = driver.list_feature_flags()

    active = [
        flag for flag in all_flags
        if flag['active']
    ]

    return active


def analyze_event_frequency(
    driver: PostHogDriver,
    event_name: str,
    days: int = 7
) -> Dict[str, Any]:
    """
    Analyze frequency of a specific event over time.

    Args:
        driver: PostHogDriver instance
        event_name: Name of event to analyze
        days: Number of days to analyze

    Returns:
        Dictionary with analysis results

    Example:
        driver = PostHogDriver.from_env()
        analysis = analyze_event_frequency(driver, '$pageview', days=7)
        print(f"Average: {analysis['avg_per_day']} events/day")
    """
    events = driver.query_events(
        event=event_name,
        date_from=datetime.now() - timedelta(days=days),
        date_to=datetime.now(),
        limit=10000
    )

    # Group by day
    events_by_day = {}
    for event in events:
        event_time = datetime.fromisoformat(event['timestamp'])
        day = event_time.date()
        events_by_day[day] = events_by_day.get(day, 0) + 1

    return {
        'event_name': event_name,
        'total_events': len(events),
        'days_analyzed': days,
        'avg_per_day': len(events) / days,
        'events_by_day': events_by_day,
        'peak_day': max(events_by_day.items(), key=lambda x: x[1]) if events_by_day else None
    }


# =============================================================================
# Cross-Platform Recipes
# =============================================================================

def correlate_deployments_with_errors(
    grafana_driver: GrafanaDriver,
    posthog_driver: PostHogDriver,
    hours: int = 24
) -> List[Dict[str, Any]]:
    """
    Find if Grafana deployment annotations correlate with PostHog error events.

    Args:
        grafana_driver: GrafanaDriver instance
        posthog_driver: PostHogDriver instance
        hours: Hours to analyze

    Returns:
        List of deployments with error counts

    Example:
        grafana = GrafanaDriver.from_env('http://localhost:8000')
        posthog = PostHogDriver.from_env()
        correlations = correlate_deployments_with_errors(grafana, posthog, hours=48)
        for c in correlations:
            print(f"{c['deployment']}: {c['errors_in_next_hour']} errors")
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
        date_from=cutoff,
        date_to=datetime.now()
    )

    # Correlate: for each deployment, count errors in next hour
    results = []
    for annotation in annotations:
        deploy_time = datetime.fromtimestamp(annotation['time'] / 1000)

        errors_after = [
            e for e in error_events
            if (deploy_time <
                datetime.fromisoformat(e['timestamp']) <
                deploy_time + timedelta(hours=1))
        ]

        results.append({
            'deployment': annotation['text'],
            'time': deploy_time.isoformat(),
            'errors_in_next_hour': len(errors_after),
            'error_spike': len(errors_after) > 10  # Threshold
        })

    return results


def compare_monitoring_vs_analytics(
    grafana_driver: GrafanaDriver,
    posthog_driver: PostHogDriver
) -> Dict[str, Any]:
    """
    Compare Grafana monitoring data with PostHog analytics data.

    Useful for understanding if monitoring aligns with user experience.

    Args:
        grafana_driver: GrafanaDriver instance
        posthog_driver: PostHogDriver instance

    Returns:
        Comparison report

    Example:
        grafana = GrafanaDriver.from_env('http://localhost:8000')
        posthog = PostHogDriver.from_env()
        comparison = compare_monitoring_vs_analytics(grafana, posthog)
    """
    # Get Grafana incidents (annotations tagged 'incident')
    cutoff = datetime.now() - timedelta(days=7)
    incidents = grafana_driver.get_annotations(
        from_time=cutoff,
        tags=['incident']
    )

    # Get PostHog error events
    errors = posthog_driver.query_events(
        event='error_occurred',
        date_from=cutoff
    )

    # Get PostHog pageviews
    pageviews = posthog_driver.query_events(
        event='$pageview',
        date_from=cutoff
    )

    return {
        'period': '7 days',
        'incidents_reported': len(incidents),
        'user_errors': len(errors),
        'total_pageviews': len(pageviews),
        'error_rate': len(errors) / len(pageviews) if pageviews else 0,
        'incidents': [
            {
                'text': i['text'],
                'time': datetime.fromtimestamp(i['time'] / 1000).isoformat()
            }
            for i in incidents
        ]
    }


# =============================================================================
# Helper Utilities
# =============================================================================

def format_dashboard_report(dashboards: List[Dict[str, Any]]) -> str:
    """Format list of dashboards as readable report."""
    if not dashboards:
        return "No dashboards found."

    report = f"Found {len(dashboards)} dashboards:\n\n"

    for i, dash in enumerate(dashboards, 1):
        tags_str = ', '.join(dash.get('tags', []))
        report += f"{i}. {dash['title']}\n"
        report += f"   UID: {dash['uid']}\n"
        report += f"   Tags: [{tags_str}]\n"
        if dash.get('folderTitle'):
            report += f"   Folder: {dash['folderTitle']}\n"
        report += "\n"

    return report


def format_event_report(events: List[Dict[str, Any]]) -> str:
    """Format list of events as readable report."""
    if not events:
        return "No events found."

    report = f"Found {len(events)} events:\n\n"

    for i, event in enumerate(events[:20], 1):  # Limit to 20 for readability
        report += f"{i}. {event['event']}\n"
        report += f"   Time: {event['timestamp']}\n"
        report += f"   User: {event['distinct_id']}\n"
        if event.get('properties'):
            report += f"   Properties: {event['properties']}\n"
        report += "\n"

    if len(events) > 20:
        report += f"... and {len(events) - 20} more events\n"

    return report


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == '__main__':
    """
    Examples showing how Claude Agent SDK can use these recipes.
    """
    print("Driver Recipe Examples\n" + "=" * 60 + "\n")

    print("Recipes available:")
    print("1. find_unused_dashboards() - Find stale dashboards")
    print("2. find_dashboards_with_alerts() - Find alert dashboards")
    print("3. export_all_dashboards_to_directory() - Backup all dashboards")
    print("4. get_dashboard_summary() - Detailed dashboard info")
    print("5. find_dashboards_using_datasource() - Find dashboards by datasource")
    print("6. get_top_events() - Most frequent PostHog events")
    print("7. find_active_feature_flags() - Active feature flags")
    print("8. analyze_event_frequency() - Event frequency analysis")
    print("9. correlate_deployments_with_errors() - Cross-platform correlation")
    print("10. compare_monitoring_vs_analytics() - Monitoring vs analytics report")
    print()

    print("=" * 60)
    print("\nClaude Agent SDK can:")
    print("- Import these recipes directly")
    print("- Modify them for specific needs")
    print("- Combine multiple recipes")
    print("- Use them as templates for new functionality")
