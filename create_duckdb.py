#!/usr/bin/env python3
"""
Export EV Revolution data to DuckDB for easy querying and sharing.
"""

import duckdb
from pathlib import Path

# Create DuckDB connection
db_path = "/home/user/bg/ev_revolution.duckdb"
conn = duckdb.connect(db_path)

data_dir = Path("/home/user/bg/ev_data")

print("=" * 80)
print("CREATING DUCKDB DATABASE: ev_revolution.duckdb")
print("=" * 80)
print()

# Import each parquet file as a table
tables = [
    "country",
    "manufacturer",
    "ev_sales",
    "charging_station",
    "market_share"
]

for table_name in tables:
    parquet_file = data_dir / f"{table_name}.parquet"
    print(f"📥 Importing {table_name}...")

    conn.execute(f"""
        CREATE TABLE {table_name} AS
        SELECT * FROM read_parquet('{parquet_file}')
    """)

    count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    print(f"   ✓ Loaded {count:,} rows")

print()
print("=" * 80)
print("CREATING VIEWS FOR ANALYSIS")
print("=" * 80)
print()

# Create useful views
print("📊 Creating view: ev_sales_with_country...")
conn.execute("""
    CREATE VIEW ev_sales_with_country AS
    SELECT
        s.*,
        c.country_name,
        c.region,
        c.population_millions,
        c.gdp_per_capita_usd,
        c.ev_policy_score
    FROM ev_sales s
    JOIN country c ON s.country_id = c.country_id
""")

print("📊 Creating view: charging_with_country...")
conn.execute("""
    CREATE VIEW charging_with_country AS
    SELECT
        ch.*,
        c.country_name,
        c.region,
        c.population_millions
    FROM charging_station ch
    JOIN country c ON ch.country_id = c.country_id
""")

print("📊 Creating view: market_share_full...")
conn.execute("""
    CREATE VIEW market_share_full AS
    SELECT
        ms.*,
        c.country_name,
        c.region,
        m.manufacturer_name,
        m.headquarters_country
    FROM market_share ms
    JOIN country c ON ms.country_id = c.country_id
    JOIN manufacturer m ON ms.manufacturer_id = m.manufacturer_id
""")

print("📊 Creating view: yearly_summary...")
conn.execute("""
    CREATE VIEW yearly_summary AS
    SELECT
        EXTRACT(YEAR FROM month) AS year,
        SUM(ev_units_sold) AS total_ev_sales,
        SUM(total_vehicle_sales) AS total_vehicle_sales,
        (SUM(ev_units_sold) * 100.0 / SUM(total_vehicle_sales)) AS ev_market_share_pct
    FROM ev_sales
    GROUP BY year
    ORDER BY year
""")

print("📊 Creating view: top_countries...")
conn.execute("""
    CREATE VIEW top_countries AS
    SELECT
        country_name,
        region,
        SUM(ev_units_sold) AS total_ev_sales,
        AVG(ev_market_share_pct) AS avg_market_share_pct,
        AVG(ev_policy_score) AS avg_policy_score
    FROM ev_sales_with_country
    GROUP BY country_name, region
    ORDER BY total_ev_sales DESC
""")

print("📊 Creating view: top_manufacturers...")
conn.execute("""
    CREATE VIEW top_manufacturers AS
    SELECT
        manufacturer_name,
        headquarters_country,
        SUM(units_sold) AS total_units_sold,
        SUM(revenue_millions_usd) AS total_revenue_millions
    FROM market_share_full
    GROUP BY manufacturer_name, headquarters_country
    ORDER BY total_units_sold DESC
""")

print()
print("=" * 80)
print("SAMPLE QUERIES")
print("=" * 80)
print()

print("Query 1: Yearly Growth Summary")
print("-" * 80)
result = conn.execute("SELECT * FROM yearly_summary").df()
print(result.to_string(index=False))
print()

print("Query 2: Top 10 Countries")
print("-" * 80)
result = conn.execute("SELECT * FROM top_countries LIMIT 10").df()
print(result.to_string(index=False))
print()

print("Query 3: Top 10 Manufacturers")
print("-" * 80)
result = conn.execute("SELECT * FROM top_manufacturers LIMIT 10").df()
print(result.to_string(index=False))
print()

# Get database info
print("=" * 80)
print("DATABASE INFORMATION")
print("=" * 80)
print()

tables_info = conn.execute("""
    SELECT
        table_name,
        (SELECT COUNT(*) FROM information_schema.columns
         WHERE table_name = t.table_name) as num_columns
    FROM information_schema.tables t
    WHERE table_schema = 'main' AND table_type = 'BASE TABLE'
    ORDER BY table_name
""").df()

print("Tables:")
print(tables_info.to_string(index=False))
print()

views_info = conn.execute("""
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'main' AND table_type = 'VIEW'
    ORDER BY table_name
""").df()

print("Views:")
for view in views_info['table_name']:
    print(f"  - {view}")
print()

conn.close()

print("=" * 80)
print(f"✅ DuckDB database created: {db_path}")
print("=" * 80)
print()
print("To query this database:")
print(f"  duckdb {db_path}")
print()
print("Example queries:")
print("  SELECT * FROM yearly_summary;")
print("  SELECT * FROM top_countries LIMIT 10;")
print("  SELECT * FROM ev_sales_with_country WHERE country_name = 'Norway';")
print()
