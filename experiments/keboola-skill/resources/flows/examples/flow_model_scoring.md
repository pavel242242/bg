# Flow Example — Model Scoring (Explainable First)
```yaml
id: flow_churn_scoring
owner: data-science@company.com
schedule: "0 */4 * * *"   # every 4 hours
tags: [ml, scoring, churn]
contracts:
  inputs:
    - name: staged.customer_features
  outputs:
    - name: gold.churn_scores
    - name: gold.churn_feature_importance
steps:
  - name: score_logistic_regression
    type: transformation:python
    script: score_logit.py
    params:
      threshold: 0.35    # policy: optimize F1
  - name: write_scores
    type: transformation:sql
    script: write_scores.sql
  - name: validate
    type: transformation:sql
    script: validate_scoring.sql
    tests:
      - distribution_shift_ks: [probability, 0.1]
      - null_rate_pct: [probability, 0, 1]
docs: "See runbooks/incidents/model_drift.md"
```
