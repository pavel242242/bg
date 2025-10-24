# Flow Example — Daily Sales KPI (Raw→Staged→Gold)
```yaml
id: flow_sales_kpi
owner: analytics@company.com
schedule: "0 6 * * *"   # daily 06:00
sla:
  freshness_minutes: 120
tags: [sales, kpi, daily]
contracts:
  inputs:
    - name: raw.sales_orders
      fields:
        - order_id: string
        - ts: timestamp
        - sales_amount: numeric
        - currency: string
  outputs:
    - name: gold.sales_kpi_daily
      fields:
        - day: date
        - sales: numeric
        - currency: string
steps:
  - name: extract_orders
    type: component:extractor
    source: "e-commerce api"
    retry: {max: 3, backoff_sec: 30}
  - name: load_raw
    type: component:writer
    target: raw.sales_orders
  - name: stage_orders
    type: transformation:sql
    script: stage_sales_orders.sql
    output: staged.sales_orders_clean
    tests:
      - not_null: [order_id, ts, sales_amount]
      - valid_currency: ["USD","EUR","GBP"]
  - name: compute_kpi
    type: transformation:sql
    script: kpi_sales_daily.sql
    output: gold.sales_kpi_daily
    tests:
      - rowcount_delta_pct: [-10, 50]
      - freshness_minutes: 120
alerts:
  - on: failure
    to: "#data-alerts"
  - on: sla_breach
    to: "#data-alerts"
docs: "See runbooks/incidents/pipeline_failure.md"
```
