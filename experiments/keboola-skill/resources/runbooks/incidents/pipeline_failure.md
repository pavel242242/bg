# Incident Playbook — Pipeline Failure
**Severity:** SEV-2 (data unavailable for key users)

## 1. Triage
- Confirm blast radius (which consumers, which tables)
- Freshness gap (minutes)
- Identify failing step & owner

## 2. Stabilize
- Rollback to last healthy gold snapshot
- Pause downstream consumers (toggle read-only mode)

## 3. Diagnose
- Check logs & last code changes
- Validate upstream availability and schema
- Re-run failing step with debug flags

## 4. Remediate
- Patch fix with PR + code review
- Backfill missing window
- Re-enable downstream

## 5. Learn
- Blameless postmortem (root cause, contributing factors)
- Add tests/alerts to prevent recurrence
- Update runbook links in Flow
