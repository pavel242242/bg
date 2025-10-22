# Flow Example — CDC Orders (Near-Real-Time)
```yaml
id: flow_cdc_orders
owner: platform@company.com
schedule: "*/5 * * * *"   # every 5 minutes
tags: [cdc, streaming, orders]
contracts:
  inputs:
    - name: mysql.orders (cdc)
  outputs:
    - name: staged.orders_stream
    - name: gold.orders_current
steps:
  - name: cdc_ingest
    type: component:datastreams
    source: mysql.orders
    mode: cdc
  - name: apply_schema
    type: transformation:python
    script: apply_schema_and_dedupe.py
  - name: publish_current
    type: transformation:sql
    script: publish_orders_current.sql
    tests:
      - duplicate_keys: [order_id]
      - freshness_minutes: 10
monitoring:
  - metric: pipeline_success_rate
  - metric: lag_minutes
docs: "Docs/Contracts/orders_contract.md"
```
