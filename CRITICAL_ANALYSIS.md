# CRITICAL ANALYSIS: What Will Go Wrong

## Executive Summary

**CRITICAL GAP IDENTIFIED:** The current driver implementation is designed as standalone Python clients, but they need to run as **Claude Code agents executing inside E2B sandboxes**. This architectural mismatch creates multiple failure points.

---

## 🚨 Critical Issues

### 1. **E2B Sandbox Network Restrictions**

**WILL GO WRONG:**
```
❌ Drivers try to connect to external APIs from inside sandbox
❌ E2B sandbox has network egress restrictions
❌ API calls timeout or fail with connection errors
```

**Why It Fails:**
- E2B sandboxes may block outbound HTTPS connections
- Grafana/PostHog APIs require external network access
- No fallback or mock API available

**Impact:** 🔴 **SHOWSTOPPER** - Drivers can't function without network access

**Solution Required:**
```python
# Need to detect sandbox environment and route through proxy
if os.getenv('E2B_SANDBOX'):
    # Route through E2B network proxy
    session.proxies = {'https': 'http://e2b-proxy:8080'}
```

---

### 2. **Missing Mock APIs for Development**

**WILL GO WRONG:**
```
❌ No way to test drivers without hitting real APIs
❌ Development requires valid API tokens
❌ Rate limiting during testing
❌ Can't reproduce bugs without production access
```

**What's Missing (compared to Salesforce example):**
- Salesforce had `mock_api/` with FastAPI + DuckDB
- Grafana needs mock endpoints for dashboards, datasources, annotations
- PostHog needs mock endpoints for events, insights, feature flags

**Impact:** 🔴 **CRITICAL** - Can't develop or test in isolation

**Missing Files:**
```
❌ mock_grafana_api/
   ❌ main.py          # FastAPI server
   ❌ db.py            # Mock data storage
   ❌ fixtures.py      # Sample dashboards, annotations

❌ mock_posthog_api/
   ❌ main.py          # FastAPI server
   ❌ db.py            # Mock event storage
   ❌ fixtures.py      # Sample events, feature flags
```

---

### 3. **No Agent Executor Integration**

**WILL GO WRONG:**
```
❌ Claude Code agent doesn't know these drivers exist
❌ No script generation templates
❌ Agent can't orchestrate driver execution
❌ No sandbox upload/deployment logic
```

**What's Missing:**
```python
# ❌ MISSING: agent_executor.py equivalent
class GrafanaAgentExecutor:
    def __init__(self, sandbox):
        self.sandbox = sandbox
        # Upload driver to sandbox
        # Upload mock API to sandbox
        # Start mock API service
        # Generate and execute scripts

    def execute_prompt(self, user_prompt):
        # Map prompt to script template
        # Execute in sandbox
        # Parse results
```

**Impact:** 🔴 **SHOWSTOPPER** - No way for Claude Code to use the drivers

---

### 4. **Missing Script Templates**

**WILL GO WRONG:**
```
❌ Agent generates incorrect driver usage code
❌ Import paths wrong (not in sandbox filesystem)
❌ Error handling missing
❌ Result formatting inconsistent
```

**What's Missing:**
```python
# ❌ MISSING: script_templates.py
GRAFANA_LIST_DASHBOARDS = """
import sys
sys.path.insert(0, '/home/user')

from grafana_driver import GrafanaDriver
from base_driver import AuthConfig, AuthStrategy

auth = AuthConfig(AuthStrategy.BEARER_TOKEN, {'token': '{api_token}'})
driver = GrafanaDriver('{base_url}', auth)

dashboards = driver.search_dashboards(query='{query}')
print(json.dumps(dashboards, indent=2))
"""

POSTHOG_QUERY_EVENTS = """
# Similar template for PostHog
"""
```

**Impact:** 🔴 **CRITICAL** - Agent can't generate working code

---

### 5. **Dependency Installation in Sandbox**

**WILL GO WRONG:**
```
❌ E2B sandbox doesn't have `requests` installed
❌ `pip install` fails or takes too long
❌ Version conflicts with sandbox Python
```

**Current Issue:**
- `requirements.txt` exists but who installs it in sandbox?
- E2B sandboxes are ephemeral - installs happen on EVERY run
- Slow startup times

**Impact:** 🟡 **MAJOR** - Performance and reliability issues

**Solution Required:**
```python
# agent_executor.py needs to:
def _setup_sandbox(self):
    # Install dependencies
    self.sandbox.process.start_and_wait(
        "pip install requests"
    )
```

---

### 6. **Authentication Secrets in Sandbox**

**WILL GO WRONG:**
```
❌ API tokens passed as plaintext to sandbox
❌ Tokens logged in E2B execution logs
❌ Environment variables not propagated to sandbox
❌ Security audit nightmare
```

**Current Issue:**
```python
# This is INSECURE in E2B context:
driver = GrafanaDriver.from_env()  # ❌ Env vars don't exist in sandbox
```

**What Should Happen:**
```python
# Agent executor needs to inject secrets securely
script = TEMPLATE.format(
    api_token=self._get_secret('GRAFANA_TOKEN'),  # From Claude Code secrets
    base_url=self._get_secret('GRAFANA_URL')
)
```

**Impact:** 🔴 **CRITICAL** - Security vulnerability

---

### 7. **Error Propagation from Sandbox**

**WILL GO WRONG:**
```
❌ Driver raises exception inside sandbox
❌ Exception lost in JSON parsing
❌ Agent sees "JSONDecodeError" instead of real error
❌ User gets useless error message
```

**Current Issue:**
```python
# Inside sandbox, this fails:
driver.get_dashboard_by_uid('bad-uid')
# Raises ResourceNotFoundError

# But agent_executor sees:
# "Failed to parse JSON: Traceback (most recent call last)..."
```

**Solution Required:**
```python
# Script template needs error handling:
try:
    result = driver.search_dashboards()
    print(json.dumps({'success': True, 'data': result}))
except DriverError as e:
    print(json.dumps({'success': False, 'error': str(e), 'type': type(e).__name__}))
```

**Impact:** 🟡 **MAJOR** - Poor debugging experience

---

### 8. **Pagination in Sandbox Context**

**WILL GO WRONG:**
```
❌ Agent requests 10,000 events
❌ Driver starts paginating inside sandbox
❌ Sandbox times out after 5 minutes
❌ Partial results lost
```

**Current Issue:**
```python
# This could run for hours in sandbox:
for event in driver._paginate('events', page_size=100):
    process(event)
```

**Solution Required:**
- Add `max_pages` limit in templates
- Add timeout handling
- Stream results back to agent incrementally

**Impact:** 🟡 **MAJOR** - Sandbox timeouts

---

### 9. **No Discovery/Schema Caching**

**WILL GO WRONG:**
```
❌ Agent asks "what dashboards exist?"
❌ Driver queries API
❌ Agent asks "get dashboard X"
❌ Driver queries API again (could use cached list)
```

**What Salesforce Did Right:**
```python
# agent_executor.py cached discovered objects
self.discovered_objects = self._discover_objects()
# Then used cache for script generation
```

**Impact:** 🟡 **MAJOR** - Unnecessary API calls, rate limiting

---

### 10. **Claude Code Agent Prompt Mapping**

**WILL GO WRONG:**
```
❌ User: "Show me my Grafana dashboards"
❌ Agent: "I don't know how to do that"
❌ Or agent generates random Python code instead of using driver
```

**What's Missing:**
- No system prompt telling Claude Code these drivers exist
- No examples of driver usage in prompts
- No capability declaration

**Required Addition:**
```markdown
# .claude/commands/grafana.md or MCP server
You have access to Grafana and PostHog drivers for data extraction.

Available operations:
- List Grafana dashboards: Use GrafanaDriver.search_dashboards()
- Query PostHog events: Use PostHogDriver.query_events()
...

Examples:
[show script template examples]
```

**Impact:** 🔴 **SHOWSTOPPER** - Agent doesn't use drivers at all

---

## 🏗️ Correct Architecture (E2B + Claude Code)

```
┌─────────────────────────────────────────────────────────────┐
│  Claude Code Agent (Host)                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Agent Executor                                         │ │
│  │  - Maps user prompt to script template               │ │
│  │  - Creates E2B sandbox                               │ │
│  │  - Uploads drivers + mock API                        │ │
│  │  - Starts mock API service (if dev mode)            │ │
│  │  - Generates execution script                        │ │
│  │  - Executes in sandbox                               │ │
│  │  - Parses JSON results                               │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  E2B Sandbox (Isolated VM)                                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Mock API (FastAPI)                    [localhost:8000] │ │
│  │  - Mock Grafana endpoints                             │ │
│  │  - Mock PostHog endpoints                             │ │
│  │  - DuckDB backend with fixtures                       │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Generated Script (Python)                              │ │
│  │  import sys                                            │ │
│  │  sys.path.insert(0, '/home/user')                     │ │
│  │  from grafana_driver import GrafanaDriver             │ │
│  │                                                         │ │
│  │  driver = GrafanaDriver('http://localhost:8000', ...) │ │
│  │  dashboards = driver.search_dashboards()              │ │
│  │  print(json.dumps(dashboards))                        │ │
│  └────────────────────────────────────────────────────────┘ │
│                       │                                      │
│                       ▼                                      │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Grafana/PostHog Driver                                 │ │
│  │  - Makes HTTP requests to localhost:8000              │ │
│  │  - Or real API if production mode                     │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 What Must Be Added

### Priority 1: SHOWSTOPPERS (Must have to function)

1. **Agent Executor** (`agent_executor.py`)
   - Sandbox orchestration
   - Driver upload logic
   - Mock API deployment
   - Script generation from templates
   - Result parsing

2. **Script Templates** (`script_templates.py`)
   - Pre-built patterns for common operations
   - Proper error handling
   - JSON output formatting
   - Sandbox path configuration

3. **Mock APIs** (`mock_grafana_api/`, `mock_posthog_api/`)
   - FastAPI servers
   - DuckDB backends
   - Sample data fixtures
   - Endpoint implementations

4. **Claude Code Integration** (`.claude/commands/` or MCP server)
   - System prompts with driver documentation
   - Capability declarations
   - Usage examples

### Priority 2: CRITICAL (Needed for reliability)

5. **Sandbox Dependency Manager**
   - Pre-install requirements
   - Handle installation failures
   - Version pinning

6. **Secret Management**
   - Secure token injection
   - Environment variable handling
   - Logging sanitization

7. **Error Propagation**
   - Structured error responses
   - Error type preservation
   - Stack trace capture

### Priority 3: IMPORTANT (Needed for production)

8. **Result Streaming**
   - Incremental output for large datasets
   - Pagination limits
   - Timeout handling

9. **Discovery Caching**
   - Cache API metadata
   - Reduce redundant calls
   - Smart invalidation

10. **Testing Infrastructure**
    - Unit tests with mocks
    - Integration tests with sandbox
    - Claude Code agent tests

---

## 🎯 Comparison: What Exists vs What's Needed

| Component | Current Status | Required for E2B+Claude | Gap |
|-----------|---------------|------------------------|-----|
| Base Driver | ✅ Implemented | ✅ Good | None |
| Grafana Driver | ✅ Implemented | ✅ Good | None |
| PostHog Driver | ✅ Implemented | ✅ Good | None |
| Mock Grafana API | ❌ Missing | ✅ Required | 🔴 Critical |
| Mock PostHog API | ❌ Missing | ✅ Required | 🔴 Critical |
| Agent Executor | ❌ Missing | ✅ Required | 🔴 Showstopper |
| Script Templates | ❌ Missing | ✅ Required | 🔴 Showstopper |
| Claude Code Integration | ❌ Missing | ✅ Required | 🔴 Showstopper |
| Sandbox Deployment | ❌ Missing | ✅ Required | 🔴 Critical |
| Error Handling | ⚠️ Partial | ✅ Required | 🟡 Major |
| Secret Management | ❌ Missing | ✅ Required | 🔴 Critical |

---

## 🚀 Immediate Next Steps

1. **Create Mock APIs** (2-3 hours)
   - Grafana mock with dashboards, datasources, annotations
   - PostHog mock with events, feature flags

2. **Implement Agent Executor** (3-4 hours)
   - Sandbox orchestration
   - Upload drivers and mocks
   - Generate scripts from templates

3. **Add Script Templates** (1-2 hours)
   - List dashboards, export dashboard
   - Query events, list feature flags
   - Proper error handling

4. **Create Claude Code Integration** (1 hour)
   - Slash command or MCP server
   - System prompt with driver docs
   - Usage examples

5. **Test End-to-End** (2 hours)
   - Claude Code → Agent Executor → E2B Sandbox → Mock API
   - Verify error handling
   - Verify result parsing

---

## 💡 How This Leverages Claude Code

**Claude Code's Role:**
1. **Prompt Understanding:** User says "show my Grafana dashboards"
2. **Intent Mapping:** Claude Code maps to `list_dashboards` template
3. **Script Generation:** Fills template with user params
4. **Sandbox Orchestration:** Creates E2B sandbox via agent executor
5. **Execution:** Runs script in isolated environment
6. **Result Processing:** Parses JSON output, formats for user

**Why E2B:**
- **Isolation:** API drivers run in sandboxed environment
- **Security:** Credentials never touch host system
- **Repeatability:** Each run starts fresh
- **Testing:** Mock APIs run inside sandbox

**Current State:**
- ❌ Drivers exist but can't be invoked by Claude Code
- ❌ No bridge between "user prompt" and "driver execution"

**Required State:**
- ✅ Agent executor orchestrates everything
- ✅ Script templates map prompts to code
- ✅ Mock APIs enable testing
- ✅ Claude Code can demonstrate driver usage without real APIs

---

## 🎬 Conclusion

**What We Have:**
- ✅ Well-designed driver abstractions
- ✅ Complete API coverage
- ✅ Good error handling in drivers

**What We Need:**
- ❌ The orchestration layer (agent executor)
- ❌ The testing layer (mock APIs)
- ❌ The integration layer (script templates + Claude Code config)

**Current State:** Drivers are like a car engine without a chassis, wheels, or steering wheel.

**Bottom Line:** The drivers are 30% of the solution. Need to build the other 70% to make this work in E2B + Claude Code context.
