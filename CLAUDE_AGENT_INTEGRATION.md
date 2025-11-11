# Claude Agent SDK + Driver Integration Architecture

## The Real Question: What Does Claude Agent SDK See?

When a Claude Agent SDK instance runs (in E2B or locally), it needs **tools** - functions it can call. Our drivers need to be exposed as tools to the agent.

---

## Architecture: Where Everything Runs

```
┌─────────────────────────────────────────────────────────────┐
│ HOST MACHINE (Developer's Computer / Server)               │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐│
│  │ Claude Agent SDK Instance                              ││
│  │                                                         ││
│  │  Available Tools:                                      ││
│  │    - query_grafana_dashboards()                        ││
│  │    - get_grafana_dashboard()                           ││
│  │    - query_posthog_events()                            ││
│  │    - list_posthog_feature_flags()                      ││
│  │    - ... (all driver operations as tools)              ││
│  │                                                         ││
│  │  When tool called:                                     ││
│  │    1. Creates E2B sandbox (with our template)          ││
│  │    2. Executes driver operation inside sandbox         ││
│  │    3. Returns results to agent                         ││
│  └────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Creates sandbox when needed
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ E2B SANDBOX (Ephemeral, Isolated VM)                       │
│                                                              │
│  /home/user/                                                │
│    ├── base_driver.py          (pre-installed)             │
│    ├── grafana_driver.py       (pre-installed)             │
│    ├── posthog_driver.py       (pre-installed)             │
│    ├── mock_grafana_api/       (pre-installed)             │
│    └── mock_posthog_api/       (pre-installed)             │
│                                                              │
│  [Mock API running on localhost:8000]                      │
│  [Driver code executes here]                                │
└─────────────────────────────────────────────────────────────┘
```

---

## What Claude Agent SDK Sees: Tool Definitions

The Claude Agent SDK will see tools like this:

```python
tools = [
    {
        "name": "query_grafana_dashboards",
        "description": "Search and list Grafana dashboards. Use this when the user asks about Grafana dashboards, monitoring, or visualization.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query to filter dashboards (e.g., 'sales', 'api')"
                },
                "tag": {
                    "type": "string",
                    "description": "Tag to filter by (e.g., 'production', 'staging')"
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
        "description": "Get details of a specific Grafana dashboard by UID. Returns full dashboard configuration including panels.",
        "input_schema": {
            "type": "object",
            "properties": {
                "uid": {
                    "type": "string",
                    "description": "Dashboard UID"
                }
            },
            "required": ["uid"]
        }
    },
    {
        "name": "query_posthog_events",
        "description": "Query PostHog events for analytics. Use when user asks about user behavior, page views, clicks, or custom events.",
        "input_schema": {
            "type": "object",
            "properties": {
                "event": {
                    "type": "string",
                    "description": "Event name to filter (e.g., '$pageview', '$click', 'signup_completed')"
                },
                "date_from": {
                    "type": "string",
                    "description": "Start date (ISO format or relative like '-7d')"
                },
                "date_to": {
                    "type": "string",
                    "description": "End date (ISO format or 'now')"
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
        "description": "List all PostHog feature flags and their status. Use when user asks about features, experiments, or A/B tests.",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    }
    # ... more tools for other operations
]
```

---

## Implementation: Tool Handler Functions

Each tool has a handler that uses E2B to execute the driver:

```python
from e2b import Sandbox
from agent_executor_simplified import SimplifiedAgentExecutor
import os

# Configuration
E2B_TEMPLATE_ID = "driver-template-abc123"  # Your custom template
MODE = "mock"  # or "production"

# Create executor (shared across tool calls)
executor = SimplifiedAgentExecutor(
    template_id=E2B_TEMPLATE_ID,
    mode=MODE
)

# Tool handler functions
def query_grafana_dashboards(query=None, tag=None, limit=100):
    """
    Tool handler for querying Grafana dashboards.

    This is what Claude Agent SDK calls when it uses the tool.
    """
    result = executor.execute_grafana(
        'list_dashboards',
        query=query,
        tag=tag,
        limit=limit
    )

    if result['success']:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Found {result['count']} dashboards:\n\n" +
                           "\n".join([
                               f"- {d['title']} (UID: {d['uid']}, Tags: {d.get('tags', [])})"
                               for d in result['data']
                           ])
                }
            ]
        }
    else:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Error: {result['error']}"
                }
            ],
            "is_error": True
        }

def get_grafana_dashboard(uid):
    """Tool handler for getting specific dashboard."""
    result = executor.execute_grafana('get_dashboard', uid=uid)

    if result['success']:
        dashboard = result['data']['dashboard']
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Dashboard: {dashboard['title']}\n" +
                           f"UID: {dashboard['uid']}\n" +
                           f"Panels: {len(dashboard.get('panels', []))}\n" +
                           f"Tags: {dashboard.get('tags', [])}\n\n" +
                           f"Full configuration:\n{json.dumps(dashboard, indent=2)}"
                }
            ]
        }
    else:
        return {
            "content": [{"type": "text", "text": f"Error: {result['error']}"}],
            "is_error": True
        }

def query_posthog_events(event=None, date_from=None, date_to=None, limit=100):
    """Tool handler for querying PostHog events."""
    from datetime import datetime, timedelta

    # Parse relative dates
    if date_from and date_from.startswith('-'):
        days = int(date_from[1:-1])  # -7d -> 7
        date_from = datetime.now() - timedelta(days=days)

    if date_to == 'now':
        date_to = datetime.now()

    result = executor.execute_posthog(
        'query_events',
        event=event,
        date_from=date_from,
        date_to=date_to,
        limit=limit
    )

    if result['success']:
        events = result['data']
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Found {result['count']} events:\n\n" +
                           "\n".join([
                               f"- {e['event']} at {e['timestamp']} (user: {e['distinct_id']})"
                               for e in events[:10]  # Show first 10
                           ]) +
                           (f"\n\n... and {len(events) - 10} more" if len(events) > 10 else "")
                }
            ]
        }
    else:
        return {
            "content": [{"type": "text", "text": f"Error: {result['error']}"}],
            "is_error": True
        }

def list_posthog_feature_flags():
    """Tool handler for listing feature flags."""
    result = executor.execute_posthog('list_feature_flags')

    if result['success']:
        flags = result['data']
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Feature Flags ({len(flags)}):\n\n" +
                           "\n".join([
                               f"- {f['key']}: {'✓ Active' if f['active'] else '✗ Inactive'} - {f['name']}"
                               for f in flags
                           ])
                }
            ]
        }
    else:
        return {
            "content": [{"type": "text", "text": f"Error: {result['error']}"}],
            "is_error": True
        }

# Map tool names to handlers
TOOL_HANDLERS = {
    "query_grafana_dashboards": query_grafana_dashboards,
    "get_grafana_dashboard": get_grafana_dashboard,
    "query_posthog_events": query_posthog_events,
    "list_posthog_feature_flags": list_posthog_feature_flags,
}
```

---

## Conversation Flow Example

```
User: "Show me my Grafana dashboards tagged with 'production'"

Claude Agent SDK:
  1. Sees user request
  2. Decides to use tool: query_grafana_dashboards
  3. Calls tool with parameters: {tag: "production"}

Tool Handler (query_grafana_dashboards):
  1. Creates E2B sandbox (from custom template)
  2. Starts mock Grafana API inside sandbox
  3. Executes driver code: driver.search_dashboards(tag='production')
  4. Returns structured results
  5. Sandbox destroyed

Claude Agent SDK receives:
  "Found 2 dashboards:
   - API Metrics (UID: api-metrics, Tags: ['api', 'production'])
   - Database Monitoring (UID: database-monitoring, Tags: ['database', 'production'])"

Claude Agent SDK responds to user:
  "I found 2 Grafana dashboards tagged with 'production':

   1. API Metrics - Monitors API performance including request rates and errors
   2. Database Monitoring - Tracks database query performance

   Would you like me to get more details about any of these?"
```

---

## Complete Integration File

Here's the actual integration file that registers tools with Claude Agent SDK:

```python
# claude_agent_tools.py
"""
Claude Agent SDK tool integration for Grafana & PostHog drivers.

This file bridges the gap between Claude Agent SDK and our E2B-based drivers.
"""

from typing import Any, Dict, List
import json
import os
from datetime import datetime, timedelta

from agent_executor_simplified import SimplifiedAgentExecutor

# Configuration
E2B_TEMPLATE_ID = os.getenv("DRIVER_E2B_TEMPLATE_ID", "base")
DRIVER_MODE = os.getenv("DRIVER_MODE", "mock")  # mock or production

# Create shared executor
executor = SimplifiedAgentExecutor(
    template_id=E2B_TEMPLATE_ID,
    mode=DRIVER_MODE
)

# Tool Definitions
GRAFANA_TOOLS = [
    {
        "name": "query_grafana_dashboards",
        "description": "Search and list Grafana dashboards by query or tag",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "tag": {"type": "string", "description": "Filter by tag"},
                "limit": {"type": "integer", "default": 100}
            }
        }
    },
    {
        "name": "get_grafana_dashboard",
        "description": "Get details of a specific Grafana dashboard",
        "input_schema": {
            "type": "object",
            "properties": {
                "uid": {"type": "string", "description": "Dashboard UID"}
            },
            "required": ["uid"]
        }
    },
    {
        "name": "export_grafana_dashboard",
        "description": "Export dashboard JSON configuration",
        "input_schema": {
            "type": "object",
            "properties": {
                "uid": {"type": "string", "description": "Dashboard UID"}
            },
            "required": ["uid"]
        }
    },
    {
        "name": "list_grafana_datasources",
        "description": "List all Grafana data sources",
        "input_schema": {"type": "object", "properties": {}}
    }
]

POSTHOG_TOOLS = [
    {
        "name": "query_posthog_events",
        "description": "Query PostHog events for analytics",
        "input_schema": {
            "type": "object",
            "properties": {
                "event": {"type": "string", "description": "Event name"},
                "date_from": {"type": "string", "description": "Start date (ISO or relative like '-7d')"},
                "date_to": {"type": "string", "description": "End date (ISO or 'now')"},
                "limit": {"type": "integer", "default": 100}
            }
        }
    },
    {
        "name": "list_posthog_feature_flags",
        "description": "List all PostHog feature flags",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "get_posthog_event_definitions",
        "description": "Get all event definitions with volume stats",
        "input_schema": {"type": "object", "properties": {}}
    }
]

ALL_TOOLS = GRAFANA_TOOLS + POSTHOG_TOOLS

# Tool Handlers (simplified - map directly to executor)
def handle_tool_call(tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle any tool call by mapping it to the appropriate executor method.

    This is called by Claude Agent SDK when it uses a tool.
    """
    # Map tool name to service and operation
    if tool_name.startswith("query_grafana_") or tool_name.startswith("get_grafana_") or tool_name.startswith("list_grafana_") or tool_name.startswith("export_grafana_"):
        service = "grafana"
        operation = tool_name.replace("query_grafana_", "").replace("get_grafana_", "get_").replace("list_grafana_", "list_").replace("export_grafana_", "export_")
        # Map to actual operation names
        operation_map = {
            "dashboards": "list_dashboards",
            "dashboard": "get_dashboard",
            "export_dashboard": "export_dashboard",
            "datasources": "list_datasources"
        }
        operation = operation_map.get(operation, operation)
        result = executor.execute_grafana(operation, **tool_input)
    else:
        service = "posthog"
        operation = tool_name.replace("query_posthog_", "query_").replace("list_posthog_", "list_").replace("get_posthog_", "get_")
        operation_map = {
            "events": "query_events",
            "feature_flags": "list_feature_flags",
            "event_definitions": "get_event_definitions"
        }
        operation = operation_map.get(operation, operation)

        # Handle relative dates for PostHog
        if 'date_from' in tool_input and tool_input['date_from'] and tool_input['date_from'].startswith('-'):
            days = int(tool_input['date_from'][1:-1])
            tool_input['date_from'] = datetime.now() - timedelta(days=days)
        if 'date_to' in tool_input and tool_input['date_to'] == 'now':
            tool_input['date_to'] = datetime.now()

        result = executor.execute_posthog(operation, **tool_input)

    # Format result for Claude
    if result['success']:
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result['data'], indent=2)
                }
            ]
        }
    else:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Error: {result['error']}"
                }
            ],
            "is_error": True
        }

# Export for Claude Agent SDK
__all__ = ['ALL_TOOLS', 'handle_tool_call', 'executor']
```

---

## Using with Claude Agent SDK

```python
# main.py - Claude Agent SDK integration
from claude_agent_sdk import Agent
from claude_agent_tools import ALL_TOOLS, handle_tool_call

# Create agent with our tools
agent = Agent(
    tools=ALL_TOOLS,
    tool_handler=handle_tool_call
)

# Use the agent
response = agent.chat("Show me my Grafana dashboards tagged with production")
print(response)
```

---

## What the Driver "Offers" to Claude Agent SDK

The driver offers **capabilities as tools**:

1. **Grafana Capabilities:**
   - Search dashboards
   - Get dashboard details
   - Export dashboard configs
   - List data sources
   - Query annotations

2. **PostHog Capabilities:**
   - Query events
   - List feature flags
   - Get event definitions
   - List insights
   - Access experiments

3. **Execution Model:**
   - Tools execute in isolated E2B sandboxes
   - Fast execution (~150ms startup + operation time)
   - Safe (isolated from host)
   - Configurable (mock or production mode)

4. **Developer Experience:**
   - Tools are **declarative** (Claude knows what they do from descriptions)
   - Results are **structured** (JSON)
   - Errors are **handled** (structured error responses)
   - **Stateless** (each call is independent)

---

## Summary

**What Claude Agent SDK sees:**
- A set of tools (functions) it can call
- Clear descriptions of what each tool does
- Input schemas defining parameters

**What happens when Claude uses a tool:**
1. Tool handler called with parameters
2. E2B sandbox created (from custom template with drivers)
3. Driver operation executed inside sandbox
4. Results returned to Claude
5. Claude uses results to respond to user

**What the drivers provide:**
- Abstraction over Grafana/PostHog APIs
- Execution in safe, isolated environment
- Testing capability (mock mode)
- Production capability (real API mode)
- Consistent interface regardless of backend

The drivers are essentially **remote procedure calls** that Claude Agent SDK can make, with E2B providing the secure execution environment!
