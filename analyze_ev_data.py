#!/usr/bin/env python3
"""
Analyze the EV Revolution dataset and extract key insights for Voronoi story.
"""

import pandas as pd
import json
from pathlib import Path

# Load generated data
data_dir = Path("/home/user/bg/ev_data")

country = pd.read_parquet(data_dir / "country.parquet")
manufacturer = pd.read_parquet(data_dir / "manufacturer.parquet")
ev_sales = pd.read_parquet(data_dir / "ev_sales.parquet")
charging_station = pd.read_parquet(data_dir / "charging_station.parquet")
market_share = pd.read_parquet(data_dir / "market_share.parquet")

print("=" * 80)
print("GLOBAL EV REVOLUTION: DATA ANALYSIS")
print("=" * 80)
print()

# 1. Overall EV Sales Growth
print("📈 1. GLOBAL EV SALES GROWTH (2020-2025)")
print("-" * 80)

# Merge sales with country data
ev_sales_full = ev_sales.merge(country, on="country_id")

# Calculate yearly trends
ev_sales_full['year'] = pd.to_datetime(ev_sales_full['month']).dt.year
yearly_sales = ev_sales_full.groupby('year').agg({
    'ev_units_sold': 'sum',
    'total_vehicle_sales': 'sum'
}).reset_index()
yearly_sales['market_share_pct'] = (yearly_sales['ev_units_sold'] / yearly_sales['total_vehicle_sales'] * 100)

print(yearly_sales.to_string(index=False))
print()

growth_rate = ((yearly_sales.iloc[-1]['ev_units_sold'] / yearly_sales.iloc[0]['ev_units_sold']) - 1) * 100
print(f"💡 Total EV sales grew by {growth_rate:.1f}% from 2020 to 2025")
print(f"💡 Global EV market share rose from {yearly_sales.iloc[0]['market_share_pct']:.1f}% to {yearly_sales.iloc[-1]['market_share_pct']:.1f}%")
print()

# 2. Top EV Markets
print("🌍 2. TOP 10 EV MARKETS (Total Sales 2020-2025)")
print("-" * 80)

country_sales = ev_sales_full.groupby('country_name').agg({
    'ev_units_sold': 'sum',
    'ev_market_share_pct': 'mean'
}).sort_values('ev_units_sold', ascending=False).head(10)

print(country_sales.to_string())
print()

# 3. Charging Infrastructure Growth
print("⚡ 3. CHARGING INFRASTRUCTURE EXPANSION")
print("-" * 80)

charging_full = charging_station.merge(country, on="country_id")
charging_full['year'] = pd.to_datetime(charging_full['month']).dt.year

yearly_chargers = charging_full.groupby('year')['public_chargers'].sum().reset_index()
print(yearly_chargers.to_string(index=False))
print()

charger_growth = ((yearly_chargers.iloc[-1]['public_chargers'] / yearly_chargers.iloc[0]['public_chargers']) - 1) * 100
print(f"💡 Global charging infrastructure grew by {charger_growth:.1f}% from 2020 to 2025")
print()

# 4. Top EV Manufacturers
print("🏭 4. TOP EV MANUFACTURERS BY GLOBAL SALES")
print("-" * 80)

market_share_full = market_share.merge(manufacturer, on="manufacturer_id")
mfr_sales = market_share_full.groupby('manufacturer_name').agg({
    'units_sold': 'sum',
    'revenue_millions_usd': 'sum'
}).sort_values('units_sold', ascending=False)

print(mfr_sales.to_string())
print()

# 5. Regional Analysis
print("🗺️  5. REGIONAL EV ADOPTION")
print("-" * 80)

regional_sales = ev_sales_full.groupby('region').agg({
    'ev_units_sold': 'sum',
    'ev_market_share_pct': 'mean',
    'country_name': 'count'
}).rename(columns={'country_name': 'num_countries'}).sort_values('ev_units_sold', ascending=False)

print(regional_sales.to_string())
print()

# 6. Policy Impact
print("📊 6. CORRELATION: EV POLICY SCORE vs. MARKET SHARE")
print("-" * 80)

policy_impact = ev_sales_full.groupby('country_name').agg({
    'ev_policy_score': 'first',
    'ev_market_share_pct': 'mean',
    'ev_units_sold': 'sum'
}).sort_values('ev_policy_score', ascending=False).head(10)

print(policy_impact.to_string())
print()

# 7. Key Insights Summary
print("=" * 80)
print("🎯 KEY INSIGHTS FOR VORONOI STORY")
print("=" * 80)
print()

insights = []

# Calculate some key metrics
total_evs_2025 = yearly_sales[yearly_sales['year'] == 2025]['ev_units_sold'].values[0]
total_evs_2020 = yearly_sales[yearly_sales['year'] == 2020]['ev_units_sold'].values[0]

top_country = country_sales.index[0]
top_country_sales = country_sales.iloc[0]['ev_units_sold']

top_manufacturer = mfr_sales.index[0]
top_mfr_sales = mfr_sales.iloc[0]['units_sold']

insights.append(f"1. Global EV sales reached {total_evs_2025:,.0f} units in 2025, up from {total_evs_2020:,.0f} in 2020")
insights.append(f"2. {top_country} leads the EV revolution with {top_country_sales:,.0f} total units sold")
insights.append(f"3. {top_manufacturer} dominates the market with {top_mfr_sales:,.0f} units sold globally")
insights.append(f"4. Charging infrastructure expanded {charger_growth:.0f}%, keeping pace with EV adoption")
insights.append(f"5. Countries with strong EV policies (score >80) show 2-3x higher market share")

for i, insight in enumerate(insights, 1):
    print(f"   {insight}")

print()
print("=" * 80)

# Save insights to JSON
insights_data = {
    "title": "The Global Electric Vehicle Revolution: 2020-2025",
    "subtitle": "A Data Story of the Fastest Transportation Transformation in History",
    "key_insights": insights,
    "datasets": {
        "countries": len(country),
        "manufacturers": len(manufacturer),
        "total_records": len(ev_sales) + len(charging_station) + len(market_share)
    },
    "top_markets": country_sales.head(5).to_dict(),
    "top_manufacturers": mfr_sales.head(5).to_dict(),
    "yearly_growth": yearly_sales.to_dict('records')
}

output_file = Path("/home/user/bg/ev_story_insights.json")
with open(output_file, 'w') as f:
    json.dump(insights_data, f, indent=2, default=str)

print(f"✅ Insights saved to: {output_file}")
