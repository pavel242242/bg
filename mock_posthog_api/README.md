# Mock PostHog API

FastAPI-based mock implementation of PostHog API for E2B sandbox testing.

## Running

```bash
cd mock_posthog_api
uvicorn main:app --host 0.0.0.0 --port 8001
```

## Endpoints

- `GET /api/users/@me` - Current user
- `GET /api/projects` - List projects
- `GET /api/projects/{id}/events` - Query events
- `GET /api/projects/{id}/event_definitions` - Event definitions
- `GET /api/projects/{id}/feature_flags` - List feature flags
- `GET /api/projects/{id}/insights` - List insights

## Sample Data

- Project ID: 12345
- 100 sample events ($pageview, $click)
- 4 event definitions
- 2 feature flags
- 1 insight

## Testing

```python
from posthog_driver import PostHogDriver
from base_driver import AuthConfig, AuthStrategy

auth = AuthConfig(AuthStrategy.BEARER_TOKEN, {'token': 'test'})
driver = PostHogDriver('http://localhost:8001', auth, project_id=12345)

events = driver.query_events(event='$pageview')
print(f"Events: {len(events)}")
```
