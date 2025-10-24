"""
Streamlit Data App Scaffold — BigQuery (Keboola Workspace)
----------------------------------------------------------
Usage:
  - Authenticate via a service account key (JSON) or default credentials.
  - In Keboola Workspace, set GOOGLE_APPLICATION_CREDENTIALS appropriately.
Env:
  GCP_PROJECT=...
  BQ_DATASET=...
  BQ_TABLE=...
"""

import os
import streamlit as st
import pandas as pd
from google.cloud import bigquery

PROJECT = os.getenv("GCP_PROJECT")
DATASET = os.getenv("BQ_DATASET", "dataset")
TABLE = os.getenv("BQ_TABLE", "my_table")
TABLE_REF = f"{PROJECT}.{DATASET}.{TABLE}"
LIMIT = 1000

client = bigquery.Client(project=PROJECT)

st.title("Example App — BigQuery")
st.caption("Freshness • Trend • Segmentation • Download")

QUERY_FRESHNESS = f"""
SELECT MAX(ingested_at) AS max_ingest_ts, TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), MAX(ingested_at), MINUTE) AS minutes_ago
FROM `{TABLE_REF}`;
"""

QUERY_KPI = f"""
SELECT DATE(ts) AS day, SUM(sales_amount) AS sales
FROM `{TABLE_REF}`
GROUP BY 1
ORDER BY 1
"""

QUERY_SAMPLE = f"""
SELECT * FROM `{TABLE_REF}`
ORDER BY ingested_at DESC
LIMIT {LIMIT}
"""

@st.cache_data(ttl=60)
def run_query(sql):
    df = client.query(sql).to_dataframe(create_bqstorage_client=True)
    return df

try:
    df_fresh = run_query(QUERY_FRESHNESS)
    minutes = int(df_fresh["minutes_ago"].iloc[0]) if not df_fresh.empty else None
    st.metric("Freshness (minutes)", minutes if minutes is not None else "n/a")
except Exception as e:
    st.warning(f"Freshness query failed: {e}")

try:
    df_kpi = run_query(QUERY_KPI)
    st.line_chart(df_kpi, x="day", y="sales")
except Exception as e:
    st.warning(f"KPI query failed: {e}")

try:
    df = run_query(QUERY_SAMPLE)
    st.dataframe(df.head(50))
    st.download_button("Download CSV", df.to_csv(index=False).encode("utf-8"), file_name="sample.csv", mime="text/csv")
except Exception as e:
    st.warning(f"Preview failed: {e}")

st.markdown("---")
st.caption("Notes: Add masking/policies for PII. Prefer parameterized queries for user filters. Log app queries to a telemetry table for observability.")
