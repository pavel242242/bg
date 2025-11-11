"""
PostHog API Driver - Product Analytics and Feature Flags

Provides access to PostHog events, insights, feature flags, and analytics data.
Supports both PostHog Cloud and self-hosted instances.

API Documentation: https://posthog.com/docs/api
"""

import os
from typing import Optional, Dict, Any, List, Iterator
from datetime import datetime, timedelta
from urllib.parse import urlencode

from base_driver import (
    PaginatedDriver,
    AuthConfig,
    AuthStrategy,
    create_auth_config_from_env,
    ResourceNotFoundError,
    QueryError,
    PaginationStrategy
)


class PostHogDriver(PaginatedDriver):
    """
    Driver for PostHog API data extraction.

    Provides methods to:
    - Query events and analytics data
    - Access insights and dashboards
    - Retrieve feature flags and experiments
    - Export cohorts and persons
    - Query session recordings metadata

    Example:
        # Using environment variable
        driver = PostHogDriver.from_env()

        # Using explicit token
        auth = AuthConfig(
            AuthStrategy.BEARER_TOKEN,
            {'token': 'phc_xxxxx'}
        )
        driver = PostHogDriver('https://app.posthog.com', auth, project_id=12345)

        # Query events
        events = driver.query_events(
            event='$pageview',
            date_from=datetime.now() - timedelta(days=7),
            date_to=datetime.now()
        )

        # Get feature flags
        flags = driver.list_feature_flags()

        # Query insights
        insight = driver.get_insight(123)
    """

    def __init__(
        self,
        base_url: str,
        auth_config: AuthConfig,
        project_id: Optional[int] = None,
        timeout: int = 30,
        verify_ssl: bool = True
    ):
        """
        Initialize PostHog driver.

        Args:
            base_url: PostHog instance URL (e.g., 'https://app.posthog.com')
            auth_config: Authentication configuration (Personal API Key)
            project_id: Default project ID for queries
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
        """
        # Ensure API path is included
        if not base_url.endswith('/api'):
            base_url = f"{base_url.rstrip('/')}/api"

        super().__init__(base_url, auth_config, timeout, verify_ssl)
        self.project_id = project_id

    @classmethod
    def from_env(
        cls,
        base_url: str = 'https://app.posthog.com',
        env_var: str = 'POSTHOG_API_KEY',
        project_id: Optional[int] = None,
        timeout: int = 30
    ) -> 'PostHogDriver':
        """
        Create driver from environment variable.

        Args:
            base_url: PostHog instance URL (default: PostHog Cloud)
            env_var: Environment variable name for API key
            project_id: Default project ID
            timeout: Request timeout in seconds

        Returns:
            Initialized PostHogDriver

        Raises:
            AuthError: If environment variable is not set
        """
        auth_config = create_auth_config_from_env(
            AuthStrategy.BEARER_TOKEN,
            env_var
        )

        # Try to get project ID from env if not provided
        if project_id is None:
            project_id_str = os.getenv('POSTHOG_PROJECT_ID')
            if project_id_str:
                project_id = int(project_id_str)

        return cls(base_url, auth_config, project_id, timeout)

    def test_connection(self) -> bool:
        """
        Test connection to PostHog API.

        Returns:
            True if connection is successful

        Raises:
            ConnectionError: If connection fails
            AuthError: If authentication fails
        """
        # Try to get current user
        response = self._get('users/@me')
        return 'id' in response

    def _ensure_project_id(self, project_id: Optional[int] = None) -> int:
        """
        Ensure a project ID is available.

        Args:
            project_id: Optional project ID override

        Returns:
            Project ID to use

        Raises:
            ValueError: If no project ID is available
        """
        pid = project_id or self.project_id
        if pid is None:
            raise ValueError(
                "Project ID required. Provide project_id parameter or set "
                "during driver initialization."
            )
        return pid

    # ========================================================================
    # Project Operations
    # ========================================================================

    def list_projects(self) -> List[Dict[str, Any]]:
        """
        List all accessible projects.

        Returns:
            List of project objects

        Example:
            projects = driver.list_projects()
            for project in projects:
                print(f"{project['id']}: {project['name']}")
        """
        response = self._get('projects')
        return response.get('results', [])

    def get_project(self, project_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get project details.

        Args:
            project_id: Project ID (uses default if not provided)

        Returns:
            Project object
        """
        pid = self._ensure_project_id(project_id)
        return self._get(f'projects/{pid}')

    # ========================================================================
    # Event Operations
    # ========================================================================

    def query_events(
        self,
        event: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        properties: Optional[Dict[str, Any]] = None,
        project_id: Optional[int] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Query events with filters.

        Args:
            event: Event name filter
            date_from: Start date for query
            date_to: End date for query
            properties: Property filters (e.g., {'$browser': 'Chrome'})
            project_id: Project ID (uses default if not provided)
            limit: Maximum number of results

        Returns:
            List of event objects

        Example:
            # Get all pageview events from last 7 days
            events = driver.query_events(
                event='$pageview',
                date_from=datetime.now() - timedelta(days=7),
                date_to=datetime.now(),
                properties={'$current_url': {'$icontains': '/dashboard'}}
            )
        """
        pid = self._ensure_project_id(project_id)

        params = {'limit': limit}

        if event:
            params['event'] = event
        if date_from:
            params['after'] = date_from.isoformat()
        if date_to:
            params['before'] = date_to.isoformat()
        if properties:
            params['properties'] = properties

        response = self._get(f'projects/{pid}/events', params=params)
        return response.get('results', [])

    def get_event_definitions(
        self,
        project_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all event definitions.

        Args:
            project_id: Project ID (uses default if not provided)

        Returns:
            List of event definitions

        Example:
            events = driver.get_event_definitions()
            for event in events:
                print(f"{event['name']}: {event['volume_30_day']} events/month")
        """
        pid = self._ensure_project_id(project_id)
        response = self._get(f'projects/{pid}/event_definitions')
        return response.get('results', [])

    def get_event_properties(
        self,
        event_name: str,
        project_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get properties for a specific event.

        Args:
            event_name: Event name
            project_id: Project ID (uses default if not provided)

        Returns:
            List of property definitions
        """
        pid = self._ensure_project_id(project_id)
        response = self._get(
            f'projects/{pid}/property_definitions',
            params={'event_names': [event_name]}
        )
        return response.get('results', [])

    # ========================================================================
    # Insight Operations
    # ========================================================================

    def list_insights(
        self,
        project_id: Optional[int] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List all insights (saved queries/charts).

        Args:
            project_id: Project ID (uses default if not provided)
            limit: Maximum number of results

        Returns:
            List of insight objects

        Example:
            insights = driver.list_insights()
            for insight in insights:
                print(f"{insight['name']}: {insight['filters']}")
        """
        pid = self._ensure_project_id(project_id)
        response = self._get(f'projects/{pid}/insights', params={'limit': limit})
        return response.get('results', [])

    def get_insight(
        self,
        insight_id: int,
        project_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get a specific insight.

        Args:
            insight_id: Insight ID
            project_id: Project ID (uses default if not provided)

        Returns:
            Insight object with results
        """
        pid = self._ensure_project_id(project_id)
        return self._get(f'projects/{pid}/insights/{insight_id}')

    def query_insight(
        self,
        filters: Dict[str, Any],
        project_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute an ad-hoc insight query.

        Args:
            filters: PostHog filter object
            project_id: Project ID (uses default if not provided)

        Returns:
            Query results

        Example:
            # Trend query for pageviews
            results = driver.query_insight({
                'insight': 'TRENDS',
                'events': [{'id': '$pageview'}],
                'date_from': '-7d',
                'date_to': 'now'
            })
        """
        pid = self._ensure_project_id(project_id)
        return self._post(f'projects/{pid}/insights/trend', json=filters)

    # ========================================================================
    # Dashboard Operations
    # ========================================================================

    def list_dashboards(
        self,
        project_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        List all dashboards.

        Args:
            project_id: Project ID (uses default if not provided)

        Returns:
            List of dashboard objects
        """
        pid = self._ensure_project_id(project_id)
        response = self._get(f'projects/{pid}/dashboards')
        return response.get('results', [])

    def get_dashboard(
        self,
        dashboard_id: int,
        project_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get a specific dashboard.

        Args:
            dashboard_id: Dashboard ID
            project_id: Project ID (uses default if not provided)

        Returns:
            Dashboard object with tiles
        """
        pid = self._ensure_project_id(project_id)
        return self._get(f'projects/{pid}/dashboards/{dashboard_id}')

    # ========================================================================
    # Feature Flag Operations
    # ========================================================================

    def list_feature_flags(
        self,
        project_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        List all feature flags.

        Args:
            project_id: Project ID (uses default if not provided)

        Returns:
            List of feature flag objects

        Example:
            flags = driver.list_feature_flags()
            for flag in flags:
                print(f"{flag['key']}: {flag['active']}")
        """
        pid = self._ensure_project_id(project_id)
        response = self._get(f'projects/{pid}/feature_flags')
        return response.get('results', [])

    def get_feature_flag(
        self,
        flag_id: int,
        project_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get a specific feature flag.

        Args:
            flag_id: Feature flag ID
            project_id: Project ID (uses default if not provided)

        Returns:
            Feature flag object
        """
        pid = self._ensure_project_id(project_id)
        return self._get(f'projects/{pid}/feature_flags/{flag_id}')

    def evaluate_feature_flag(
        self,
        flag_key: str,
        distinct_id: str,
        project_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Evaluate a feature flag for a user.

        Args:
            flag_key: Feature flag key
            distinct_id: User distinct ID
            project_id: Project ID (uses default if not provided)

        Returns:
            Evaluation result
        """
        pid = self._ensure_project_id(project_id)
        return self._post(
            f'projects/{pid}/feature_flags/local_evaluation',
            json={'flag_key': flag_key, 'distinct_id': distinct_id}
        )

    # ========================================================================
    # Cohort Operations
    # ========================================================================

    def list_cohorts(
        self,
        project_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        List all cohorts.

        Args:
            project_id: Project ID (uses default if not provided)

        Returns:
            List of cohort objects
        """
        pid = self._ensure_project_id(project_id)
        response = self._get(f'projects/{pid}/cohorts')
        return response.get('results', [])

    def get_cohort(
        self,
        cohort_id: int,
        project_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get a specific cohort.

        Args:
            cohort_id: Cohort ID
            project_id: Project ID (uses default if not provided)

        Returns:
            Cohort object
        """
        pid = self._ensure_project_id(project_id)
        return self._get(f'projects/{pid}/cohorts/{cohort_id}')

    # ========================================================================
    # Person Operations
    # ========================================================================

    def list_persons(
        self,
        project_id: Optional[int] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List persons (users).

        Args:
            project_id: Project ID (uses default if not provided)
            limit: Maximum number of results

        Returns:
            List of person objects
        """
        pid = self._ensure_project_id(project_id)
        response = self._get(f'projects/{pid}/persons', params={'limit': limit})
        return response.get('results', [])

    def get_person(
        self,
        person_id: str,
        project_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get a specific person.

        Args:
            person_id: Person ID or distinct_id
            project_id: Project ID (uses default if not provided)

        Returns:
            Person object
        """
        pid = self._ensure_project_id(project_id)
        return self._get(f'projects/{pid}/persons/{person_id}')

    def get_person_properties(
        self,
        project_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all person property definitions.

        Args:
            project_id: Project ID (uses default if not provided)

        Returns:
            List of property definitions
        """
        pid = self._ensure_project_id(project_id)
        response = self._get(f'projects/{pid}/property_definitions')
        return response.get('results', [])

    # ========================================================================
    # Session Recording Operations
    # ========================================================================

    def list_session_recordings(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        project_id: Optional[int] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List session recordings (metadata only).

        Args:
            date_from: Start date filter
            date_to: End date filter
            project_id: Project ID (uses default if not provided)
            limit: Maximum number of results

        Returns:
            List of session recording metadata
        """
        pid = self._ensure_project_id(project_id)

        params = {'limit': limit}
        if date_from:
            params['date_from'] = date_from.isoformat()
        if date_to:
            params['date_to'] = date_to.isoformat()

        response = self._get(f'projects/{pid}/session_recordings', params=params)
        return response.get('results', [])

    def get_session_recording(
        self,
        recording_id: str,
        project_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get a specific session recording.

        Args:
            recording_id: Recording ID
            project_id: Project ID (uses default if not provided)

        Returns:
            Session recording object
        """
        pid = self._ensure_project_id(project_id)
        return self._get(f'projects/{pid}/session_recordings/{recording_id}')

    # ========================================================================
    # Experiment Operations
    # ========================================================================

    def list_experiments(
        self,
        project_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        List all experiments.

        Args:
            project_id: Project ID (uses default if not provided)

        Returns:
            List of experiment objects
        """
        pid = self._ensure_project_id(project_id)
        response = self._get(f'projects/{pid}/experiments')
        return response.get('results', [])

    def get_experiment(
        self,
        experiment_id: int,
        project_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get a specific experiment.

        Args:
            experiment_id: Experiment ID
            project_id: Project ID (uses default if not provided)

        Returns:
            Experiment object with results
        """
        pid = self._ensure_project_id(project_id)
        return self._get(f'projects/{pid}/experiments/{experiment_id}')

    # ========================================================================
    # Utility Methods
    # ========================================================================

    def get_current_user(self) -> Dict[str, Any]:
        """
        Get current user details.

        Returns:
            User object
        """
        return self._get('users/@me')

    def get_organization(self) -> Dict[str, Any]:
        """
        Get current organization details.

        Returns:
            Organization object
        """
        # Get from current user's organization
        user = self.get_current_user()
        org_id = user.get('organization')
        if org_id:
            return self._get(f'organizations/{org_id}')
        return {}

    # ========================================================================
    # Pagination Overrides
    # ========================================================================

    def _extract_items(self, response: Dict[str, Any]) -> list:
        """Extract items from PostHog paginated response."""
        return response.get('results', [])

    def _extract_next_cursor(self, response: Dict[str, Any]) -> Optional[str]:
        """Extract next page URL from PostHog response."""
        return response.get('next')
