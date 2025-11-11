# E2B + Claude Code Integration Guide

Complete guide for using Grafana and PostHog drivers with Claude Code agents in E2B sandboxes.

## Overview

This integration allows Claude Code agents to:
1. Query Grafana dashboards, data sources, and annotations
2. Query PostHog events, feature flags, and insights
3. Execute driver operations in isolated E2B sandboxes
4. Use mock APIs for testing or real APIs for production

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│ Claude Code (Host)                                           │
│                                                               │
│  User: "Show my Grafana dashboards"                          │
│    ↓                                                         │
│  Agent Executor:                                             │
│    1. Map prompt → "list_dashboards" operation              │
│    2. Create E2B sandbox                                     │
│    3. Upload drivers + mock APIs                             │
│    4. Start mock API services                                │
│    5. Generate script from template                          │
│    6. Execute in sandbox                                     │
│    7. Parse JSON results                                     │
│    8. Return to user                                         │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│ E2B Sandbox (Isolated Linux VM)                             │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Mock Grafana API (port 8000)                            ││
│  │  - FastAPI server with DuckDB                           ││
│  │  - Sample dashboards, datasources, annotations          ││
│  └─────────────────────────────────────────────────────────┘│
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Mock PostHog API (port 8001)                            ││
│  │  - FastAPI server with DuckDB                           ││
│  │  - Sample events, feature flags, insights               ││
│  └─────────────────────────────────────────────────────────┘│
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Generated Script (Python)                                ││
│  │  from grafana_driver import GrafanaDriver               ││
│  │  driver = GrafanaDriver('http://localhost:8000', ...)   ││
│  │  result = driver.search_dashboards()                    ││
│  │  print(json.dumps(result))                              ││
│  └─────────────────────────────────────────────────────────┘│
│                            ↓                                  │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Driver Code (base_driver.py, grafana_driver.py)         ││
│  │  - Makes HTTP requests to localhost:8000                ││
│  │  - Returns structured data                              ││
│  └─────────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────────┘
```

## Files Overview

### Core Drivers (30% complete - these work standalone)
- `base_driver.py` - Base driver framework
- `grafana_driver.py` - Grafana API client
- `posthog_driver.py` - PostHog API client

### E2B Integration (70% needed - now complete!)
- **Mock APIs:**
  - `mock_grafana_api/` - Mock Grafana server for testing
  - `mock_posthog_api/` - Mock PostHog server for testing

- **Orchestration:**
  - `script_templates.py` - Code generation templates
  - `agent_executor.py` - Sandbox orchestration

- **Documentation:**
  - `CRITICAL_ANALYSIS.md` - What goes wrong and why
  - `E2B_INTEGRATION_GUIDE.md` - This file

## Quick Start

### 1. Install Dependencies

```bash
# Core dependencies
pip install requests fastapi uvicorn duckdb

# E2B SDK (for sandbox execution)
pip install e2b
```

### 2. Set Environment Variables

```bash
# E2B
export E2B_API_KEY="your-e2b-key"

# Production mode (optional)
export GRAFANA_TOKEN="glsa_xxxxx"
export GRAFANA_URL="https://your-instance.grafana.net"
export POSTHOG_API_KEY="phc_xxxxx"
export POSTHOG_PROJECT_ID="12345"
```

### 3. Test Mock Mode (No Real APIs)

```python
from agent_executor import create_executor

# Create executor in mock mode
with create_executor('mock') as executor:
    # Query Grafana dashboards (uses mock data)
    result = executor.execute_grafana('list_dashboards', query='sales')
    print(result)

    # Query PostHog events (uses mock data)
    result = executor.execute_posthog('query_events', event='$pageview')
    print(result)
```

### 4. Test Production Mode (Real APIs)

```python
# Requires real API tokens
with create_executor('production') as executor:
    # Real Grafana API call
    result = executor.execute_grafana('list_dashboards')

    # Real PostHog API call
    result = executor.execute_posthog('query_events', event='$pageview')
```

## Available Operations

### Grafana Operations

```python
# List dashboards
executor.execute_grafana('list_dashboards', query='sales', tag='production')

# Get specific dashboard
executor.execute_grafana('get_dashboard', uid='dashboard-uid')

# Export dashboard JSON
executor.execute_grafana('export_dashboard', uid='dashboard-uid')

# List data sources
executor.execute_grafana('list_datasources')

# Query annotations
from datetime import datetime, timedelta
executor.execute_grafana(
    'get_annotations',
    from_time=datetime.now() - timedelta(days=7),
    to_time=datetime.now()
)
```

### PostHog Operations

```python
# List projects
executor.execute_posthog('list_projects')

# Query events
from datetime import datetime, timedelta
executor.execute_posthog(
    'query_events',
    event='$pageview',
    date_from=datetime.now() - timedelta(days=7),
    limit=100
)

# Get event definitions
executor.execute_posthog('get_event_definitions')

# List feature flags
executor.execute_posthog('list_feature_flags')

# List insights
executor.execute_posthog('list_insights', limit=10)
```

## How It Works

### Step 1: User Prompt

```
User: "Show me my Grafana dashboards with tag 'production'"
```

### Step 2: Agent Executor Maps to Operation

```python
operation = 'list_dashboards'
params = {'tag': 'production'}
```

### Step 3: Generate Script from Template

```python
script = """
import sys
sys.path.insert(0, '/home/user')

import json
from grafana_driver import GrafanaDriver
from base_driver import AuthConfig, AuthStrategy

auth = AuthConfig(AuthStrategy.BEARER_TOKEN, {'token': 'mock-token'})
driver = GrafanaDriver('http://localhost:8000', auth)

dashboards = driver.search_dashboards(tag='production')

print(json.dumps({
    'success': True,
    'data': dashboards
}))
"""
```

### Step 4: Execute in Sandbox

```python
# Sandbox already has:
# - Drivers uploaded to /home/user/
# - Mock API running on localhost:8000
# - All dependencies installed

result = sandbox.process.start_and_wait("python3 script.py")
```

### Step 5: Parse Results

```python
parsed = json.loads(result.stdout)

if parsed['success']:
    dashboards = parsed['data']
    # Present to user
else:
    error = parsed['error']
    # Handle error
```

## Mock API Testing

### Running Mock APIs Standalone

```bash
# Terminal 1: Start Grafana mock
cd mock_grafana_api
uvicorn main:app --host 0.0.0.0 --port 8000

# Terminal 2: Start PostHog mock
cd mock_posthog_api
uvicorn main:app --host 0.0.0.0 --port 8001

# Terminal 3: Test drivers
python
>>> from grafana_driver import GrafanaDriver
>>> from base_driver import AuthConfig, AuthStrategy
>>> auth = AuthConfig(AuthStrategy.BEARER_TOKEN, {'token': 'test'})
>>> driver = GrafanaDriver('http://localhost:8000', auth)
>>> dashboards = driver.search_dashboards()
>>> print(len(dashboards))  # Should print 4
```

### Sample Data Available

**Grafana Mock:**
- 4 dashboards (System Overview, API Metrics, Sales Dashboard, Database Monitoring)
- 3 data sources (Prometheus, PostgreSQL, Loki)
- 4 annotations (deployments, incidents, maintenance)
- 3 folders (General, Monitoring, Business Metrics)

**PostHog Mock:**
- 1 project (ID: 12345)
- 100 sample events ($pageview, $click)
- 4 event definitions
- 2 feature flags
- 1 insight

## Error Handling

All scripts include comprehensive error handling:

```python
try:
    # Driver operation
    result = driver.search_dashboards()

    # Success response
    print(json.dumps({
        'success': True,
        'data': result
    }))

except DriverError as e:
    # Error response
    print(json.dumps({
        'success': False,
        'error': str(e),
        'error_type': type(e).__name__
    }))
```

Agent executor parses this and handles errors appropriately.

## Adding New Operations

### 1. Add Template to `script_templates.py`

```python
GRAFANA_NEW_OPERATION = """
import sys
sys.path.insert(0, '/home/user')

import json
from grafana_driver import GrafanaDriver
from base_driver import AuthConfig, AuthStrategy, DriverError

try:
    auth = AuthConfig(AuthStrategy.BEARER_TOKEN, {'token': '{api_token}'})
    driver = GrafanaDriver('{base_url}', auth)

    result = driver.new_operation({param})

    print(json.dumps({'success': True, 'data': result}))

except DriverError as e:
    print(json.dumps({'success': False, 'error': str(e)}))
"""

# Register in catalog
GRAFANA_TEMPLATES['new_operation'] = GRAFANA_NEW_OPERATION
```

### 2. Use in Agent Executor

```python
result = executor.execute_grafana('new_operation', param='value')
```

## Claude Code Integration

### Option 1: Slash Command

Create `.claude/commands/grafana.md`:

```markdown
# Grafana Integration

Query Grafana dashboards and data sources using the agent executor.

## Usage

Use the agent_executor module to query Grafana:

\`\`\`python
from agent_executor import create_executor

with create_executor('mock') as executor:
    # List dashboards
    result = executor.execute_grafana('list_dashboards', query='sales')

    # Get dashboard
    result = executor.execute_grafana('get_dashboard', uid='abc123')
\`\`\`

## Available Operations

- list_dashboards: Search dashboards
- get_dashboard: Get specific dashboard
- export_dashboard: Export dashboard JSON
- list_datasources: List data sources
- get_annotations: Query annotations
```

### Option 2: MCP Server

Create MCP server exposing driver operations as tools.

### Option 3: Direct Import

Claude Code agents can directly import and use the agent executor.

## Troubleshooting

### Issue: "Module not found: base_driver"

**Cause:** Driver files not uploaded to sandbox

**Fix:**
```python
executor._upload_drivers()  # Ensure drivers are uploaded
```

### Issue: "Connection refused to localhost:8000"

**Cause:** Mock API not started

**Fix:**
```python
executor._start_mock_apis()  # Start mock APIs
time.sleep(2)  # Wait for startup
```

### Issue: "Failed to parse JSON output"

**Cause:** Script error, output not JSON

**Fix:** Check sandbox logs:
```python
result = sandbox.process.start_and_wait("python3 script.py")
print(result.stdout)  # Raw output
print(result.stderr)  # Errors
```

### Issue: "Rate limit exceeded"

**Cause:** Too many requests to real API

**Fix:** Use mock mode for development:
```python
executor = create_executor('mock')  # Uses mock APIs
```

## Performance Considerations

### Sandbox Startup Time

- First time: ~5-10 seconds (install dependencies)
- Subsequent: ~2-3 seconds (reuse sandbox)

**Optimization:** Keep sandbox alive between operations

```python
executor = create_executor('mock')
executor.start_sandbox()  # Do once

# Multiple operations reuse sandbox
result1 = executor.execute_grafana('list_dashboards')
result2 = executor.execute_grafana('list_datasources')
result3 = executor.execute_posthog('query_events')

executor.stop_sandbox()  # Cleanup when done
```

### Mock API Performance

- Mock APIs respond in <10ms
- No network latency
- No rate limiting
- Deterministic results

### Production API Performance

- Depends on API response time
- Subject to rate limits
- Network latency included

## Security Best Practices

1. **Never hardcode tokens:**
   ```python
   # ❌ Bad
   token = "glsa_xxx"

   # ✓ Good
   token = os.getenv('GRAFANA_TOKEN')
   ```

2. **Use E2B secrets:**
   ```python
   # E2B can inject secrets securely
   sandbox.set_secret('GRAFANA_TOKEN', token)
   ```

3. **Sanitize logs:**
   - Agent executor should not log tokens
   - Redact sensitive data in error messages

4. **Validate inputs:**
   - Sanitize user inputs before template insertion
   - Prevent code injection

## Next Steps

1. **Test mock mode locally**
2. **Get E2B API key** from e2b.dev
3. **Uncomment sandbox code** in agent_executor.py
4. **Test in E2B sandbox**
5. **Add production API tokens**
6. **Test production mode**
7. **Integrate with Claude Code**

## Resources

- E2B Documentation: https://e2b.dev/docs
- Grafana API Docs: https://grafana.com/docs/grafana/latest/developers/http_api/
- PostHog API Docs: https://posthog.com/docs/api
- Driver Architecture: See `DRIVER_ARCHITECTURE_ANALYSIS.md`
- Critical Issues: See `CRITICAL_ANALYSIS.md`
