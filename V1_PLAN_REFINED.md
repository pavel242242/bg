# V1 Implementation Plan - PostHog Driver (Refined)

## Confirmed Scope: Option B - Production-Ready PostHog Driver

**Timeline:** 5 days
**Focus:** Single production-ready driver with real-world use cases

---

## PostHog Capabilities Analysis (Based on Research)

### Core PostHog Architecture
```
PostHog = Product OS
├── Event Capture (SDKs → /i/v0/e/ endpoint)
├── Data Warehouse (built-in, ClickHouse-based)
├── Analytics Suite (insights, funnels, cohorts, etc.)
├── Feature Flags & Experiments
├── Session Replay
└── 120+ Integrations (in/out)
```

### Key PostHog Use Cases (Prioritized for V1)

**Tier 1 (Must Have):**
1. **Event Querying** - Core analytics ("What events happened?")
2. **Feature Flags** - Experiments and rollouts ("What features are live?")
3. **Cohorts** - User segmentation ("Who are our power users?")
4. **Insights** - Saved analytics queries ("How's our funnel performing?")
5. **Projects** - Multi-project support

**Tier 2 (Nice to Have):**
6. **Persons** - Individual user data
7. **Annotations** - Event markers
8. **HogQL Queries** - Flexible SQL-like queries

**Tier 3 (Future):**
9. Session Replays
10. Experiments (detailed)
11. Data warehouse sources/destinations

### PostHog API Patterns

**Event Capture:**
- POST `/i/v0/e/` - Single event
- POST `/batch` - Batch events (optimized)

**Analytics/Query:**
- POST `/api/projects/{id}/query/` - HogQL queries (flexible)
- GET `/api/projects/{id}/events` - List events
- Rate limit: ~120 queries/hour (via external ETL)

**Feature Flags:**
- GET `/api/projects/{id}/feature_flags`
- POST `/api/projects/{id}/feature_flags/local_evaluation`

**Key Insight:** PostHog prefers batch exports over API polling for heavy data transfer.
Our driver should support both:
- Light queries (via API) - For Claude Agent SDK use cases
- Acknowledge batch export pattern (documentation)

---

## V1 Refined Scope

### PostHog Driver Methods (Priority Order)

#### Phase 1: Core Analytics (Days 1-2)
```python
class PostHogDriver(PaginatedDriver):
    # Project management
    def list_projects()
    def get_project(project_id)

    # Event querying (CORE)
    def query_events(event, date_from, date_to, properties, limit)
    def get_event_definitions()
    def get_event_properties(event_name)

    # Feature flags (HIGH VALUE)
    def list_feature_flags()
    def get_feature_flag(flag_id)

    # Basic queries
    def list_insights(limit)
    def get_insight(insight_id)
```

#### Phase 2: User Segmentation (Day 3)
```python
    # Cohorts (user segmentation)
    def list_cohorts()
    def get_cohort(cohort_id)

    # Person data
    def list_persons(limit)
    def get_person(person_id)
    def get_person_properties()
```

#### Phase 3: Advanced (Day 4)
```python
    # HogQL (flexible querying)
    def query_hogql(query)  # Run arbitrary HogQL queries

    # Dashboards
    def list_dashboards()
    def get_dashboard(dashboard_id)
```

### Recipe Library (Based on Real Use Cases)

From the research, these are high-value recipes:

```python
# driver_recipes.py

def find_power_users(driver, action, frequency=5, weeks=7):
    """Who are our power users?
    Users who performed action X at least N times in last Y weeks."""

def find_churn_risk_users(driver, key_event, days_inactive=30):
    """Which users are at risk of churning?
    Users who stopped doing key_event for N days."""

def analyze_funnel_dropoff(driver, funnel_steps):
    """Where are users dropping off?
    Returns dropoff rates at each funnel step."""

def compare_cohort_behavior(driver, cohort_a, cohort_b, metric):
    """How do different user groups compare?
    E.g., paid vs organic users."""

def find_correlated_behaviors(driver, conversion_event, days=30):
    """What behaviors correlate with conversion?
    Which events/properties predict success?"""

def analyze_feature_flag_impact(driver, flag_key, metric_event):
    """Did this feature flag improve metrics?
    Compare users with/without flag."""

def get_user_journey(driver, user_id, days=30):
    """What does this user's journey look like?
    Full event history for support/debugging."""

def track_experiment_results(driver, experiment_id):
    """How's our A/B test performing?
    Statistical analysis of variants."""

def find_error_patterns(driver, error_event, days=7):
    """What errors are affecting users most?
    Frequency, impacted users, patterns."""

def calculate_retention_cohort(driver, cohort_id, period='weekly'):
    """How well do we retain users?
    Cohort-based retention analysis."""
```

---

## Updated 5-Day Plan

### Day 1: Core Setup & Validation
**Goal:** Driver works in E2B sandbox

- [ ] Build E2B template with PostHog driver + mock API
- [ ] Test basic imports in E2B
- [ ] Implement core methods (list_projects, query_events, list_feature_flags)
- [ ] Test with mock PostHog API
- [ ] **Milestone:** Driver executes queries in E2B

### Day 2: Claude Agent SDK Integration
**Goal:** Claude can use driver directly

- [ ] Create example Claude Agent script
- [ ] Import driver: `from posthog_driver import PostHogDriver`
- [ ] Execute 3 key operations:
  - Query events
  - List feature flags
  - Get event definitions
- [ ] Extend driver with custom method (show extensibility)
- [ ] **Milestone:** Claude Agent successfully queries PostHog

### Day 3: Production API Testing
**Goal:** Driver works with real PostHog

- [ ] Set up real PostHog project (free tier)
- [ ] Test all implemented methods with production API
- [ ] Handle rate limits (120 queries/hour consideration)
- [ ] Test error scenarios (bad auth, network issues, etc.)
- [ ] Implement remaining Tier 1 methods (cohorts, insights)
- [ ] **Milestone:** All Tier 1 methods production-validated

### Day 4: Recipe Library
**Goal:** 10+ ready-to-use patterns

- [ ] Implement 10 recipes based on common use cases:
  - find_power_users
  - find_churn_risk_users
  - analyze_funnel_dropoff
  - get_user_journey
  - find_correlated_behaviors
  - analyze_feature_flag_impact
  - track_experiment_results
  - compare_cohort_behavior
  - find_error_patterns
  - calculate_retention_cohort
- [ ] Test each recipe with mock and real data
- [ ] Document usage examples
- [ ] **Milestone:** Recipe library complete

### Day 5: Testing & Documentation
**Goal:** Production-ready release

- [ ] Unit tests for driver methods
- [ ] Integration tests (E2B + mock API)
- [ ] Complete API documentation
- [ ] Quick start guide
- [ ] Troubleshooting guide
- [ ] Recipe catalog
- [ ] **Milestone:** V1 ready for use

---

## V1 Deliverables (Updated)

### Code
- [x] `base_driver.py` - Already built
- [ ] `posthog_driver.py` - Enhanced with all Tier 1 + Tier 2 methods
- [x] `mock_posthog_api/` - Already built, may need enhancements
- [ ] `driver_recipes.py` - 10 PostHog-specific recipes
- [x] `e2b.Dockerfile` - Already built
- [ ] `tests/` - Unit and integration tests
- [ ] `examples/` - Claude Agent SDK usage examples

### Documentation
- [ ] `QUICKSTART_POSTHOG.md` - 5-minute getting started
- [ ] `API_REFERENCE_POSTHOG.md` - Complete method documentation
- [ ] `RECIPES_POSTHOG.md` - Recipe catalog with use cases
- [ ] `USE_CASES.md` - Map real questions to driver methods
- [ ] `TROUBLESHOOTING.md` - Common issues

### Validation
- [ ] E2B template builds successfully
- [ ] Driver works in E2B sandbox
- [ ] Mock API covers all driver methods
- [ ] Claude Agent SDK can import and use driver
- [ ] Production API validation (real PostHog account)
- [ ] All tests passing
- [ ] All recipes tested

---

## Success Criteria (Refined)

### Must Have (V1 Release)
1. ✅ PostHog driver with Tier 1 methods (events, flags, cohorts, insights)
2. ✅ Works in E2B sandbox with mock API
3. ✅ Claude Agent SDK can import and extend driver
4. ✅ 10+ production-tested recipes
5. ✅ Works with real PostHog API (validated on production)
6. ✅ Complete documentation (quick start, API ref, recipes)
7. ✅ Zero known critical bugs

### V1 Use Cases Validated
Based on research, these questions should be answerable:
- ✅ "Who are our power users?" (recipe: find_power_users)
- ✅ "Which users might churn?" (recipe: find_churn_risk_users)
- ✅ "Where do users drop off in our funnel?" (recipe: analyze_funnel_dropoff)
- ✅ "What features do power users use?" (query_events + cohorts)
- ✅ "Did our feature flag improve metrics?" (recipe: analyze_feature_flag_impact)
- ✅ "What errors are users hitting?" (recipe: find_error_patterns)
- ✅ "What's this user's journey?" (recipe: get_user_journey)

---

## Key Insights from Research

### 1. PostHog's Architecture Philosophy
- **Built-in data warehouse** - Not just analytics, it's a data platform
- **120+ integrations** - Brings data in and sends data out
- **Real-time + Batch** - Different patterns for different needs
- **HogQL** - SQL-like queries on ClickHouse

**Implication for Driver:**
- Support flexible querying (HogQL method)
- Document batch export pattern (for heavy data transfer)
- Focus on analytics queries (not heavy ETL)

### 2. Common Questions PostHog Answers
From the research, key personas and questions:
- **Product Managers:** Power users, churn risk, feature usage
- **Growth:** Channel performance, cohort behavior
- **UX:** Funnel drop-offs, user paths
- **Data Analysts:** Correlations, trends
- **Engineers:** Error tracking, performance
- **Experiments:** A/B test results

**Implication for Recipes:**
Each persona should have 1-2 recipes that directly answer their questions.

### 3. API Patterns
- **Event capture:** High throughput, batching preferred
- **Query API:** For analytics, has rate limits
- **Batch exports:** For heavy data transfer (outside V1 scope)

**Implication for Driver:**
- Query API for analytics (our focus)
- Document rate limits
- Note: For heavy ETL, use PostHog's batch exports (not driver)

---

## Risk Mitigation (Updated)

### Risk: Rate Limits
**Mitigation:**
- Document rate limits in driver
- Implement backoff/retry
- Advise using batch exports for heavy workloads

### Risk: PostHog API Changes
**Mitigation:**
- Use stable API endpoints
- Version pin in documentation
- Test with real API regularly

### Risk: Mock API Divergence
**Mitigation:**
- Validate mock responses match real API
- Test all recipes with production data
- Document any mock limitations

---

## Next Steps

1. **Confirm refined scope** - Is this the right set of methods and recipes?
2. **Set up PostHog account** - Need real PostHog project for testing
3. **Start Day 1** - Build E2B template, test in sandbox
4. **Iterate daily** - Complete one phase per day

Ready to start Day 1 when you are!
