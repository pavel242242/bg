"""
PostHog Driver Recipe Collection - Common Patterns for Claude Agent SDK

These are ready-to-use patterns that Claude Agent SDK can import and use directly,
or modify to fulfill specific user requests. Think of these as examples that show
how to combine driver methods to accomplish common tasks.

Claude Agent SDK runs in the same E2B sandbox as the drivers, so it can:
- Import these recipes directly
- Modify them for specific needs
- Use them as templates for new functionality
- Combine multiple recipes

Usage:
    from driver_recipes import find_power_users
    from posthog_driver import PostHogDriver

    driver = PostHogDriver.from_env()
    power_users = find_power_users(driver, action='signup', frequency=5, weeks=4)
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json

from posthog_driver import PostHogDriver


# =============================================================================
# PostHog Recipes - User Segmentation
# =============================================================================

def find_power_users(
    driver: PostHogDriver,
    action: str,
    frequency: int = 5,
    weeks: int = 7
) -> List[Dict[str, Any]]:
    """
    Find power users who performed an action frequently.

    Example: "Who are our power users?" (users who completed signup 5+ times in last 7 weeks)

    Args:
        driver: PostHogDriver instance
        action: Event name to track
        frequency: Minimum number of times action performed
        weeks: Time period to analyze

    Returns:
        List of power user IDs with their activity counts

    Example:
        driver = PostHogDriver.from_env()
        power_users = find_power_users(driver, 'completed_onboarding', frequency=5, weeks=4)
        print(f"Found {len(power_users)} power users")
    """
    date_from = datetime.now() - timedelta(weeks=weeks)

    events = driver.query_events(
        event=action,
        date_from=date_from,
        date_to=datetime.now(),
        limit=10000
    )

    # Count events per user
    user_counts = {}
    for event in events:
        user_id = event['distinct_id']
        user_counts[user_id] = user_counts.get(user_id, 0) + 1

    # Filter users who meet frequency threshold
    power_users = [
        {'user_id': user_id, 'event_count': count}
        for user_id, count in user_counts.items()
        if count >= frequency
    ]

    # Sort by event count
    power_users.sort(key=lambda x: x['event_count'], reverse=True)

    return power_users


def find_churn_risk_users(
    driver: PostHogDriver,
    key_event: str,
    days_inactive: int = 30
) -> List[Dict[str, Any]]:
    """
    Find users at risk of churning (stopped doing key event).

    Example: "Which users might churn?" (users who logged in before but not in last 30 days)

    Args:
        driver: PostHogDriver instance
        key_event: Event that indicates active usage (e.g., 'login', '$pageview')
        days_inactive: Days without activity to consider churn risk

    Returns:
        List of at-risk users

    Example:
        driver = PostHogDriver.from_env()
        at_risk = find_churn_risk_users(driver, 'login', days_inactive=14)
    """
    cutoff = datetime.now() - timedelta(days=days_inactive)

    # Get recent active users
    recent_events = driver.query_events(
        event=key_event,
        date_from=cutoff,
        limit=10000
    )
    recent_users = set(e['distinct_id'] for e in recent_events)

    # Get all historical users (e.g., last 90 days)
    historical_events = driver.query_events(
        event=key_event,
        date_from=datetime.now() - timedelta(days=90),
        date_to=cutoff,
        limit=10000
    )
    historical_users = set(e['distinct_id'] for e in historical_events)

    # Users who were active before but not recently = churn risk
    at_risk_users = historical_users - recent_users

    return [{'user_id': user_id} for user_id in at_risk_users]


def get_user_journey(
    driver: PostHogDriver,
    user_id: str,
    days: int = 30
) -> List[Dict[str, Any]]:
    """
    Get complete event history for a user.

    Example: "What does this user's journey look like?" (for support, debugging)

    Args:
        driver: PostHogDriver instance
        user_id: User distinct ID
        days: Days of history to retrieve

    Returns:
        List of events in chronological order

    Example:
        driver = PostHogDriver.from_env()
        journey = get_user_journey(driver, 'user@example.com', days=7)
        for event in journey:
            print(f"{event['timestamp']}: {event['event']}")
    """
    # Get person details first (if available)
    try:
        person = driver.get_person(user_id)
    except:
        person = None

    # Get all events for this user
    events = driver.query_events(
        date_from=datetime.now() - timedelta(days=days),
        limit=10000
    )

    # Filter events for this specific user
    user_events = [e for e in events if e['distinct_id'] == user_id]

    # Sort chronologically
    user_events.sort(key=lambda e: e['timestamp'])

    return user_events


# =============================================================================
# PostHog Recipes - Analytics & Insights
# =============================================================================

def get_top_events(
    driver: PostHogDriver,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Get the most frequent events.

    Example: "What are our top events?" (by volume)

    Args:
        driver: PostHogDriver instance
        limit: Number of top events to return

    Returns:
        List of events sorted by volume

    Example:
        driver = PostHogDriver.from_env()
        top_events = get_top_events(driver, limit=10)
        for event in top_events:
            print(f"{event['name']}: {event['volume_30_day']:,} events/month")
    """
    event_definitions = driver.get_event_definitions()

    # Sort by 30-day volume
    sorted_events = sorted(
        event_definitions,
        key=lambda e: e.get('volume_30_day', 0),
        reverse=True
    )

    return sorted_events[:limit]


def analyze_event_frequency(
    driver: PostHogDriver,
    event_name: str,
    days: int = 7
) -> Dict[str, Any]:
    """
    Analyze frequency of a specific event over time.

    Example: "How often does X event happen?" (trend analysis)

    Args:
        driver: PostHogDriver instance
        event_name: Name of event to analyze
        days: Number of days to analyze

    Returns:
        Dictionary with analysis results (total, avg/day, by-day breakdown)

    Example:
        driver = PostHogDriver.from_env()
        analysis = analyze_event_frequency(driver, '$pageview', days=7)
        print(f"Average: {analysis['avg_per_day']:.1f} events/day")
    """
    events = driver.query_events(
        event=event_name,
        date_from=datetime.now() - timedelta(days=days),
        date_to=datetime.now(),
        limit=100000
    )

    # Group by day
    events_by_day = {}
    for event in events:
        event_time = datetime.fromisoformat(event['timestamp'])
        day = event_time.date()
        events_by_day[day] = events_by_day.get(day, 0) + 1

    peak_day = max(events_by_day.items(), key=lambda x: x[1]) if events_by_day else (None, 0)

    return {
        'event_name': event_name,
        'total_events': len(events),
        'days_analyzed': days,
        'avg_per_day': len(events) / days if days > 0 else 0,
        'events_by_day': events_by_day,
        'peak_day': peak_day[0],
        'peak_day_count': peak_day[1]
    }


def find_error_patterns(
    driver: PostHogDriver,
    error_event: str = 'error_occurred',
    days: int = 7
) -> Dict[str, Any]:
    """
    Analyze error events to find patterns.

    Example: "What errors are affecting users most?" (error tracking)

    Args:
        driver: PostHogDriver instance
        error_event: Name of error event
        days: Days to analyze

    Returns:
        Dictionary with error analysis (count, affected users, common properties)

    Example:
        driver = PostHogDriver.from_env()
        errors = find_error_patterns(driver, 'error_occurred', days=7)
        print(f"Total errors: {errors['total_errors']}")
        print(f"Affected users: {errors['affected_users']}")
    """
    events = driver.query_events(
        event=error_event,
        date_from=datetime.now() - timedelta(days=days),
        limit=10000
    )

    affected_users = set(e['distinct_id'] for e in events)

    # Analyze error properties (if available)
    error_types = {}
    for event in events:
        props = event.get('properties', {})
        error_type = props.get('error_type', 'Unknown')
        error_types[error_type] = error_types.get(error_type, 0) + 1

    return {
        'total_errors': len(events),
        'affected_users': len(affected_users),
        'days_analyzed': days,
        'error_types': error_types,
        'errors_per_day': len(events) / days if days > 0 else 0
    }


# =============================================================================
# PostHog Recipes - Feature Flags & Experiments
# =============================================================================

def find_active_feature_flags(driver: PostHogDriver) -> List[Dict[str, Any]]:
    """
    Get all active feature flags.

    Example: "What features are currently live?" (feature flag management)

    Args:
        driver: PostHogDriver instance

    Returns:
        List of active feature flags

    Example:
        driver = PostHogDriver.from_env()
        active_flags = find_active_feature_flags(driver)
        for flag in active_flags:
            print(f"{flag['key']}: {flag['name']}")
    """
    all_flags = driver.list_feature_flags()

    active = [
        flag for flag in all_flags
        if flag['active']
    ]

    return active


def analyze_feature_flag_impact(
    driver: PostHogDriver,
    flag_key: str,
    metric_event: str,
    days: int = 7
) -> Dict[str, Any]:
    """
    Analyze the impact of a feature flag on a metric.

    Example: "Did this feature flag improve metrics?" (A/B testing)

    Args:
        driver: PostHogDriver instance
        flag_key: Feature flag key
        metric_event: Event to measure (e.g., 'purchase_completed')
        days: Days to analyze

    Returns:
        Dictionary with comparison of users with/without flag

    Example:
        driver = PostHogDriver.from_env()
        impact = analyze_feature_flag_impact(driver, 'new-checkout', 'purchase_completed')
        print(f"With flag: {impact['with_flag_rate']:.2%}")
        print(f"Without flag: {impact['without_flag_rate']:.2%}")
    """
    # Note: This is a simplified implementation
    # Real implementation would use PostHog's experiment analysis
    # or track flag evaluations in event properties

    events = driver.query_events(
        event=metric_event,
        date_from=datetime.now() - timedelta(days=days),
        limit=10000
    )

    # Check if events have flag information in properties
    with_flag = [e for e in events if e.get('properties', {}).get(f'$feature/{flag_key}')]
    without_flag = [e for e in events if not e.get('properties', {}).get(f'$feature/{flag_key}')]

    total_users = len(set(e['distinct_id'] for e in events))
    users_with_flag = len(set(e['distinct_id'] for e in with_flag))
    users_without_flag = len(set(e['distinct_id'] for e in without_flag))

    return {
        'flag_key': flag_key,
        'metric_event': metric_event,
        'days_analyzed': days,
        'total_events': len(events),
        'events_with_flag': len(with_flag),
        'events_without_flag': len(without_flag),
        'with_flag_rate': len(with_flag) / users_with_flag if users_with_flag > 0 else 0,
        'without_flag_rate': len(without_flag) / users_without_flag if users_without_flag > 0 else 0
    }


# =============================================================================
# PostHog Recipes - Cohort Analysis
# =============================================================================

def compare_cohort_behavior(
    driver: PostHogDriver,
    cohort_a_id: int,
    cohort_b_id: int,
    metric_event: str,
    days: int = 30
) -> Dict[str, Any]:
    """
    Compare behavior between two cohorts.

    Example: "How do paid vs free users compare?" (cohort analysis)

    Args:
        driver: PostHogDriver instance
        cohort_a_id: First cohort ID
        cohort_b_id: Second cohort ID
        metric_event: Event to compare
        days: Days to analyze

    Returns:
        Dictionary comparing the two cohorts

    Example:
        driver = PostHogDriver.from_env()
        comparison = compare_cohort_behavior(driver, cohort_a=1, cohort_b=2, metric_event='purchase')
    """
    cohort_a = driver.get_cohort(cohort_a_id)
    cohort_b = driver.get_cohort(cohort_b_id)

    events = driver.query_events(
        event=metric_event,
        date_from=datetime.now() - timedelta(days=days),
        limit=10000
    )

    # Note: Simplified - would need to get cohort membership from PostHog
    # This is a placeholder showing the pattern

    return {
        'cohort_a': cohort_a['name'],
        'cohort_b': cohort_b['name'],
        'metric_event': metric_event,
        'days_analyzed': days,
        'total_events': len(events)
    }


# =============================================================================
# Helper Utilities
# =============================================================================

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
            report += f"   Properties: {json.dumps(event['properties'], indent=6)}\n"
        report += "\n"

    if len(events) > 20:
        report += f"... and {len(events) - 20} more events\n"

    return report


def format_user_list(users: List[Dict[str, Any]]) -> str:
    """Format list of users as readable report."""
    if not users:
        return "No users found."

    report = f"Found {len(users)} users:\n\n"

    for i, user in enumerate(users[:50], 1):
        user_id = user.get('user_id', user.get('distinct_id', 'Unknown'))
        count = user.get('event_count', '')
        report += f"{i}. {user_id}"
        if count:
            report += f" ({count} events)"
        report += "\n"

    if len(users) > 50:
        report += f"... and {len(users) - 50} more users\n"

    return report


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == '__main__':
    """
    Examples showing how Claude Agent SDK can use these recipes.
    """
    print("PostHog Driver Recipe Examples\n" + "=" * 60 + "\n")

    print("Recipes available:")
    print("1. find_power_users() - Find users with high activity")
    print("2. find_churn_risk_users() - Find users who stopped activity")
    print("3. get_user_journey() - Get user's complete event history")
    print("4. get_top_events() - Most frequent events by volume")
    print("5. analyze_event_frequency() - Event frequency over time")
    print("6. find_error_patterns() - Analyze error events")
    print("7. find_active_feature_flags() - List active feature flags")
    print("8. analyze_feature_flag_impact() - Measure flag impact")
    print("9. compare_cohort_behavior() - Compare user cohorts")
    print()

    print("=" * 60)
    print("\nClaude Agent SDK can:")
    print("- Import these recipes directly")
    print("- Modify them for specific needs")
    print("- Combine multiple recipes")
    print("- Use them as templates for new functionality")
