# Incident Playbook — Data Quality Breach
**Severity:** SEV-2 (incorrect metrics shipped)

## 1. Triage
- Identify affected metrics and consumers
- Quantify error magnitude & time window
- Freeze downstream publishing

## 2. Stabilize
- Promote last certified dataset (if available)
- Display banner in Data App: "Under Review"

## 3. Diagnose
- Which validation failed (freshness/volume/schema/distribution)?
- Trace lineage to the source of drift
- Reproduce transformation locally

## 4. Remediate
- Fix contract/transform; reprocess
- Validate with additional assertions
- Communicate recovery ETA to stakeholders

## 5. Learn
- Add missing validation and contract tests
- Document edge case; update dictionary/contract
- Schedule health review for this domain
