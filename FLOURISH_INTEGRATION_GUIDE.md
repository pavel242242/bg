# Flourish Studio Integration Guide
## Publishing EV Revolution Data to Flourish for Interactive Visualizations

---

## Overview

**Flourish Studio** is a powerful data visualization platform perfect for creating interactive, publication-ready charts and stories. This guide shows how to publish our EV Revolution dataset to Flourish.

### What We Have
- 5 tables (country, manufacturer, ev_sales, charging_station, market_share)
- 1,750+ records of time-series data
- DuckDB database with analytical views
- Perfect for visual storytelling

### What Flourish Can Create
- Racing bar charts (manufacturer market share over time)
- Line charts (EV sales growth trends)
- Scatter plots (policy score vs. adoption)
- Sankey diagrams (regional flow)
- Interactive stories (multi-slide narratives)

---

## Two Approaches

### 🎯 Approach 1: Simple (No API Key Required)
**Best for:** Quick start, manual control, free accounts
1. Export data to CSV
2. Upload to Flourish Studio UI
3. Create visualizations through web interface

### 🚀 Approach 2: Programmatic (Requires API Key)
**Best for:** Automation, live updates, enterprise use
1. Install `flourishcharts` Python package
2. Use API to create and update visualizations
3. Embed in websites or apps

**Note:** Flourish API is enterprise-level and requires a paid account with API access.

---

## Approach 1: Export for Flourish UI (Simple)

### Step 1: Export Data to CSV

Run the export script:
```bash
python3 export_to_flourish.py
```

This creates Flourish-optimized CSVs in `flourish_exports/`:
- `yearly_summary.csv` - For line charts
- `top_countries.csv` - For bar charts
- `top_manufacturers.csv` - For racing bars
- `ev_sales_monthly.csv` - For time series
- `policy_vs_adoption.csv` - For scatter plots

### Step 2: Upload to Flourish

1. Go to https://flourish.studio
2. Create account (free tier available)
3. Click "New visualization"
4. Choose template (e.g., "Line chart race", "Bar chart race")
5. Upload CSV
6. Customize styling
7. Publish & share

### Recommended Visualizations

#### 1. Bar Chart Race: EV Sales by Country
**Template:** Bar chart race
**Data:** `ev_sales_monthly.csv`
**Settings:**
- X-axis: month (date)
- Y-axis: ev_units_sold
- Category: country_name
- Animation: Auto-play

**Story:** Watch countries compete for EV market leadership 2020-2025

---

#### 2. Line Chart: Global EV Growth
**Template:** Line chart
**Data:** `yearly_summary.csv`
**Settings:**
- X-axis: year
- Y-axis: total_ev_sales
- Secondary Y-axis: ev_market_share_pct

**Story:** The exponential rise of electric vehicles

---

#### 3. Scatter Plot: Policy Impact
**Template:** Scatter plot
**Data:** `policy_vs_adoption.csv`
**Settings:**
- X-axis: avg_policy_score
- Y-axis: avg_market_share_pct
- Size: total_ev_sales
- Color: region

**Story:** Strong policy = higher adoption (with notable exceptions)

---

#### 4. Racing Bar: Manufacturer Battle
**Template:** Bar chart race
**Data:** `manufacturer_monthly.csv`
**Settings:**
- X-axis: month
- Y-axis: units_sold
- Category: manufacturer_name
- Color: headquarters_country

**Story:** Legacy automakers vs. pure EV players

---

## Approach 2: Programmatic API (Advanced)

### Prerequisites

**1. Flourish API Key**
- Go to https://app.flourish.studio/settings
- Generate API key (requires enterprise/business account)
- Store securely

**2. Install Package**
```bash
pip install flourishcharts
```

**3. Set Environment Variable**
```bash
export FLOURISH_API_KEY="your_key_here"
```

### Using the API

See `flourish_api_example.py` for full implementation.

**Basic Pattern:**
```python
from flourishcharts import Flourish
import pandas as pd

# Initialize
flourish = Flourish(api_key="your_key")

# Load data
df = pd.read_csv("flourish_exports/yearly_summary.csv")

# Create chart
chart = flourish.create_chart(
    chart_type="line",
    data=df,
    title="Global EV Sales Growth 2020-2025"
)

# Publish
chart.publish()
print(f"Chart URL: {chart.url}")
```

---

## Data Export Script Details

The `export_to_flourish.py` script creates optimized CSV files:

### Features
- **Time formatting:** ISO8601 dates for Flourish's date parser
- **Column naming:** Human-readable headers
- **Aggregations:** Pre-calculated summaries for faster loading
- **Wide format:** Optimized for Flourish's data binding

### Customization

Edit the script to create custom exports:
```python
# Example: Create monthly manufacturer rankings
query = """
SELECT
    month,
    manufacturer_name,
    SUM(units_sold) as total_units,
    ROW_NUMBER() OVER (PARTITION BY month ORDER BY SUM(units_sold) DESC) as rank
FROM market_share_full
GROUP BY month, manufacturer_name
ORDER BY month, rank
"""
```

---

## Best Practices for Flourish

### 1. Data Preparation
✅ **Do:**
- Use clear column names ("Country" not "country_id")
- Format dates as YYYY-MM-DD or ISO8601
- Pre-aggregate large datasets
- Include metadata columns (region, category, etc.)

❌ **Don't:**
- Upload massive raw datasets (>50K rows can be slow)
- Use database IDs as labels
- Mix data types in columns

### 2. Chart Selection
| Data Type | Best Flourish Template |
|-----------|----------------------|
| Time series comparison | Line chart race |
| Rankings over time | Bar chart race |
| Part-to-whole | Sankey, treemap |
| Correlation | Scatter plot |
| Geographic | Map (with lat/lon) |
| Multi-slide story | Story template |

### 3. Storytelling
- Start with context (what's the big picture?)
- Show change over time (animations engage)
- Highlight outliers (callouts, annotations)
- End with insight (so what?)

---

## Example: Creating a Flourish Story

**Goal:** Multi-slide narrative about EV revolution

### Slide 1: The Global Picture
- **Viz:** Line chart of total EV sales
- **Caption:** "From 4.6M in 2020 to explosive growth by 2025"

### Slide 2: Regional Leaders
- **Viz:** Bar chart race by region
- **Caption:** "Asia dominates volume, Europe leads adoption"

### Slide 3: Infrastructure Race
- **Viz:** Dual-axis line (EVs vs. chargers)
- **Caption:** "Charging infrastructure kept pace"

### Slide 4: Policy Matters
- **Viz:** Scatter plot (policy score vs. market share)
- **Caption:** "Strong policy correlates with faster adoption"

### Slide 5: The Winners
- **Viz:** Bar chart of top manufacturers
- **Caption:** "Legacy automakers fight back"

**Export all data → Upload to Flourish Story template → Publish**

---

## Integration with This Repo

### Current Exports Available

Run the export script to generate:
```bash
python3 export_to_flourish.py
```

**Outputs:**
- `flourish_exports/` directory
- 6 CSV files ready for Flourish
- README with upload instructions

### Automation (with API)

For live dashboards:
```bash
# 1. Regenerate data (optional)
cd /tmp/datagen
datagen generate /home/user/bg/voronoi_ev_story_schema.json --seed 42

# 2. Export to Flourish
python3 export_to_flourish.py

# 3. Update Flourish charts (requires API)
python3 flourish_api_update.py
```

**Use case:** Monthly data refreshes with auto-updating charts

---

## Cost Considerations

### Flourish Pricing (as of 2025)

| Plan | Price | Features | Best For |
|------|-------|----------|----------|
| **Free** | $0/mo | 5 public visualizations, Flourish branding | Trying it out |
| **Solo** | $59/mo | Unlimited visualizations, no branding | Individual creators |
| **Business** | $99/mo | Team collaboration, API access | Small teams |
| **Enterprise** | Custom | Advanced API, SSO, support | Large orgs |

**For this project:**
- Free tier works for initial prototyping
- Solo tier if publishing multiple charts
- Business tier needed for API automation

---

## Technical Limitations

### Flourish Free Tier
- ❌ No API access
- ❌ Flourish branding on charts
- ✅ Full template library
- ✅ CSV uploads
- ✅ Public sharing

### Flourish API (Business+)
- ✅ Programmatic chart creation
- ✅ Live data connections
- ✅ Automated updates
- ❌ Requires paid plan
- ❌ More complex setup

**Recommendation:** Start with free tier + CSV exports, upgrade if you need automation.

---

## Alternative: Public Data Hosting

If you don't want to pay for Flourish API, use **Live CSV** feature:

### Setup
1. Export CSVs to `flourish_exports/`
2. Host on GitHub Pages, S3, or Google Drive
3. Get public URL (e.g., `https://raw.githubusercontent.com/user/repo/main/data.csv`)
4. In Flourish UI, choose "Import from URL"
5. Paste URL
6. Set auto-refresh interval

**Benefit:** Charts update automatically when you push new CSV to GitHub

---

## Comparison: Flourish vs. Other Tools

| Feature | Flourish | Tableau Public | D3.js | Plotly |
|---------|----------|----------------|-------|--------|
| **Ease of use** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| **Interactivity** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Animations** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **API access** | ⭐⭐⭐ (paid) | ❌ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Free tier** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Storytelling** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |

**Why Flourish for this project:**
- Racing bar charts (perfect for manufacturer competition)
- Story templates (multi-slide narrative)
- Beautiful defaults (less design work)
- Easy sharing (publish & get link)

---

## Next Steps

### Quick Start (5 minutes)
1. Run `python3 export_to_flourish.py`
2. Go to https://flourish.studio
3. Create free account
4. Upload `yearly_summary.csv`
5. Choose "Line chart" template
6. Publish & share

### Full Implementation (1 hour)
1. Export all datasets
2. Create 5 visualizations (one per insight)
3. Combine into Flourish Story
4. Publish story
5. Embed in VORONOI_CREATOR_APPLICATION.md

### Advanced (with API access)
1. Get Flourish Business account
2. Generate API key
3. Install `flourishcharts`
4. Run `flourish_api_example.py`
5. Automate updates with cron/GitHub Actions

---

## Support & Resources

### Official Docs
- **Main site:** https://flourish.studio
- **Developer docs:** https://developers.flourish.studio
- **API reference:** https://developers.flourish.studio/api
- **Examples:** https://developers.flourish.studio/api/examples

### Community
- **Help center:** https://help.flourish.studio
- **Twitter:** @f_l_o_u_r_i_s_h
- **Showcase:** https://flourish.studio/examples

### Our Implementation
- Export script: `export_to_flourish.py`
- API example: `flourish_api_example.py` (optional)
- Data directory: `flourish_exports/`

---

## Conclusion

**Flourish Studio is perfect for this EV dataset because:**
1. ✅ Time-series animations (bar chart races)
2. ✅ Beautiful defaults (professional out-of-the-box)
3. ✅ Easy sharing (publish & embed)
4. ✅ Story templates (multi-slide narratives)
5. ✅ Free tier available (no upfront cost)

**The workflow:**
```
datagen → DuckDB → CSV export → Flourish upload → Interactive viz → Share
```

**Time to first chart: < 10 minutes**

---

*Run `python3 export_to_flourish.py` to get started.*
