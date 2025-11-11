"""
Agent Executor for Grafana and PostHog Drivers in E2B Sandboxes.

This module orchestrates the execution of driver operations inside E2B sandboxes:
1. Creates/manages E2B sandbox
2. Uploads drivers and mock APIs
3. Starts mock API services
4. Generates execution scripts from templates
5. Executes scripts in sandbox
6. Parses and returns results

Usage:
    executor = AgentExecutor(mode='mock')  # or 'production'
    result = executor.execute_grafana('list_dashboards', query='sales')
"""

import json
import time
from typing import Optional, Dict, Any, Literal
from datetime import datetime, timedelta
import os

from script_templates import format_template, get_template


class AgentExecutor:
    """
    Executor for running driver operations in E2B sandboxes.

    Handles:
    - Sandbox lifecycle management
    - File uploads (drivers, mock APIs)
    - Service orchestration (mock APIs)
    - Script generation and execution
    - Result parsing
    """

    def __init__(
        self,
        mode: Literal['mock', 'production'] = 'mock',
        e2b_api_key: Optional[str] = None,
        grafana_token: Optional[str] = None,
        grafana_url: Optional[str] = None,
        posthog_token: Optional[str] = None,
        posthog_url: Optional[str] = None,
        posthog_project_id: Optional[int] = None
    ):
        """
        Initialize agent executor.

        Args:
            mode: 'mock' to use mock APIs, 'production' for real APIs
            e2b_api_key: E2B API key for sandbox creation
            grafana_token: Grafana API token (production mode)
            grafana_url: Grafana instance URL (production mode)
            posthog_token: PostHog API token (production mode)
            posthog_url: PostHog instance URL (production mode)
            posthog_project_id: PostHog project ID (production mode)
        """
        self.mode = mode
        self.e2b_api_key = e2b_api_key or os.getenv('E2B_API_KEY')
        self.sandbox = None
        self.mock_api_processes = {}

        # Production mode configuration
        self.grafana_token = grafana_token or os.getenv('GRAFANA_TOKEN')
        self.grafana_url = grafana_url or os.getenv('GRAFANA_URL', 'https://grafana.com')
        self.posthog_token = posthog_token or os.getenv('POSTHOG_API_KEY')
        self.posthog_url = posthog_url or os.getenv('POSTHOG_URL', 'https://app.posthog.com')
        self.posthog_project_id = posthog_project_id or os.getenv('POSTHOG_PROJECT_ID')

        if mode == 'production':
            if not self.grafana_token or not self.posthog_token:
                raise ValueError("Production mode requires API tokens")

    def start_sandbox(self):
        """
        Create and configure E2B sandbox.

        Steps:
        1. Create sandbox instance
        2. Install dependencies
        3. Upload driver files
        4. Upload mock API files (if mock mode)
        5. Start mock APIs (if mock mode)
        """
        if self.sandbox:
            print("Sandbox already running")
            return

        # NOTE: This is a conceptual implementation
        # In real usage, import e2b and use their SDK
        """
        from e2b import Sandbox

        self.sandbox = Sandbox(api_key=self.e2b_api_key)

        # Install dependencies
        self.sandbox.process.start_and_wait(
            "pip install requests fastapi uvicorn duckdb"
        )

        # Upload driver files
        self._upload_drivers()

        if self.mode == 'mock':
            # Upload and start mock APIs
            self._upload_mock_apis()
            self._start_mock_apis()
        """

        print(f"✓ Sandbox started in {self.mode} mode")

    def _upload_drivers(self):
        """Upload driver files to sandbox."""
        files_to_upload = [
            'base_driver.py',
            'grafana_driver.py',
            'posthog_driver.py'
        ]

        for filename in files_to_upload:
            """
            self.sandbox.upload_file(
                filename,
                f'/home/user/{filename}'
            )
            """
            pass

        print("✓ Drivers uploaded to sandbox")

    def _upload_mock_apis(self):
        """Upload mock API files to sandbox."""
        mock_files = {
            'grafana': ['main.py', 'db.py', 'fixtures.py'],
            'posthog': ['main.py', 'db.py', 'fixtures.py']
        }

        for service, files in mock_files.items():
            for filename in files:
                """
                self.sandbox.upload_file(
                    f'mock_{service}_api/{filename}',
                    f'/home/user/mock_{service}_api/{filename}'
                )
                """
                pass

        print("✓ Mock APIs uploaded to sandbox")

    def _start_mock_apis(self):
        """Start mock API services in sandbox background."""
        # Start Grafana mock on port 8000
        """
        grafana_process = self.sandbox.process.start(
            "cd /home/user/mock_grafana_api && uvicorn main:app --host 0.0.0.0 --port 8000",
            background=True
        )
        self.mock_api_processes['grafana'] = grafana_process

        # Start PostHog mock on port 8001
        posthog_process = self.sandbox.process.start(
            "cd /home/user/mock_posthog_api && uvicorn main:app --host 0.0.0.0 --port 8001",
            background=True
        )
        self.mock_api_processes['posthog'] = posthog_process
        """

        # Wait for APIs to start
        time.sleep(2)

        print("✓ Mock APIs started (Grafana:8000, PostHog:8001)")

    def execute_grafana(
        self,
        operation: str,
        **params
    ) -> Dict[str, Any]:
        """
        Execute a Grafana driver operation.

        Args:
            operation: Operation name (e.g., 'list_dashboards')
            **params: Operation-specific parameters

        Returns:
            Result dictionary with 'success', 'data', 'error' keys

        Example:
            result = executor.execute_grafana(
                'list_dashboards',
                query='sales',
                tag='production'
            )
        """
        # Get template
        template = get_template('grafana', operation)

        # Determine API endpoint
        if self.mode == 'mock':
            base_url = 'http://localhost:8000'
            api_token = 'mock-token'
        else:
            base_url = self.grafana_url
            api_token = self.grafana_token

        # Format template with parameters
        template_params = {
            'base_url': base_url,
            'api_token': api_token,
            **self._format_params(params)
        }

        script = format_template(template, **template_params)

        # Execute in sandbox
        return self._execute_script(script)

    def execute_posthog(
        self,
        operation: str,
        **params
    ) -> Dict[str, Any]:
        """
        Execute a PostHog driver operation.

        Args:
            operation: Operation name (e.g., 'query_events')
            **params: Operation-specific parameters

        Returns:
            Result dictionary

        Example:
            result = executor.execute_posthog(
                'query_events',
                event='$pageview',
                limit=100
            )
        """
        # Get template
        template = get_template('posthog', operation)

        # Determine API endpoint
        if self.mode == 'mock':
            base_url = 'http://localhost:8001'
            api_token = 'mock-token'
            project_id = 12345
        else:
            base_url = self.posthog_url
            api_token = self.posthog_token
            project_id = self.posthog_project_id

        # Format template with parameters
        template_params = {
            'base_url': base_url,
            'api_token': api_token,
            'project_id': project_id,
            **self._format_params(params)
        }

        script = format_template(template, **template_params)

        # Execute in sandbox
        return self._execute_script(script)

    def _format_params(self, params: Dict[str, Any]) -> Dict[str, str]:
        """
        Format parameters for template substitution.

        Converts Python objects to their repr() for safe insertion into scripts.
        """
        formatted = {}

        for key, value in params.items():
            if value is None:
                formatted[f'{key}_repr'] = 'None'
            elif isinstance(value, str):
                formatted[f'{key}_repr'] = repr(value)
            elif isinstance(value, (list, tuple)):
                formatted[f'{key}_repr'] = repr(value)
            elif isinstance(value, datetime):
                # Convert datetime to constructor call
                formatted[f'{key}_repr'] = (
                    f'datetime({value.year}, {value.month}, {value.day}, '
                    f'{value.hour}, {value.minute}, {value.second})'
                )
            else:
                formatted[key] = value

        # Add default values for common parameters
        formatted.setdefault('limit', 100)
        formatted.setdefault('query_repr', 'None')
        formatted.setdefault('tag_repr', 'None')
        formatted.setdefault('event_repr', 'None')
        formatted.setdefault('tags_repr', 'None')
        formatted.setdefault('date_from_repr', 'None')
        formatted.setdefault('date_to_repr', 'None')
        formatted.setdefault('from_time_repr', 'None')
        formatted.setdefault('to_time_repr', 'None')

        return formatted

    def _execute_script(self, script: str) -> Dict[str, Any]:
        """
        Execute Python script in sandbox and parse results.

        Args:
            script: Python script to execute

        Returns:
            Parsed JSON result from script output
        """
        if not self.sandbox:
            # For testing without actual sandbox
            print("⚠ No sandbox - returning mock result")
            return {
                'success': True,
                'data': [],
                'note': 'Mock result - no sandbox available'
            }

        """
        # Execute script
        result = self.sandbox.process.start_and_wait(
            f"python3 -c {repr(script)}"
        )

        # Parse output
        try:
            # Try to parse entire output as JSON
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            # Try to extract JSON from end of output
            lines = result.stdout.strip().split('\n')
            for i in range(len(lines) - 1, -1, -1):
                try:
                    return json.loads('\n'.join(lines[i:]))
                except json.JSONDecodeError:
                    continue

            # Failed to parse
            return {
                'success': False,
                'error': 'Failed to parse script output',
                'raw_output': result.stdout,
                'stderr': result.stderr
            }
        """

    def stop_sandbox(self):
        """Stop sandbox and cleanup resources."""
        if self.sandbox:
            """
            # Stop mock APIs
            for name, process in self.mock_api_processes.items():
                process.kill()

            # Close sandbox
            self.sandbox.close()
            """
            self.sandbox = None
            self.mock_api_processes = {}

        print("✓ Sandbox stopped")

    def __enter__(self):
        """Context manager entry."""
        self.start_sandbox()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_sandbox()


# =============================================================================
# Convenience Functions
# =============================================================================

def create_executor(mode: Literal['mock', 'production'] = 'mock') -> AgentExecutor:
    """
    Create agent executor with environment variable configuration.

    Args:
        mode: 'mock' or 'production'

    Returns:
        Configured AgentExecutor

    Example:
        with create_executor('mock') as executor:
            result = executor.execute_grafana('list_dashboards')
    """
    return AgentExecutor(mode=mode)


# =============================================================================
# Usage Examples
# =============================================================================

if __name__ == '__main__':
    print("Agent Executor Examples\n" + "=" * 60 + "\n")

    # Example 1: Mock mode (no real APIs)
    print("Example 1: Mock Mode\n")

    executor = create_executor('mock')
    # In real usage, this would work:
    # executor.start_sandbox()
    # result = executor.execute_grafana('list_dashboards', query='sales')
    # print(json.dumps(result, indent=2))
    # executor.stop_sandbox()

    print("✓ Executor created in mock mode")
    print("  - Would use http://localhost:8000 for Grafana")
    print("  - Would use http://localhost:8001 for PostHog")
    print("  - No real API calls made\n")

    # Example 2: Production mode
    print("Example 2: Production Mode\n")

    # executor = create_executor('production')
    # executor.start_sandbox()
    # result = executor.execute_grafana('list_dashboards')
    # print(json.dumps(result, indent=2))
    # executor.stop_sandbox()

    print("✓ Production mode would:")
    print("  - Use real Grafana/PostHog URLs from env")
    print("  - Use real API tokens")
    print("  - Make actual API calls\n")

    # Example 3: Context manager
    print("Example 3: Context Manager\n")

    # with create_executor('mock') as executor:
    #     grafana_result = executor.execute_grafana('list_dashboards')
    #     posthog_result = executor.execute_posthog('query_events')
    # # Sandbox automatically cleaned up

    print("✓ Context manager handles:")
    print("  - Automatic sandbox startup")
    print("  - Automatic cleanup on exit")
    print("  - Exception handling\n")

    print("=" * 60)
    print("\nTo use in production:")
    print("1. Install e2b: pip install e2b")
    print("2. Set E2B_API_KEY environment variable")
    print("3. Uncomment sandbox creation code")
    print("4. Run executor.start_sandbox()")
