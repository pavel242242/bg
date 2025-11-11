# Quick Start: Driver Framework with E2B

## TL;DR

```bash
# 1. Install E2B CLI
brew install e2b-dev/e2b/e2b  # or: npm install -g @e2b/cli

# 2. Build custom template
e2b template init
e2b template build

# 3. Use in Python
python
>>> from agent_executor_simplified import create_executor
>>> executor = create_executor('mock', template_id='your-template-id')
>>> result = executor.execute_grafana('list_dashboards')
>>> print(result['data'])
```

---

## Step-by-Step Guide

### Prerequisites

1. **E2B Account**
   - Sign up: https://e2b.dev
   - Get API key: https://e2b.dev/dashboard

2. **Install E2B CLI**
   ```bash
   # Option A: Homebrew (Mac/Linux)
   brew install e2b-dev/e2b/e2b

   # Option B: NPM
   npm install -g @e2b/cli

   # Verify
   e2b version
   ```

3. **Set API Key**
   ```bash
   export E2B_API_KEY="your-api-key-here"
   ```

---

### Step 1: Create E2B Template

**Why:** Pre-install all dependencies so sandboxes start instantly (~150ms)

```bash
# Initialize template
e2b template init

# This creates e2b.Dockerfile
# Use the provided e2b.Dockerfile from this repo
cp e2b.Dockerfile e2b.Dockerfile  # Already includes everything needed

# Build template
e2b template build

# Output:
# ✓ Building template...
# ✓ Template built successfully!
# Template ID: template_abc123xyz
```

**Save your template ID!** You'll use it in code.

---

### Step 2: Install Python SDK

```bash
pip install e2b requests
```

---

### Step 3: Test in Mock Mode

```python
from agent_executor_simplified import create_executor

# Create executor with your template ID
executor = create_executor(
    mode='mock',
    template_id='template_abc123xyz'  # Your template ID
)

# Query Grafana (uses mock API)
result = executor.execute_grafana('list_dashboards', query='sales')

print(f"Found {result['count']} dashboards")
for dashboard in result['data']:
    print(f"  - {dashboard['title']} ({dashboard['uid']})")

# Query PostHog (uses mock API)
result = executor.execute_posthog('query_events', event='$pageview', limit=10)

print(f"Found {result['count']} events")
```

**Expected Output:**
```
Found 4 dashboards
  - System Overview (system-overview)
  - API Metrics (api-metrics)
  - Sales Dashboard (sales-dashboard)
  - Database Monitoring (database-monitoring)

Found 10 events
```

---

### Step 4: Use in Production Mode

```python
import os

# Set real API credentials
os.environ['GRAFANA_TOKEN'] = 'glsa_your_token_here'
os.environ['GRAFANA_URL'] = 'https://your-instance.grafana.net'
os.environ['POSTHOG_API_KEY'] = 'phc_your_key_here'
os.environ['POSTHOG_PROJECT_ID'] = '12345'

# Create executor in production mode
executor = create_executor(
    mode='production',
    template_id='template_abc123xyz'
)

# Query real APIs
dashboards = executor.execute_grafana('list_dashboards')
events = executor.execute_posthog('query_events', event='$pageview')
```

---

## Available Operations

### Grafana

```python
# List dashboards
executor.execute_grafana('list_dashboards', query='sales', tag='production', limit=50)

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
    to_time=datetime.now(),
    tags=['deployment']
)
```

### PostHog

```python
# List projects
executor.execute_posthog('list_projects')

# Query events
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

---

## Response Format

All operations return JSON:

```python
{
    'success': True,
    'data': [...],        # The actual results
    'count': 4            # Number of items (where applicable)
}

# Or on error:
{
    'success': False,
    'error': 'Resource not found: dashboard-uid',
    'error_type': 'ResourceNotFoundError'
}
```

---

## Testing Mock APIs Locally (No E2B Needed)

```bash
# Terminal 1: Start Grafana mock
cd mock_grafana_api
uvicorn main:app --host 0.0.0.0 --port 8000

# Terminal 2: Start PostHog mock
cd mock_posthog_api
uvicorn main:app --host 0.0.0.0 --port 8001

# Terminal 3: Test drivers directly
python
>>> from grafana_driver import GrafanaDriver
>>> from base_driver import AuthConfig, AuthStrategy
>>> auth = AuthConfig(AuthStrategy.BEARER_TOKEN, {'token': 'test'})
>>> driver = GrafanaDriver('http://localhost:8000', auth)
>>> dashboards = driver.search_dashboards()
>>> print(len(dashboards))  # Should print 4
```

---

## Troubleshooting

### "Template not found"

**Fix:** Make sure you built the template and saved the ID
```bash
e2b template build
# Use the ID from output
```

### "E2B_API_KEY not set"

**Fix:**
```bash
export E2B_API_KEY="your-key"
# Or pass directly:
executor = SimplifiedAgentExecutor(
    template_id='...',
    e2b_api_key='your-key'
)
```

### "Module not found: base_driver"

**Fix:** Rebuild template to include all files
```bash
# Make sure e2b.Dockerfile has COPY commands
e2b template build --force
```

### "Connection refused to localhost:8000"

**Fix:** Wait longer for mock API to start
```python
# In agent_executor_simplified.py, increase sleep time:
time.sleep(5)  # Instead of 2
```

### "Failed to parse script output"

**Fix:** Check sandbox logs for errors
```python
result = sandbox.run_code(script)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
```

---

## Performance

- **Template build:** One-time, ~30-60 seconds
- **Sandbox startup:** ~150ms (with custom template)
- **Mock API response:** <10ms
- **Real API response:** Depends on API (usually 100-500ms)

---

## What's Happening Under the Hood

```
1. You call: executor.execute_grafana('list_dashboards')
   ↓
2. E2B creates sandbox from your template (~150ms)
   ✓ All drivers already installed
   ✓ All dependencies already installed
   ✓ Python environment ready
   ↓
3. Executor starts mock API in sandbox (if mock mode)
   $ cd mock_grafana_api && uvicorn main:app --port 8000 &
   ↓
4. Executor generates Python script from template
   import sys; sys.path.insert(0, '/home/user')
   from grafana_driver import GrafanaDriver
   driver = GrafanaDriver('http://localhost:8000', ...)
   result = driver.search_dashboards()
   print(json.dumps({'success': True, 'data': result}))
   ↓
5. E2B executes script in sandbox
   ✓ Captures stdout/stderr automatically
   ✓ Handles timeouts
   ✓ Isolated from host
   ↓
6. Executor parses JSON from stdout
   {'success': True, 'data': [...], 'count': 4}
   ↓
7. Results returned to you
```

---

## Next Steps

1. **Try mock mode** - No real APIs needed
2. **Create custom template** - Pre-install everything
3. **Test with real APIs** - Set credentials, use production mode
4. **Integrate with Claude Code** - Use in agents (see CLAUDE_INTEGRATION.md)

---

## Resources

- E2B Documentation: https://e2b.dev/docs
- E2B Templates Guide: https://e2b.dev/docs/sandbox-template
- Driver Architecture: See `DRIVER_ARCHITECTURE_ANALYSIS.md`
- E2B Reality Check: See `E2B_REALITY_CHECK.md`
- Full Integration Guide: See `E2B_INTEGRATION_GUIDE.md`
