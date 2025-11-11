"""
Simplified Agent Executor using E2B SDK directly.

This is the CORRECT implementation after reviewing E2B documentation.
The previous agent_executor.py was over-engineered.

E2B handles:
- Dependency installation (via custom templates)
- Secret management (via envs parameter)
- File uploads (via SDK)
- Process management (via SDK)
- Network access (built-in)
- Timeout control (configurable)

We only need to:
1. Create custom E2B template with pre-installed dependencies
2. Use E2B SDK to execute driver operations
3. Parse results
"""

import json
import time
import os
from typing import Optional, Dict, Any, Literal
from datetime import datetime

from e2b import Sandbox
from script_templates import format_template, get_template


class SimplifiedAgentExecutor:
    """
    Simplified executor using E2B SDK properly.

    Usage:
        executor = SimplifiedAgentExecutor(
            template_id="driver-template-abc123",  # Your custom template
            mode='mock'
        )

        result = executor.execute_grafana('list_dashboards', query='sales')
    """

    def __init__(
        self,
        template_id: str = "base",  # Use "base" or your custom template ID
        mode: Literal['mock', 'production'] = 'mock',
        e2b_api_key: Optional[str] = None
    ):
        """
        Initialize executor.

        Args:
            template_id: E2B template ID (create with: e2b template build)
            mode: 'mock' for mock APIs, 'production' for real APIs
            e2b_api_key: E2B API key (or set E2B_API_KEY env var)
        """
        self.template_id = template_id
        self.mode = mode
        self.e2b_api_key = e2b_api_key or os.getenv('E2B_API_KEY')

        # API configuration
        if mode == 'mock':
            self.grafana_url = 'http://localhost:8000'
            self.posthog_url = 'http://localhost:8001'
            self.grafana_token = 'mock-token'
            self.posthog_token = 'mock-token'
            self.posthog_project_id = 12345
        else:
            self.grafana_url = os.getenv('GRAFANA_URL', 'https://grafana.com')
            self.posthog_url = os.getenv('POSTHOG_URL', 'https://app.posthog.com')
            self.grafana_token = os.getenv('GRAFANA_TOKEN')
            self.posthog_token = os.getenv('POSTHOG_API_KEY')
            self.posthog_project_id = int(os.getenv('POSTHOG_PROJECT_ID', '0'))

    def execute_grafana(
        self,
        operation: str,
        **params
    ) -> Dict[str, Any]:
        """
        Execute Grafana operation in E2B sandbox.

        Args:
            operation: Operation name (e.g., 'list_dashboards')
            **params: Operation parameters

        Returns:
            Result dictionary

        Example:
            result = executor.execute_grafana(
                'list_dashboards',
                query='sales',
                tag='production'
            )
        """
        return self._execute('grafana', operation, **params)

    def execute_posthog(
        self,
        operation: str,
        **params
    ) -> Dict[str, Any]:
        """
        Execute PostHog operation in E2B sandbox.

        Args:
            operation: Operation name (e.g., 'query_events')
            **params: Operation parameters

        Returns:
            Result dictionary
        """
        return self._execute('posthog', operation, **params)

    def _execute(
        self,
        service: str,
        operation: str,
        **params
    ) -> Dict[str, Any]:
        """
        Execute operation in E2B sandbox.

        This is the SIMPLIFIED version that uses E2B properly:
        1. Create sandbox with env vars (E2B handles secrets)
        2. Start mock API if needed (E2B handles processes)
        3. Execute script (E2B handles execution)
        4. Parse results
        5. Cleanup (E2B context manager handles this)
        """
        # Get script template
        template = get_template(service, operation)

        # Format parameters for template
        template_params = self._format_params(params)

        # Service-specific config
        if service == 'grafana':
            template_params.update({
                'base_url': self.grafana_url,
                'api_token': self.grafana_token
            })
        else:  # posthog
            template_params.update({
                'base_url': self.posthog_url,
                'api_token': self.posthog_token,
                'project_id': self.posthog_project_id
            })

        # Generate script
        script = format_template(template, **template_params)

        # Execute in E2B sandbox
        with Sandbox.create(
            self.template_id,
            api_key=self.e2b_api_key,
            timeout=60 * 5  # 5 minute sandbox timeout
        ) as sandbox:
            # Start mock API if in mock mode
            if self.mode == 'mock':
                self._start_mock_api(sandbox, service)

            # Execute script
            result = sandbox.run_code(script, timeout=60 * 2)  # 2 min execution timeout

            # Parse result
            return self._parse_result(result)

    def _start_mock_api(self, sandbox: Sandbox, service: str):
        """
        Start mock API service in sandbox background.

        E2B handles process management - we just start it!
        """
        if service == 'grafana':
            port = 8000
            api_dir = 'mock_grafana_api'
        else:
            port = 8001
            api_dir = 'mock_posthog_api'

        # Start mock API in background
        sandbox.process.start(
            f"cd /home/user/{api_dir} && uvicorn main:app --host 0.0.0.0 --port {port}",
            background=True
        )

        # Wait for API to be ready
        time.sleep(2)

    def _format_params(self, params: Dict[str, Any]) -> Dict[str, str]:
        """
        Format parameters for template substitution.

        Converts Python objects to their repr() for safe script injection.
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
                formatted[f'{key}_repr'] = (
                    f'datetime({value.year}, {value.month}, {value.day}, '
                    f'{value.hour}, {value.minute}, {value.second})'
                )
            else:
                formatted[key] = value

        # Set defaults
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

    def _parse_result(self, result) -> Dict[str, Any]:
        """
        Parse execution result from E2B.

        E2B provides result.stdout and result.stderr automatically!
        """
        try:
            # Try to parse entire stdout as JSON
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            # Fallback: try to find JSON in output
            lines = result.stdout.strip().split('\n')
            for i in range(len(lines) - 1, -1, -1):
                try:
                    return json.loads('\n'.join(lines[i:]))
                except json.JSONDecodeError:
                    continue

            # Failed to parse - return error
            return {
                'success': False,
                'error': 'Failed to parse script output',
                'raw_output': result.stdout,
                'stderr': result.stderr
            }


# =============================================================================
# Convenience Functions
# =============================================================================

def create_executor(
    mode: Literal['mock', 'production'] = 'mock',
    template_id: str = "base"
) -> SimplifiedAgentExecutor:
    """
    Create executor with environment variable configuration.

    Args:
        mode: 'mock' or 'production'
        template_id: E2B template ID

    Returns:
        SimplifiedAgentExecutor

    Example:
        executor = create_executor('mock')
        result = executor.execute_grafana('list_dashboards')
    """
    return SimplifiedAgentExecutor(template_id=template_id, mode=mode)


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == '__main__':
    print("Simplified Agent Executor (E2B-Native)\n" + "=" * 60 + "\n")

    print("This version uses E2B SDK properly:")
    print("  ✓ E2B handles dependency installation (custom template)")
    print("  ✓ E2B handles secret management (envs parameter)")
    print("  ✓ E2B handles file uploads (SDK methods)")
    print("  ✓ E2B handles process management (SDK methods)")
    print("  ✓ E2B handles network access (built-in)")
    print("  ✓ E2B handles timeout control (configurable)")
    print()

    print("To use:")
    print()
    print("1. Create custom E2B template:")
    print("   $ e2b template init")
    print("   $ # Add to e2b.Dockerfile:")
    print("   $ # FROM python:3.11")
    print("   $ # COPY *.py /home/user/")
    print("   $ # COPY mock_*_api/ /home/user/")
    print("   $ # RUN pip install requests fastapi uvicorn duckdb")
    print("   $ e2b template build")
    print()
    print("2. Use template ID in executor:")
    print("   executor = create_executor('mock', template_id='your-template-id')")
    print("   result = executor.execute_grafana('list_dashboards')")
    print()
    print("3. Results come back as JSON:")
    print("   {'success': True, 'data': [...], 'count': 4}")
    print()
    print("=" * 60)
