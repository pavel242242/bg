"""
Grafana API Driver - Data Extraction and Monitoring Integration

Provides access to Grafana dashboards, data sources, and annotations.
Supports both Grafana Cloud and self-hosted instances.

API Documentation: https://grafana.com/docs/grafana/latest/developers/http_api/
"""

import os
from typing import Optional, Dict, Any, List, Iterator
from datetime import datetime, timedelta

from base_driver import (
    PaginatedDriver,
    AuthConfig,
    AuthStrategy,
    create_auth_config_from_env,
    ResourceNotFoundError,
    QueryError
)


class GrafanaDriver(PaginatedDriver):
    """
    Driver for Grafana API data extraction.

    Provides methods to:
    - List and retrieve dashboards
    - Query data sources
    - Access annotations
    - Search organizations and folders
    - Export dashboard configurations

    Example:
        # Using environment variable
        driver = GrafanaDriver.from_env('https://my-instance.grafana.net')

        # Using explicit token
        auth = AuthConfig(
            AuthStrategy.BEARER_TOKEN,
            {'token': 'glsa_xxxxx'}
        )
        driver = GrafanaDriver('https://my-instance.grafana.net', auth)

        # List all dashboards
        dashboards = driver.search_dashboards()

        # Get specific dashboard
        dashboard = driver.get_dashboard('dashboard-uid')

        # Query annotations
        annotations = driver.get_annotations(
            from_time=datetime.now() - timedelta(days=7),
            to_time=datetime.now()
        )
    """

    def __init__(
        self,
        base_url: str,
        auth_config: AuthConfig,
        timeout: int = 30,
        verify_ssl: bool = True
    ):
        """
        Initialize Grafana driver.

        Args:
            base_url: Grafana instance URL (e.g., 'https://my-instance.grafana.net')
            auth_config: Authentication configuration (Bearer token or API key)
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
        """
        # Ensure API path is included
        if not base_url.endswith('/api'):
            base_url = f"{base_url.rstrip('/')}/api"

        super().__init__(base_url, auth_config, timeout, verify_ssl)

    @classmethod
    def from_env(
        cls,
        base_url: str,
        env_var: str = 'GRAFANA_TOKEN',
        timeout: int = 30
    ) -> 'GrafanaDriver':
        """
        Create driver from environment variable.

        Args:
            base_url: Grafana instance URL
            env_var: Environment variable name for token (default: GRAFANA_TOKEN)
            timeout: Request timeout in seconds

        Returns:
            Initialized GrafanaDriver

        Raises:
            AuthError: If environment variable is not set
        """
        auth_config = create_auth_config_from_env(
            AuthStrategy.BEARER_TOKEN,
            env_var
        )
        return cls(base_url, auth_config, timeout)

    def test_connection(self) -> bool:
        """
        Test connection to Grafana API.

        Returns:
            True if connection is successful

        Raises:
            ConnectionError: If connection fails
            AuthError: If authentication fails
        """
        # Use health endpoint
        response = self._get('health')
        return response.get('database') == 'ok'

    # ========================================================================
    # Dashboard Operations
    # ========================================================================

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
            query: Search query string
            tag: Filter by tag
            starred: Show only starred dashboards
            limit: Maximum number of results

        Returns:
            List of dashboard metadata dictionaries

        Example:
            dashboards = driver.search_dashboards(query='sales', tag='production')
        """
        params = {
            'type': 'dash-db',
            'limit': limit
        }

        if query:
            params['query'] = query
        if tag:
            params['tag'] = tag
        if starred:
            params['starred'] = 'true'

        return self._get('search', params=params)

    def get_dashboard_by_uid(self, uid: str) -> Dict[str, Any]:
        """
        Get dashboard by UID.

        Args:
            uid: Dashboard UID

        Returns:
            Dashboard object with metadata and JSON model

        Raises:
            ResourceNotFoundError: If dashboard not found

        Example:
            dashboard = driver.get_dashboard_by_uid('abc123')
            print(dashboard['dashboard']['title'])
        """
        try:
            return self._get(f'dashboards/uid/{uid}')
        except ResourceNotFoundError:
            raise ResourceNotFoundError(
                f"Dashboard with UID '{uid}' not found"
            )

    def get_dashboard_by_slug(self, slug: str) -> Dict[str, Any]:
        """
        Get dashboard by slug (deprecated in favor of UID, but still supported).

        Args:
            slug: Dashboard slug

        Returns:
            Dashboard object
        """
        return self._get(f'dashboards/db/{slug}')

    def get_home_dashboard(self) -> Dict[str, Any]:
        """
        Get the home dashboard.

        Returns:
            Home dashboard object
        """
        return self._get('dashboards/home')

    def export_dashboard(self, uid: str) -> Dict[str, Any]:
        """
        Export dashboard JSON model.

        Args:
            uid: Dashboard UID

        Returns:
            Complete dashboard JSON model suitable for import

        Example:
            dashboard_json = driver.export_dashboard('abc123')
            # Save to file for backup or migration
            with open('dashboard.json', 'w') as f:
                json.dump(dashboard_json, f)
        """
        result = self.get_dashboard_by_uid(uid)
        return result.get('dashboard', {})

    # ========================================================================
    # Data Source Operations
    # ========================================================================

    def list_datasources(self) -> List[Dict[str, Any]]:
        """
        List all data sources.

        Returns:
            List of data source configurations

        Example:
            datasources = driver.list_datasources()
            for ds in datasources:
                print(f"{ds['name']}: {ds['type']}")
        """
        return self._get('datasources')

    def get_datasource_by_id(self, datasource_id: int) -> Dict[str, Any]:
        """
        Get data source by ID.

        Args:
            datasource_id: Data source ID

        Returns:
            Data source configuration
        """
        return self._get(f'datasources/{datasource_id}')

    def get_datasource_by_name(self, name: str) -> Dict[str, Any]:
        """
        Get data source by name.

        Args:
            name: Data source name

        Returns:
            Data source configuration
        """
        return self._get(f'datasources/name/{name}')

    def get_datasource_by_uid(self, uid: str) -> Dict[str, Any]:
        """
        Get data source by UID.

        Args:
            uid: Data source UID

        Returns:
            Data source configuration
        """
        return self._get(f'datasources/uid/{uid}')

    # ========================================================================
    # Annotation Operations
    # ========================================================================

    def get_annotations(
        self,
        from_time: Optional[datetime] = None,
        to_time: Optional[datetime] = None,
        dashboard_id: Optional[int] = None,
        panel_id: Optional[int] = None,
        tags: Optional[List[str]] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Query annotations.

        Args:
            from_time: Start time for annotation query
            to_time: End time for annotation query
            dashboard_id: Filter by dashboard ID
            panel_id: Filter by panel ID
            tags: Filter by tags
            limit: Maximum number of results

        Returns:
            List of annotations

        Example:
            # Get annotations from last 7 days
            annotations = driver.get_annotations(
                from_time=datetime.now() - timedelta(days=7),
                to_time=datetime.now(),
                tags=['deployment', 'incident']
            )
        """
        params = {'limit': limit}

        if from_time:
            params['from'] = int(from_time.timestamp() * 1000)  # milliseconds
        if to_time:
            params['to'] = int(to_time.timestamp() * 1000)
        if dashboard_id:
            params['dashboardId'] = dashboard_id
        if panel_id:
            params['panelId'] = panel_id
        if tags:
            params['tags'] = tags

        return self._get('annotations', params=params)

    def create_annotation(
        self,
        text: str,
        tags: Optional[List[str]] = None,
        time: Optional[datetime] = None,
        dashboard_id: Optional[int] = None,
        panel_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create an annotation.

        Args:
            text: Annotation text
            tags: List of tags
            time: Annotation time (default: now)
            dashboard_id: Associated dashboard ID
            panel_id: Associated panel ID

        Returns:
            Created annotation object
        """
        data = {'text': text}

        if tags:
            data['tags'] = tags
        if time:
            data['time'] = int(time.timestamp() * 1000)
        if dashboard_id:
            data['dashboardId'] = dashboard_id
        if panel_id:
            data['panelId'] = panel_id

        return self._post('annotations', json=data)

    # ========================================================================
    # Organization and User Operations
    # ========================================================================

    def get_current_org(self) -> Dict[str, Any]:
        """
        Get current organization.

        Returns:
            Organization details
        """
        return self._get('org')

    def list_orgs(self) -> List[Dict[str, Any]]:
        """
        List all organizations (admin only).

        Returns:
            List of organizations
        """
        return self._get('orgs')

    def get_current_user(self) -> Dict[str, Any]:
        """
        Get current user details.

        Returns:
            User profile
        """
        return self._get('user')

    # ========================================================================
    # Folder Operations
    # ========================================================================

    def list_folders(self) -> List[Dict[str, Any]]:
        """
        List all folders.

        Returns:
            List of folders
        """
        return self._get('folders')

    def get_folder_by_uid(self, uid: str) -> Dict[str, Any]:
        """
        Get folder by UID.

        Args:
            uid: Folder UID

        Returns:
            Folder object
        """
        return self._get(f'folders/{uid}')

    def search_folders(self, query: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for folders.

        Args:
            query: Search query

        Returns:
            List of folders matching query
        """
        params = {'type': 'dash-folder'}
        if query:
            params['query'] = query

        return self._get('search', params=params)

    # ========================================================================
    # Alert Operations
    # ========================================================================

    def list_alerts(self) -> List[Dict[str, Any]]:
        """
        List all alerts.

        Returns:
            List of alert definitions
        """
        return self._get('alerts')

    def get_alert_by_id(self, alert_id: int) -> Dict[str, Any]:
        """
        Get alert by ID.

        Args:
            alert_id: Alert ID

        Returns:
            Alert definition
        """
        return self._get(f'alerts/{alert_id}')

    # ========================================================================
    # Utility Methods
    # ========================================================================

    def get_dashboard_permissions(self, dashboard_id: int) -> List[Dict[str, Any]]:
        """
        Get dashboard permissions.

        Args:
            dashboard_id: Dashboard ID

        Returns:
            List of permissions
        """
        return self._get(f'dashboards/id/{dashboard_id}/permissions')

    def get_api_keys(self) -> List[Dict[str, Any]]:
        """
        List API keys (admin only).

        Returns:
            List of API keys
        """
        return self._get('auth/keys')

    def get_health(self) -> Dict[str, Any]:
        """
        Get health status.

        Returns:
            Health status information
        """
        return self._get('health')

    # ========================================================================
    # Advanced Query Methods
    # ========================================================================

    def query_datasource(
        self,
        datasource_uid: str,
        query: Dict[str, Any],
        from_time: datetime,
        to_time: datetime
    ) -> Dict[str, Any]:
        """
        Query a data source directly.

        Args:
            datasource_uid: Data source UID
            query: Query object (format depends on data source type)
            from_time: Query start time
            to_time: Query end time

        Returns:
            Query results

        Example:
            # Query Prometheus data source
            results = driver.query_datasource(
                datasource_uid='prometheus-uid',
                query={'expr': 'up{job="api"}'},
                from_time=datetime.now() - timedelta(hours=1),
                to_time=datetime.now()
            )
        """
        data = {
            'queries': [query],
            'from': str(int(from_time.timestamp() * 1000)),
            'to': str(int(to_time.timestamp() * 1000))
        }

        return self._post(f'datasources/proxy/uid/{datasource_uid}/query', json=data)

    def export_all_dashboards(self) -> Iterator[Dict[str, Any]]:
        """
        Export all dashboards.

        Yields:
            Dashboard JSON models

        Example:
            for dashboard in driver.export_all_dashboards():
                filename = f"{dashboard['uid']}.json"
                with open(filename, 'w') as f:
                    json.dump(dashboard, f)
        """
        dashboards = self.search_dashboards()

        for dash_meta in dashboards:
            try:
                dashboard = self.export_dashboard(dash_meta['uid'])
                yield dashboard
            except ResourceNotFoundError:
                # Skip dashboards that can't be accessed
                continue
