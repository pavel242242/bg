#!/usr/bin/env python3
"""
Flourish API Example - Programmatic Chart Creation

PREREQUISITES:
1. Flourish Business/Enterprise account with API access
2. API key from https://app.flourish.studio/settings
3. flourishcharts package: pip install flourishcharts

SETUP:
export FLOURISH_API_KEY="your_key_here"

This script demonstrates creating visualizations programmatically.
For most users, the simple CSV upload approach (export_to_flourish.py) is recommended.
"""

import os
import sys
from pathlib import Path

# Check for API key
if not os.getenv("FLOURISH_API_KEY"):
    print("❌ Error: FLOURISH_API_KEY environment variable not set")
    print()
    print("To use the Flourish API:")
    print("  1. Get API key from https://app.flourish.studio/settings")
    print("  2. export FLOURISH_API_KEY='your_key_here'")
    print("  3. Run this script again")
    print()
    print("Alternative: Use the simple CSV export approach instead")
    print("  python3 export_to_flourish.py")
    print("  Then upload CSVs to Flourish Studio UI (free tier works)")
    sys.exit(1)

# Check for flourishcharts package
try:
    from flourishcharts import Flourish
except ImportError:
    print("❌ Error: flourishcharts package not installed")
    print()
    print("Install with:")
    print("  pip install flourishcharts")
    print()
    sys.exit(1)

import pandas as pd

print("=" * 80)
print("FLOURISH API - PROGRAMMATIC CHART CREATION")
print("=" * 80)
print()

# Initialize Flourish
flourish = Flourish()

# Load exported data
exports_dir = Path("/home/user/bg/flourish_exports")

# ============================================================================
# Example 1: Line Chart - Global EV Growth
# ============================================================================
print("📊 Creating Line Chart: Global EV Growth...")

df = pd.read_csv(exports_dir / "yearly_summary.csv")

try:
    # Note: Actual API syntax may vary - check flourishcharts documentation
    # This is a conceptual example based on common patterns

    chart1 = flourish.create_chart(
        chart_type="line_chart",
        data=df,
        title="Global EV Sales Growth 2020-2025",
        subtitle="The exponential rise of electric vehicles",
        x_column="year",
        y_columns=["Total EV Sales"],
        credits="Data: EV Revolution Dataset (synthetic)"
    )

    # Publish and get URL
    chart1.publish()
    print(f"   ✓ Created: {chart1.url}")
    print()

except Exception as e:
    print(f"   ⚠️  API call failed: {e}")
    print("   Note: Syntax may vary - check flourishcharts docs")
    print()

# ============================================================================
# Example 2: Bar Chart Race - Manufacturer Battle
# ============================================================================
print("📊 Creating Bar Chart Race: Manufacturer Rankings...")

df = pd.read_csv(exports_dir / "manufacturer_monthly.csv")

try:
    chart2 = flourish.create_chart(
        chart_type="bar_chart_race",
        data=df,
        title="EV Manufacturer Battle 2020-2025",
        subtitle="Legacy automakers vs. pure EV players",
        date_column="Date",
        category_column="Manufacturer",
        value_column="Units Sold",
        color_column="HQ"
    )

    chart2.publish()
    print(f"   ✓ Created: {chart2.url}")
    print()

except Exception as e:
    print(f"   ⚠️  API call failed: {e}")
    print()

# ============================================================================
# Example 3: Scatter Plot - Policy Impact
# ============================================================================
print("📊 Creating Scatter Plot: Policy vs. Adoption...")

df = pd.read_csv(exports_dir / "policy_vs_adoption.csv")

try:
    chart3 = flourish.create_chart(
        chart_type="scatter",
        data=df,
        title="EV Policy Impact Analysis",
        subtitle="Does strong policy drive adoption?",
        x_column="Policy Score",
        y_column="Market Share %",
        size_column="Total EV Sales",
        color_column="Region",
        labels_column="Country"
    )

    chart3.publish()
    print(f"   ✓ Created: {chart3.url}")
    print()

except Exception as e:
    print(f"   ⚠️  API call failed: {e}")
    print()

# ============================================================================
# Summary
# ============================================================================
print("=" * 80)
print("API EXAMPLE COMPLETE")
print("=" * 80)
print()
print("Note: This is a conceptual example. Actual flourishcharts syntax may differ.")
print()
print("For documentation:")
print("  • https://developers.flourish.studio/api")
print("  • https://www.canva.dev/opensource/flourish-charts/")
print()
print("For most users, we recommend:")
print("  1. Run: python3 export_to_flourish.py")
print("  2. Upload CSVs to Flourish Studio UI")
print("  3. Create charts through web interface (easier & free)")
print()
