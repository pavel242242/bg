"""
Claude Agent SDK Tool Integration for Grafana & PostHog Drivers

This module provides tools that Claude Agent SDK can use to query Grafana
and PostHog APIs. Tools execute inside E2B sandboxes for safety and isolation.

Usage:
    from claude_agent_sdk import Agent
    from claude_agent_tools import get_tools, handle_tool_call

    agent = Agent(
        tools=get_tools(),
        tool_handler=handle_tool_call
    )

    response = agent.chat("Show me my Grafana dashboards")
"""

import json
import os
from typing import Any, Dict, List
from datetime import datetime, timedelta

from agent_executor_simplified import SimplifiedAgentExecutor


# =============================================================================
# Configuration
# =============================================================================

# E2B template ID (set via environment or use default)
E2B_TEMPLATE_ID = os.getenv("DRIVER_E2B_TEMPLATE_ID", "base")

# Mode: 'mock' for testing, 'production' for real APIs
DRIVER_MODE = os.getenv("DRIVER_MODE", "mock")

# Create shared executor instance
# This will be reused across tool calls for efficiency
_executor = None


def get_executor() -> SimplifiedAgentExecutor:
    """Get or create the executor instance."""
    global _executor
    if _executor is None:
        _executor = SimplifiedAgentExecutor(
            template_id=E2B_TEMPLATE_ID,
            mode=DRIVER_MODE
        )
    return _executor


# =============================================================================
# Tool Definitions
# =============================================================================

GRAFANA_TOOLS = [
    {
        "name": "query_grafana_dashboards",
        "description": (
            "Search and list Grafana dashboards. Use this when the user asks "
            "about Grafana dashboards, monitoring dashboards, or visualizations. "
            "Can filter by search query and/or tags. Returns dashboard metadata "
            "including titles, UIDs, tags, and folder information."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query to filter dashboards (e.g., 'sales', 'api', 'database')"
                },
                "tag": {
                    "type": "string",
                    "description": "Filter by tag (e.g., 'production', 'staging', 'business')"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of dashboards to return",
                    "default": 100
                }
            }
        }
    },
    {
        "name": "get_grafana_dashboard",
        "description": (
            "Get detailed information about a specific Grafana dashboard by UID. "
            "Returns the complete dashboard configuration including all panels, "
            "queries, and settings. Use this when the user wants details about "
            "a specific dashboard."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "uid": {
                    "type": "string",
                    "description": "Dashboard UID (unique identifier)"
                }
            },
            "required": ["uid"]
        }
    },
    {
        "name": "export_grafana_dashboard",
        "description": (
            "Export a Grafana dashboard's JSON configuration. Use this when the "
            "user wants to backup, migrate, or view the raw configuration of a "
            "dashboard. Returns the dashboard JSON model."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "uid": {
                    "type": "string",
                    "description": "Dashboard UID to export"
                }
            },
            "required": ["uid"]
        }
    },
    {
        "name": "list_grafana_datasources",
        "description": (
            "List all Grafana data sources. Returns information about configured "
            "data sources including Prometheus, PostgreSQL, Loki, etc. Use when "
            "the user asks about data sources or monitoring backends."
        ),
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "get_grafana_annotations",
        "description": (
            "Query Grafana annotations. Annotations mark important events like "
            "deployments, incidents, or maintenance windows on dashboards. "
            "Can filter by time range and tags."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "days_back": {
                    "type": "integer",
                    "description": "Number of days to look back (e.g., 7 for last week)",
                    "default": 7
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Filter by tags (e.g., ['deployment', 'incident'])"
                },
                "limit": {
                    "type": "integer",
                    "default": 100
                }
            }
        }
    }
]

POSTHOG_TOOLS = [
    {
        "name": "query_posthog_events",
        "description": (
            "Query PostHog events for user analytics. Use when the user asks "
            "about user behavior, page views, clicks, custom events, or any "
            "analytics data. Can filter by event name and date range. "
            "Returns event data with properties and timestamps."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "event": {
                    "type": "string",
                    "description": "Event name to filter (e.g., '$pageview', '$click', 'signup_completed')"
                },
                "days_back": {
                    "type": "integer",
                    "description": "Number of days to look back (e.g., 7 for last week)",
                    "default": 7
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum events to return",
                    "default": 100
                }
            }
        }
    },
    {
        "name": "list_posthog_feature_flags",
        "description": (
            "List all PostHog feature flags and their status. Use when the user "
            "asks about features, feature flags, experiments, A/B tests, or "
            "gradual rollouts. Returns flag names, status (active/inactive), "
            "and configurations."
        ),
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "get_posthog_event_definitions",
        "description": (
            "Get all PostHog event definitions with volume statistics. Shows "
            "what events are being tracked, how often they occur, and usage "
            "patterns. Use when the user wants to understand what events are "
            "available or analyze event volumes."
        ),
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "list_posthog_insights",
        "description": (
            "List saved PostHog insights (analytics queries/charts). Insights "
            "are saved analytics views like trends, funnels, retention, etc. "
            "Use when the user asks about saved analytics, reports, or insights."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "default": 100
                }
            }
        }
    },
    {
        "name": "list_posthog_projects",
        "description": (
            "List all accessible PostHog projects. Use when the user wants to "
            "know what projects are available or switch between projects."
        ),
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    }
]


def get_tools() -> List[Dict[str, Any]]:
    """
    Get all available tools for Claude Agent SDK.

    Returns:
        List of tool definitions
    """
    return GRAFANA_TOOLS + POSTHOG_TOOLS


# =============================================================================
# Tool Handler
# =============================================================================

def handle_tool_call(tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle tool calls from Claude Agent SDK.

    This function is called when Claude decides to use one of the tools.
    It maps the tool name to the appropriate driver operation, executes it
    in an E2B sandbox, and returns formatted results.

    Args:
        tool_name: Name of the tool being called
        tool_input: Dictionary of input parameters

    Returns:
        Tool result in Claude Agent SDK format
    """
    executor = get_executor()

    try:
        # Determine service and operation
        if "grafana" in tool_name:
            result = _handle_grafana_tool(executor, tool_name, tool_input)
        elif "posthog" in tool_name:
            result = _handle_posthog_tool(executor, tool_name, tool_input)
        else:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Unknown tool: {tool_name}"
                    }
                ],
                "is_error": True
            }

        # Format successful result
        if result['success']:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": _format_result(tool_name, result['data'], result.get('count'))
                    }
                ]
            }
        else:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error: {result['error']}\nType: {result.get('error_type', 'Unknown')}"
                    }
                ],
                "is_error": True
            }

    except Exception as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Tool execution failed: {str(e)}"
                }
            ],
            "is_error": True
        }


def _handle_grafana_tool(
    executor: SimplifiedAgentExecutor,
    tool_name: str,
    tool_input: Dict[str, Any]
) -> Dict[str, Any]:
    """Handle Grafana tool calls."""
    # Map tool names to operations
    operation_map = {
        "query_grafana_dashboards": "list_dashboards",
        "get_grafana_dashboard": "get_dashboard",
        "export_grafana_dashboard": "export_dashboard",
        "list_grafana_datasources": "list_datasources",
        "get_grafana_annotations": "get_annotations"
    }

    operation = operation_map.get(tool_name)
    if not operation:
        return {
            "success": False,
            "error": f"Unknown Grafana tool: {tool_name}"
        }

    # Handle special parameters
    if operation == "get_annotations" and "days_back" in tool_input:
        days = tool_input.pop("days_back")
        tool_input["from_time"] = datetime.now() - timedelta(days=days)
        tool_input["to_time"] = datetime.now()

    return executor.execute_grafana(operation, **tool_input)


def _handle_posthog_tool(
    executor: SimplifiedAgentExecutor,
    tool_name: str,
    tool_input: Dict[str, Any]
) -> Dict[str, Any]:
    """Handle PostHog tool calls."""
    # Map tool names to operations
    operation_map = {
        "query_posthog_events": "query_events",
        "list_posthog_feature_flags": "list_feature_flags",
        "get_posthog_event_definitions": "get_event_definitions",
        "list_posthog_insights": "list_insights",
        "list_posthog_projects": "list_projects"
    }

    operation = operation_map.get(tool_name)
    if not operation:
        return {
            "success": False,
            "error": f"Unknown PostHog tool: {tool_name}"
        }

    # Handle special parameters
    if operation == "query_events" and "days_back" in tool_input:
        days = tool_input.pop("days_back")
        tool_input["date_from"] = datetime.now() - timedelta(days=days)
        tool_input["date_to"] = datetime.now()

    return executor.execute_posthog(operation, **tool_input)


def _format_result(tool_name: str, data: Any, count: int = None) -> str:
    """
    Format tool results for Claude in a human-readable way.

    Args:
        tool_name: Name of the tool
        data: Raw data from driver
        count: Optional count of items

    Returns:
        Formatted string
    """
    # For list operations, format as summary + JSON
    if "query" in tool_name or "list" in tool_name:
        summary = f"Found {count or len(data)} items.\n\n"

        # Show preview of first few items
        if isinstance(data, list) and len(data) > 0:
            preview = data[:5]  # First 5 items
            summary += "Preview:\n"
            for i, item in enumerate(preview, 1):
                if "title" in item:
                    summary += f"{i}. {item['title']} (UID: {item.get('uid', 'N/A')})\n"
                elif "name" in item:
                    summary += f"{i}. {item['name']}\n"
                elif "key" in item:
                    summary += f"{i}. {item['key']}: {item.get('name', 'N/A')}\n"
                elif "event" in item:
                    summary += f"{i}. {item['event']} at {item.get('timestamp', 'N/A')}\n"

            if len(data) > 5:
                summary += f"\n... and {len(data) - 5} more items.\n"

        summary += f"\n\nFull data (JSON):\n{json.dumps(data, indent=2)}"
        return summary

    # For single item operations, just return JSON
    return json.dumps(data, indent=2)


# =============================================================================
# Convenience Functions
# =============================================================================

def configure(template_id: str = None, mode: str = None):
    """
    Configure the driver integration.

    Args:
        template_id: E2B template ID
        mode: 'mock' or 'production'

    Example:
        configure(template_id='my-template-id', mode='production')
    """
    global E2B_TEMPLATE_ID, DRIVER_MODE, _executor

    if template_id:
        E2B_TEMPLATE_ID = template_id

    if mode:
        DRIVER_MODE = mode

    # Reset executor to pick up new config
    _executor = None


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == '__main__':
    print("Claude Agent SDK Tool Integration\n" + "=" * 60 + "\n")

    print("Available Tools:")
    for i, tool in enumerate(get_tools(), 1):
        print(f"{i}. {tool['name']}")
        print(f"   {tool['description'][:80]}...")
        print()

    print("=" * 60)
    print("\nTo use with Claude Agent SDK:")
    print()
    print("from claude_agent_sdk import Agent")
    print("from claude_agent_tools import get_tools, handle_tool_call")
    print()
    print("agent = Agent(")
    print("    tools=get_tools(),")
    print("    tool_handler=handle_tool_call")
    print(")")
    print()
    print('response = agent.chat("Show me my Grafana dashboards")')
    print()
    print("Claude will automatically use the appropriate tools!")
