#!/usr/bin/env python3
"""
Export EV Revolution data to Flourish-compatible CSV files.

This script creates optimized CSV exports from the DuckDB database,
formatted for easy upload to Flourish Studio.
"""

import duckdb
from pathlib import Path
import pandas as pd

# Configuration
DB_PATH = "/home/user/bg/ev_revolution.duckdb"
EXPORT_DIR = Path("/home/user/bg/flourish_exports")

# Create export directory
EXPORT_DIR.mkdir(exist_ok=True)

print("=" * 80)
print("EXPORTING EV DATA FOR FLOURISH STUDIO")
print("=" * 80)
print()

# Connect to DuckDB
conn = duckdb.connect(DB_PATH, read_only=True)

# ============================================================================
# Export 1: Yearly Summary (for line charts)
# ============================================================================
print("📊 Exporting yearly_summary.csv...")

query = """
SELECT
    year,
    total_ev_sales as "Total EV Sales",
    total_vehicle_sales as "Total Vehicle Sales",
    ev_market_share_pct as "EV Market Share %"
FROM yearly_summary
ORDER BY year
"""

df = conn.execute(query).df()
output_file = EXPORT_DIR / "yearly_summary.csv"
df.to_csv(output_file, index=False)
print(f"   ✓ Saved {len(df)} rows to {output_file}")
print()

# ============================================================================
# Export 2: Top Countries (for bar charts)
# ============================================================================
print("📊 Exporting top_countries.csv...")

query = """
SELECT
    country_name as "Country",
    region as "Region",
    total_ev_sales as "Total EV Sales",
    avg_market_share_pct as "Avg Market Share %",
    avg_policy_score as "Policy Score"
FROM top_countries
LIMIT 15
"""

df = conn.execute(query).df()
output_file = EXPORT_DIR / "top_countries.csv"
df.to_csv(output_file, index=False)
print(f"   ✓ Saved {len(df)} rows to {output_file}")
print()

# ============================================================================
# Export 3: Top Manufacturers (for bar charts)
# ============================================================================
print("📊 Exporting top_manufacturers.csv...")

query = """
SELECT
    manufacturer_name as "Manufacturer",
    headquarters_country as "HQ Country",
    total_units_sold as "Total Units Sold",
    total_revenue_millions as "Revenue (Millions USD)"
FROM top_manufacturers
"""

df = conn.execute(query).df()
output_file = EXPORT_DIR / "top_manufacturers.csv"
df.to_csv(output_file, index=False)
print(f"   ✓ Saved {len(df)} rows to {output_file}")
print()

# ============================================================================
# Export 4: Monthly EV Sales by Country (for racing bar charts)
# ============================================================================
print("📊 Exporting ev_sales_monthly.csv...")

query = """
SELECT
    STRFTIME(month, '%Y-%m-%d') as "Date",
    country_name as "Country",
    region as "Region",
    ev_units_sold as "EV Sales",
    ev_market_share_pct as "Market Share %"
FROM ev_sales_with_country
ORDER BY month, country_name
"""

df = conn.execute(query).df()
output_file = EXPORT_DIR / "ev_sales_monthly.csv"
df.to_csv(output_file, index=False)
print(f"   ✓ Saved {len(df)} rows to {output_file}")
print()

# ============================================================================
# Export 5: Policy vs. Adoption (for scatter plots)
# ============================================================================
print("📊 Exporting policy_vs_adoption.csv...")

query = """
SELECT
    country_name as "Country",
    region as "Region",
    AVG(ev_policy_score) as "Policy Score",
    AVG(ev_market_share_pct) as "Market Share %",
    SUM(ev_units_sold) as "Total EV Sales"
FROM ev_sales_with_country
GROUP BY country_name, region
ORDER BY "Total EV Sales" DESC
"""

df = conn.execute(query).df()
output_file = EXPORT_DIR / "policy_vs_adoption.csv"
df.to_csv(output_file, index=False)
print(f"   ✓ Saved {len(df)} rows to {output_file}")
print()

# ============================================================================
# Export 6: Manufacturer Monthly Rankings (for racing bar charts)
# ============================================================================
print("📊 Exporting manufacturer_monthly.csv...")

query = """
SELECT
    STRFTIME(month, '%Y-%m-%d') as "Date",
    manufacturer_name as "Manufacturer",
    headquarters_country as "HQ",
    SUM(units_sold) as "Units Sold",
    SUM(revenue_millions_usd) as "Revenue (M$)"
FROM market_share_full
GROUP BY month, manufacturer_name, headquarters_country
ORDER BY month, "Units Sold" DESC
"""

df = conn.execute(query).df()
output_file = EXPORT_DIR / "manufacturer_monthly.csv"
df.to_csv(output_file, index=False)
print(f"   ✓ Saved {len(df)} rows to {output_file}")
print()

# ============================================================================
# Export 7: Charging Infrastructure Growth (for dual-axis line charts)
# ============================================================================
print("📊 Exporting charging_infrastructure.csv...")

query = """
WITH monthly_agg AS (
    SELECT
        month,
        SUM(public_chargers) as total_chargers,
        AVG(fast_chargers_pct) as avg_fast_pct
    FROM charging_station
    GROUP BY month
),
ev_monthly AS (
    SELECT
        month,
        SUM(ev_units_sold) as total_evs
    FROM ev_sales
    GROUP BY month
)
SELECT
    STRFTIME(c.month, '%Y-%m-%d') as "Date",
    c.total_chargers as "Public Chargers",
    e.total_evs as "EV Sales",
    c.avg_fast_pct as "Fast Chargers %"
FROM monthly_agg c
JOIN ev_monthly e ON c.month = e.month
ORDER BY c.month
"""

df = conn.execute(query).df()
output_file = EXPORT_DIR / "charging_infrastructure.csv"
df.to_csv(output_file, index=False)
print(f"   ✓ Saved {len(df)} rows to {output_file}")
print()

# ============================================================================
# Export 8: Regional Breakdown (for treemap/sankey)
# ============================================================================
print("📊 Exporting regional_breakdown.csv...")

query = """
SELECT
    region as "Region",
    country_name as "Country",
    SUM(ev_units_sold) as "Total EV Sales",
    AVG(ev_market_share_pct) as "Avg Market Share %"
FROM ev_sales_with_country
GROUP BY region, country_name
ORDER BY region, "Total EV Sales" DESC
"""

df = conn.execute(query).df()
output_file = EXPORT_DIR / "regional_breakdown.csv"
df.to_csv(output_file, index=False)
print(f"   ✓ Saved {len(df)} rows to {output_file}")
print()

conn.close()

# ============================================================================
# Create README for Flourish exports
# ============================================================================
print("📝 Creating README...")

readme_content = """# Flourish Studio Export Files

This directory contains CSV files optimized for Flourish Studio visualizations.

## Files

### 1. yearly_summary.csv
**Best for:** Line chart
**Shows:** Global EV sales growth 2020-2025
**Columns:** year, Total EV Sales, Total Vehicle Sales, EV Market Share %

### 2. top_countries.csv
**Best for:** Bar chart (horizontal)
**Shows:** Top 15 EV markets by total sales
**Columns:** Country, Region, Total EV Sales, Avg Market Share %, Policy Score

### 3. top_manufacturers.csv
**Best for:** Bar chart
**Shows:** Leading EV manufacturers by units sold
**Columns:** Manufacturer, HQ Country, Total Units Sold, Revenue (Millions USD)

### 4. ev_sales_monthly.csv
**Best for:** Bar chart race, Line chart race
**Shows:** Monthly EV sales by country over time
**Columns:** Date, Country, Region, EV Sales, Market Share %

### 5. policy_vs_adoption.csv
**Best for:** Scatter plot
**Shows:** Correlation between policy score and market adoption
**Columns:** Country, Region, Policy Score, Market Share %, Total EV Sales

### 6. manufacturer_monthly.csv
**Best for:** Bar chart race
**Shows:** Manufacturer rankings over time
**Columns:** Date, Manufacturer, HQ, Units Sold, Revenue (M$)

### 7. charging_infrastructure.csv
**Best for:** Dual-axis line chart
**Shows:** Infrastructure growth vs. EV sales
**Columns:** Date, Public Chargers, EV Sales, Fast Chargers %

### 8. regional_breakdown.csv
**Best for:** Treemap, Sankey diagram
**Shows:** Regional and country-level sales breakdown
**Columns:** Region, Country, Total EV Sales, Avg Market Share %

## Usage

### Quick Start
1. Go to https://flourish.studio
2. Create free account
3. Click "New visualization"
4. Choose template
5. Upload CSV file
6. Customize and publish

### Recommended Templates

**For ev_sales_monthly.csv:**
- Template: "Bar chart race"
- Settings: Date on timeline, Country as category, EV Sales as value
- Story: "The race to EV dominance"

**For manufacturer_monthly.csv:**
- Template: "Bar chart race"
- Settings: Date on timeline, Manufacturer as category, Units Sold as value
- Story: "Legacy automakers vs. pure EV players"

**For policy_vs_adoption.csv:**
- Template: "Scatter plot"
- Settings: Policy Score on X, Market Share % on Y, Total Sales as size, Region as color
- Story: "Does policy drive adoption?"

**For charging_infrastructure.csv:**
- Template: "Line chart"
- Settings: Date on X, dual Y-axes for Chargers and Sales
- Story: "Infrastructure keeping pace with demand"

## Tips

- **Date format:** Already formatted as YYYY-MM-DD for Flourish
- **Column names:** Human-readable, no need to rename
- **File size:** All files optimized for fast loading
- **Updates:** Re-run `export_to_flourish.py` to regenerate

## Next Steps

See `FLOURISH_INTEGRATION_GUIDE.md` for detailed instructions on:
- Creating specific visualizations
- Using Flourish API (if you have access)
- Building multi-slide stories
- Embedding in websites

---

Generated by: export_to_flourish.py
Source: ev_revolution.duckdb
"""

readme_file = EXPORT_DIR / "README.md"
with open(readme_file, 'w') as f:
    f.write(readme_content)

print(f"   ✓ Created {readme_file}")
print()

# ============================================================================
# Summary
# ============================================================================
print("=" * 80)
print("✅ EXPORT COMPLETE")
print("=" * 80)
print()
print(f"Location: {EXPORT_DIR}")
print()
print("Files created:")
files = sorted(EXPORT_DIR.glob("*.csv"))
for f in files:
    size_kb = f.stat().st_size / 1024
    print(f"  • {f.name} ({size_kb:.1f} KB)")
print(f"  • README.md")
print()
print("Next steps:")
print("  1. Go to https://flourish.studio")
print("  2. Create free account")
print("  3. Upload CSV files")
print("  4. Create visualizations")
print()
print("See FLOURISH_INTEGRATION_GUIDE.md for detailed instructions")
print()
