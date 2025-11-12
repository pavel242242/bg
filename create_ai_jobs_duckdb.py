#!/usr/bin/env python3
"""
Export AI Jobs data to DuckDB and Flourish-compatible CSV files.
"""

import duckdb
from pathlib import Path
import pandas as pd

# Configuration
DATA_DIR = Path("/home/user/bg/ai_jobs_data")
DB_PATH = "/home/user/bg/ai_jobs_displacement.duckdb"
EXPORT_DIR = Path("/home/user/bg/ai_jobs_flourish")

# Create export directory
EXPORT_DIR.mkdir(exist_ok=True)

print("=" * 80)
print("CREATING AI JOBS DUCKDB DATABASE & FLOURISH EXPORTS")
print("=" * 80)
print()

# ============================================================================
# Part 1: Create DuckDB Database
# ============================================================================
print("📊 Creating DuckDB database...")
conn = duckdb.connect(DB_PATH)

# Import parquet files
tables = ["region", "industry", "role", "job_displacement", "ai_tool_adoption"]

for table_name in tables:
    parquet_file = DATA_DIR / f"{table_name}.parquet"
    print(f"   📥 Importing {table_name}...")

    conn.execute(f"""
        CREATE TABLE {table_name} AS
        SELECT * FROM read_parquet('{parquet_file}')
    """)

    count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    print(f"      ✓ Loaded {count:,} rows")

print()

# Create analytical views
print("📊 Creating analytical views...")

# View: Full job displacement with all context
conn.execute("""
    CREATE VIEW job_displacement_full AS
    SELECT
        jd.*,
        r.region_name,
        r.continent,
        r.digital_workforce_millions,
        r.ai_adoption_index,
        r.avg_digital_wage_usd,
        i.industry_name,
        i.automation_vulnerability,
        ro.role_name,
        ro.replacement_rate,
        ro.avg_wage_before_ai_usd
    FROM job_displacement jd
    JOIN region r ON jd.region_id = r.region_id
    JOIN industry i ON jd.industry_id = i.industry_id
    JOIN role ro ON jd.role_id = ro.role_id
""")

# View: Yearly summary
conn.execute("""
    CREATE VIEW yearly_summary AS
    SELECT
        EXTRACT(YEAR FROM quarter) AS year,
        SUM(jobs_displaced) AS total_jobs_displaced,
        SUM(jobs_created_ai_adjacent) AS total_jobs_created,
        SUM(net_job_loss) AS total_net_loss,
        AVG(productivity_multiplier) AS avg_productivity_multiplier,
        AVG(wage_suppression_pct) AS avg_wage_suppression_pct
    FROM job_displacement
    GROUP BY year
    ORDER BY year
""")

# View: Top vulnerable roles
conn.execute("""
    CREATE VIEW top_vulnerable_roles AS
    SELECT
        role_name,
        SUM(jobs_displaced) AS total_displaced,
        SUM(net_job_loss) AS total_net_loss,
        AVG(replacement_rate) AS avg_replacement_rate,
        AVG(wage_suppression_pct) AS avg_wage_suppression,
        AVG(avg_wage_before_ai_usd) AS avg_wage_before_ai
    FROM job_displacement_full
    GROUP BY role_name
    ORDER BY total_displaced DESC
""")

# View: Industry impact
conn.execute("""
    CREATE VIEW industry_impact AS
    SELECT
        industry_name,
        automation_vulnerability,
        SUM(jobs_displaced) AS total_displaced,
        SUM(net_job_loss) AS total_net_loss,
        AVG(productivity_multiplier) AS avg_productivity_multiplier
    FROM job_displacement_full
    GROUP BY industry_name, automation_vulnerability
    ORDER BY total_displaced DESC
""")

# View: Regional impact
conn.execute("""
    CREATE VIEW regional_impact AS
    SELECT
        region_name,
        continent,
        digital_workforce_millions,
        SUM(jobs_displaced) AS total_displaced,
        SUM(net_job_loss) AS total_net_loss,
        AVG(wage_suppression_pct) AS avg_wage_suppression
    FROM job_displacement_full
    GROUP BY region_name, continent, digital_workforce_millions
    ORDER BY total_displaced DESC
""")

print("   ✓ Created 5 analytical views")
print()

# ============================================================================
# Part 2: Export Flourish-Compatible CSVs
# ============================================================================
print("📊 Exporting Flourish CSVs...")
print()

# Export 1: Yearly Trend
print("   Exporting yearly_trend.csv...")
query = """
SELECT
    year as "Year",
    total_jobs_displaced as "Jobs Displaced",
    total_jobs_created as "Jobs Created (AI-Adjacent)",
    total_net_loss as "Net Job Loss",
    avg_productivity_multiplier as "Productivity Multiplier",
    avg_wage_suppression_pct as "Wage Suppression %"
FROM yearly_summary
"""
df = conn.execute(query).df()
df.to_csv(EXPORT_DIR / "yearly_trend.csv", index=False)
print(f"      ✓ {len(df)} rows")

# Export 2: Top Roles
print("   Exporting top_roles.csv...")
query = """
SELECT
    role_name as "Role",
    total_displaced as "Total Jobs Displaced",
    total_net_loss as "Net Job Loss",
    avg_replacement_rate as "AI Replacement Rate",
    avg_wage_suppression as "Wage Suppression %"
FROM top_vulnerable_roles
LIMIT 20
"""
df = conn.execute(query).df()
df.to_csv(EXPORT_DIR / "top_roles.csv", index=False)
print(f"      ✓ {len(df)} rows")

# Export 3: Industry Impact
print("   Exporting industry_impact.csv...")
query = """
SELECT
    industry_name as "Industry",
    automation_vulnerability as "Vulnerability Score",
    total_displaced as "Jobs Displaced",
    total_net_loss as "Net Job Loss",
    avg_productivity_multiplier as "Productivity Multiplier"
FROM industry_impact
"""
df = conn.execute(query).df()
df.to_csv(EXPORT_DIR / "industry_impact.csv", index=False)
print(f"      ✓ {len(df)} rows")

# Export 4: Regional Impact
print("   Exporting regional_impact.csv...")
query = """
SELECT
    region_name as "Region",
    continent as "Continent",
    total_displaced as "Jobs Displaced",
    total_net_loss as "Net Job Loss",
    avg_wage_suppression as "Wage Suppression %"
FROM regional_impact
LIMIT 15
"""
df = conn.execute(query).df()
df.to_csv(EXPORT_DIR / "regional_impact.csv", index=False)
print(f"      ✓ {len(df)} rows")

# Export 5: Quarterly Displacement (for time series racing charts)
print("   Exporting quarterly_by_role.csv...")
query = """
SELECT
    quarter as "Quarter",
    role_name as "Role",
    SUM(jobs_displaced) as "Jobs Displaced",
    AVG(wage_suppression_pct) as "Wage Suppression %"
FROM job_displacement_full
GROUP BY quarter, role_name
ORDER BY quarter, "Jobs Displaced" DESC
"""
df = conn.execute(query).df()
df.to_csv(EXPORT_DIR / "quarterly_by_role.csv", index=False)
print(f"      ✓ {len(df)} rows")

# Export 6: Quarterly by Industry
print("   Exporting quarterly_by_industry.csv...")
query = """
SELECT
    quarter as "Quarter",
    industry_name as "Industry",
    SUM(jobs_displaced) as "Jobs Displaced",
    AVG(productivity_multiplier) as "Productivity Multiplier"
FROM job_displacement_full
GROUP BY quarter, industry_name
ORDER BY quarter, "Jobs Displaced" DESC
"""
df = conn.execute(query).df()
df.to_csv(EXPORT_DIR / "quarterly_by_industry.csv", index=False)
print(f"      ✓ {len(df)} rows")

# Export 7: AI Adoption vs Displacement
print("   Exporting ai_adoption_correlation.csv...")
query = """
WITH adoption_yearly AS (
    SELECT
        EXTRACT(YEAR FROM quarter) as year,
        AVG(companies_using_ai_pct) as avg_ai_adoption_pct,
        AVG(avg_ai_spend_per_employee_usd) as avg_ai_spend
    FROM ai_tool_adoption
    GROUP BY year
),
displacement_yearly AS (
    SELECT
        year,
        total_jobs_displaced,
        total_net_loss
    FROM yearly_summary
)
SELECT
    a.year as "Year",
    a.avg_ai_adoption_pct as "AI Adoption %",
    a.avg_ai_spend as "AI Spend per Employee (USD)",
    d.total_jobs_displaced as "Jobs Displaced",
    d.total_net_loss as "Net Job Loss"
FROM adoption_yearly a
JOIN displacement_yearly d ON a.year = d.year
ORDER BY a.year
"""
df = conn.execute(query).df()
df.to_csv(EXPORT_DIR / "ai_adoption_correlation.csv", index=False)
print(f"      ✓ {len(df)} rows")

# Export 8: Replacement Rate Analysis
print("   Exporting replacement_rates.csv...")
query = """
SELECT
    role_name as "Role",
    avg_replacement_rate as "Replacement Rate",
    total_displaced as "Jobs Displaced",
    avg_wage_before_ai as "Avg Wage Before AI (USD)"
FROM top_vulnerable_roles
WHERE total_displaced > 50000
ORDER BY avg_replacement_rate DESC
"""
df = conn.execute(query).df()
df.to_csv(EXPORT_DIR / "replacement_rates.csv", index=False)
print(f"      ✓ {len(df)} rows")

conn.close()

print()
print("=" * 80)
print("✅ EXPORT COMPLETE")
print("=" * 80)
print()
print(f"DuckDB Database: {DB_PATH}")
print(f"Flourish Exports: {EXPORT_DIR}")
print()
print("Query examples:")
print(f"  duckdb {DB_PATH} \"SELECT * FROM yearly_summary\"")
print(f"  duckdb {DB_PATH} \"SELECT * FROM top_vulnerable_roles LIMIT 10\"")
print()
print("Flourish-ready files:")
for csv_file in sorted(EXPORT_DIR.glob("*.csv")):
    size_kb = csv_file.stat().st_size / 1024
    print(f"  • {csv_file.name} ({size_kb:.1f} KB)")
print()
