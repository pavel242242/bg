"""
Streamlit Data App Scaffold — Snowflake (Keboola Workspace)
-----------------------------------------------------------
Usage:
  - This app expects a Keboola Workspace with a Snowflake connection.
  - Provide connection info via environment variables or a `secrets.toml`:
      SNOWFLAKE_ACCOUNT=...
      SNOWFLAKE_USER=...
      SNOWFLAKE_PASSWORD=...
      SNOWFLAKE_ROLE=...
      SNOWFLAKE_WAREHOUSE=...
      SNOWFLAKE_DATABASE=...
      SNOWFLAKE_SCHEMA=...
  - In Keboola, mount this as a Workspace app or run locally for dev.
"""

import os
import streamlit as st
import pandas as pd

try:
    import snowflake.connector
except ImportError:
    st.error("Please install snowflake-connector-python")
    st.stop()

# --- Sidebar: configuration ---
st.sidebar.header("Config")
TABLE = st.sidebar.text_input("Table (DATABASE.SCHEMA.TABLE)", value=os.getenv("SNOWFLAKE_DATABASE","DB")+"."+os.getenv("SNOWFLAKE_SCHEMA","SCHEMA")+".MY_TABLE")
LIMIT = st.sidebar.number_input("Row limit", min_value=10, max_value=100000, value=1000, step=10)

# --- Header ---
st.title("Sales KPI — Example App (Snowflake)")
st.caption("Freshness • Trend • Segmentation • Download")

# --- Connection helper ---
def snowflake_conn():
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        role=os.getenv("SNOWFLAKE_ROLE"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
    )

# --- Queries ---
QUERY_FRESHNESS = f"""
SELECT MAX(ingested_at) AS max_ingest_ts, DATEDIFF('minute', MAX(ingested_at), CURRENT_TIMESTAMP()) AS minutes_ago
FROM {TABLE};
"""

QUERY_SAMPLE = f"""
SELECT * FROM {TABLE}
ORDER BY ingested_at DESC
LIMIT {LIMIT};
"""

QUERY_KPI = f"""
SELECT DATE_TRUNC('day', ts) AS day, SUM(sales_amount) AS sales
FROM {TABLE}
GROUP BY 1
ORDER BY 1;
"""

def run_query(sql):
    with snowflake_conn() as conn:
        cur = conn.cursor()
        cur.execute(sql)
        cols = [c[0] for c in cur.description]
        rows = cur.fetchall()
        return pd.DataFrame(rows, columns=cols)

# --- Freshness ---
with st.expander("Freshness"):
    try:
        df_fresh = run_query(QUERY_FRESHNESS)
        minutes = int(df_fresh["MINUTES_AGO"].iloc[0]) if not df_fresh.empty else None
        st.metric("Freshness (minutes)", minutes if minutes is not None else "n/a")
    except Exception as e:
        st.warning(f"Freshness query failed: {e}")

# --- KPI Trend ---
with st.expander("KPI: Sales Trend"):
    try:
        df_kpi = run_query(QUERY_KPI)
        st.line_chart(df_kpi, x="DAY", y="SALES")
    except Exception as e:
        st.warning(f"KPI query failed: {e}")

# --- Data Preview & Download ---
with st.expander("Data Preview & Download"):
    try:
        df = run_query(QUERY_SAMPLE)
        st.dataframe(df.head(50))
        st.download_button("Download CSV", df.to_csv(index=False).encode("utf-8"), file_name="sample.csv", mime="text/csv")
    except Exception as e:
        st.warning(f"Preview failed: {e}")

st.markdown("---")
st.caption("Notes: This scaffold uses idempotent read-only queries. Add role-based access and masking for PII. Use Contracts + Validation in your pipeline.")
