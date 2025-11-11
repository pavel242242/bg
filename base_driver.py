"""
Base driver component for API-based data extraction.

Provides a generalized framework for building extractor drivers with:
- Session management
- Pluggable authentication strategies
- Request abstraction with error handling
- Context manager support
- Consistent exception hierarchy
"""

import os
from typing import Optional, Dict, Any, Union
from enum import Enum
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError as RequestsConnectionError


# ============================================================================
# Exception Hierarchy
# ============================================================================

class DriverError(Exception):
    """Base exception for all driver errors."""
    pass


class ConnectionError(DriverError):
    """Raised when there are network connectivity issues."""
    pass


class AuthError(DriverError):
    """Raised when authentication fails."""
    pass


class ResourceNotFoundError(DriverError):
    """Raised when a requested resource is not found."""
    pass


class QueryError(DriverError):
    """Raised when a query operation fails."""
    pass


class RateLimitError(DriverError):
    """Raised when API rate limits are exceeded."""
    pass


# ============================================================================
# Authentication Strategies
# ============================================================================

class AuthStrategy(Enum):
    """Supported authentication strategies."""
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    BASIC_AUTH = "basic_auth"
    OAUTH2 = "oauth2"


class AuthConfig:
    """Configuration for authentication."""

    def __init__(
        self,
        strategy: AuthStrategy,
        credentials: Dict[str, str],
        header_name: Optional[str] = None
    ):
        """
        Initialize authentication configuration.

        Args:
            strategy: Authentication strategy to use
            credentials: Dictionary of credentials (key, token, username, password, etc.)
            header_name: Optional custom header name (e.g., 'X-API-Key')
        """
        self.strategy = strategy
        self.credentials = credentials
        self.header_name = header_name

    def apply_to_session(self, session: requests.Session):
        """Apply authentication configuration to a requests session."""
        if self.strategy == AuthStrategy.API_KEY:
            header_name = self.header_name or 'X-API-Key'
            session.headers[header_name] = self.credentials.get('api_key')

        elif self.strategy == AuthStrategy.BEARER_TOKEN:
            token = self.credentials.get('token')
            session.headers['Authorization'] = f'Bearer {token}'

        elif self.strategy == AuthStrategy.BASIC_AUTH:
            username = self.credentials.get('username')
            password = self.credentials.get('password')
            session.auth = (username, password)

        elif self.strategy == AuthStrategy.OAUTH2:
            token = self.credentials.get('access_token')
            session.headers['Authorization'] = f'Bearer {token}'


# ============================================================================
# Base Driver
# ============================================================================

class BaseAPIDriver:
    """
    Base class for API-based data extraction drivers.

    Provides common functionality:
    - HTTP session management with connection pooling
    - Authentication handling
    - Request abstraction with error handling
    - Response parsing
    - Context manager support for resource cleanup

    Subclasses should implement:
    - Resource-specific methods (list, get, query, etc.)
    - Response transformation logic
    - Driver-specific error handling
    """

    def __init__(
        self,
        base_url: str,
        auth_config: AuthConfig,
        timeout: int = 30,
        verify_ssl: bool = True,
        max_retries: int = 3
    ):
        """
        Initialize the base driver.

        Args:
            base_url: Base URL for the API
            auth_config: Authentication configuration
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
            max_retries: Maximum number of retry attempts
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.max_retries = max_retries

        # Initialize session
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

        # Apply authentication
        auth_config.apply_to_session(self.session)

    def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make an HTTP request with error handling.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint (will be appended to base_url)
            **kwargs: Additional arguments passed to requests (params, json, etc.)

        Returns:
            Parsed JSON response as dictionary

        Raises:
            ConnectionError: Network connectivity issues
            AuthError: Authentication failures
            ResourceNotFoundError: Resource not found (404)
            RateLimitError: Rate limit exceeded (429)
            QueryError: Query execution failures
            DriverError: Other API errors
        """
        # Build full URL
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        # Set default timeout if not provided
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout

        # Set SSL verification
        if 'verify' not in kwargs:
            kwargs['verify'] = self.verify_ssl

        try:
            # Make request
            response = self.session.request(method, url, **kwargs)

            # Handle specific status codes
            if response.status_code == 401:
                raise AuthError(
                    f"Authentication failed. Please check your credentials. "
                    f"URL: {url}"
                )

            elif response.status_code == 404:
                raise ResourceNotFoundError(
                    f"Resource not found: {endpoint}"
                )

            elif response.status_code == 429:
                raise RateLimitError(
                    f"Rate limit exceeded. Please try again later."
                )

            elif response.status_code == 400:
                try:
                    error_detail = response.json()
                except ValueError:
                    error_detail = response.text
                raise QueryError(
                    f"Bad request: {error_detail}"
                )

            elif not response.ok:
                raise DriverError(
                    f"Request failed with status {response.status_code}: "
                    f"{response.text}"
                )

            # Parse JSON response
            try:
                return response.json()
            except ValueError as e:
                raise DriverError(
                    f"Failed to parse JSON response: {str(e)}"
                )

        except (RequestsConnectionError, Timeout) as e:
            raise ConnectionError(
                f"Network error: {str(e)}. "
                f"Please check your connection and try again."
            )

        except RequestException as e:
            raise DriverError(
                f"Request failed: {str(e)}"
            )

    def _get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Convenience method for GET requests."""
        return self._make_request('GET', endpoint, **kwargs)

    def _post(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Convenience method for POST requests."""
        return self._make_request('POST', endpoint, **kwargs)

    def _put(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Convenience method for PUT requests."""
        return self._make_request('PUT', endpoint, **kwargs)

    def _delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Convenience method for DELETE requests."""
        return self._make_request('DELETE', endpoint, **kwargs)

    def test_connection(self) -> bool:
        """
        Test the connection to the API.

        Returns:
            True if connection is successful

        Raises:
            ConnectionError: If connection fails
            AuthError: If authentication fails
        """
        # Subclasses should override with a specific endpoint
        raise NotImplementedError(
            "Subclasses must implement test_connection()"
        )

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup session."""
        self.session.close()

    def close(self):
        """Explicitly close the session."""
        self.session.close()


# ============================================================================
# Pagination Support
# ============================================================================

class PaginationStrategy(Enum):
    """Common pagination strategies."""
    OFFSET_LIMIT = "offset_limit"  # ?offset=0&limit=100
    PAGE_SIZE = "page_size"         # ?page=1&size=100
    CURSOR = "cursor"               # ?cursor=abc123
    LINK_HEADER = "link_header"     # Link header with next/prev URLs


class PaginatedDriver(BaseAPIDriver):
    """
    Extended driver with pagination support.

    Provides helpers for iterating through paginated API responses.
    """

    def _paginate(
        self,
        endpoint: str,
        strategy: PaginationStrategy,
        page_size: int = 100,
        max_pages: Optional[int] = None,
        **kwargs
    ):
        """
        Iterate through paginated results.

        Args:
            endpoint: API endpoint to paginate
            strategy: Pagination strategy to use
            page_size: Number of items per page
            max_pages: Maximum number of pages to fetch (None = all)
            **kwargs: Additional request parameters

        Yields:
            Individual items from paginated response
        """
        page = 0
        cursor = None

        while True:
            # Check max pages limit
            if max_pages and page >= max_pages:
                break

            # Build pagination parameters
            params = kwargs.get('params', {}).copy()

            if strategy == PaginationStrategy.OFFSET_LIMIT:
                params['offset'] = page * page_size
                params['limit'] = page_size

            elif strategy == PaginationStrategy.PAGE_SIZE:
                params['page'] = page + 1
                params['size'] = page_size

            elif strategy == PaginationStrategy.CURSOR:
                if cursor:
                    params['cursor'] = cursor
                params['limit'] = page_size

            kwargs['params'] = params

            # Make request
            response = self._get(endpoint, **kwargs)

            # Extract items (subclasses should override _extract_items)
            items = self._extract_items(response)

            if not items:
                break

            for item in items:
                yield item

            # Check for next page
            if strategy == PaginationStrategy.CURSOR:
                cursor = self._extract_next_cursor(response)
                if not cursor:
                    break

            elif len(items) < page_size:
                # Received fewer items than requested = last page
                break

            page += 1

    def _extract_items(self, response: Dict[str, Any]) -> list:
        """
        Extract items from paginated response.

        Subclasses should override this method.
        """
        # Default: assume response is a list
        if isinstance(response, list):
            return response
        # Or response has a 'data' or 'results' key
        return response.get('data', response.get('results', []))

    def _extract_next_cursor(self, response: Dict[str, Any]) -> Optional[str]:
        """
        Extract next cursor from response.

        Subclasses should override for cursor-based pagination.
        """
        return response.get('next_cursor') or response.get('cursor')


# ============================================================================
# Helper Functions
# ============================================================================

def create_auth_config_from_env(
    strategy: AuthStrategy,
    env_var_name: str,
    header_name: Optional[str] = None
) -> AuthConfig:
    """
    Create auth configuration from environment variable.

    Args:
        strategy: Authentication strategy
        env_var_name: Name of environment variable
        header_name: Optional custom header name

    Returns:
        AuthConfig instance

    Raises:
        AuthError: If environment variable is not set
    """
    value = os.getenv(env_var_name)

    if not value:
        raise AuthError(
            f"Authentication required: Environment variable '{env_var_name}' not set"
        )

    if strategy == AuthStrategy.API_KEY:
        credentials = {'api_key': value}
    elif strategy in (AuthStrategy.BEARER_TOKEN, AuthStrategy.OAUTH2):
        credentials = {'token': value}
    else:
        raise ValueError(f"Unsupported strategy for env config: {strategy}")

    return AuthConfig(strategy, credentials, header_name)
