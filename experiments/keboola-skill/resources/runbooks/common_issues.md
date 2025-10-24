# Common Issues, Errors, and Fixes

## 1) Authentication / Authorization Failures
**Symptoms:** 401/403, expired tokens, role not allowed.  
**Fix:** Rotate credentials; verify role grants; test with minimal `SELECT 1`.  
**Prevention:** Use service accounts, short-lived tokens, and secrets management.

## 2) Freshness SLA Breach
**Symptoms:** Freshness minutes > SLO.  
**Debug:** Check upstream source lags; orchestration queue; long-running steps.  
**Fix:** Increase parallelism; optimize slow transforms; backfill missing windows.  
**Prevention:** Alert on lag early (warn), auto-scale warehouse/pool.

## 3) Schema Drift
**Symptoms:** New/drop/renamed fields; type changes.  
**Debug:** Compare contract vs. actual; inspect CDC events.  
**Fix:** Add compatibility columns; cast types; version schemas.  
**Prevention:** Enforce **Data Contracts**; field-level lineage; contract tests.

## 4) Duplicates / Keys
**Symptoms:** Duplicate primary keys, exploding joins.  
**Debug:** Check dedupe step and sort keys; look for late-arriving events.  
**Fix:** Idempotent dedupe; windows; watermarking.  
**Prevention:** Unique constraints; pre-join distincts; audit row counts.

## 5) Distribution Shift (Models)
**Symptoms:** AUC drop; calibration off; action rates swing.  
**Debug:** PSI/KS tests; feature drift; data leakage checks.  
**Fix:** Recalibrate thresholds; retrain; feature sanitation.  
**Prevention:** Monitor features; keep training snapshots; data app for drift.

## 6) Quotas / Cost Spikes
**Symptoms:** Job failures; spend alerts.  
**Debug:** Examine query plans; check retries & partitions.  
**Fix:** Cluster/partition; cache results; reduce fan-out.  
**Prevention:** Budget alerts; cost attribution tags; CI guardrails.

## 7) Orchestration Failures
**Symptoms:** DAG stuck; tasks retry forever.  
**Debug:** Inspect logs; reproduce failing unit locally.  
**Fix:** Add timeouts; circuit breakers; graceful degradation outputs.  
**Prevention:** Split monolith DAGs; idempotent tasks; backoff.
