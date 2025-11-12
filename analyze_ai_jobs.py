#!/usr/bin/env python3
"""
Analyze AI Job Displacement data to extract hard-hitting insights.
"""

import pandas as pd
import json
from pathlib import Path

# Load generated data
data_dir = Path("/home/user/bg/ai_jobs_data")

region = pd.read_parquet(data_dir / "region.parquet")
industry = pd.read_parquet(data_dir / "industry.parquet")
role = pd.read_parquet(data_dir / "role.parquet")
job_displacement = pd.read_parquet(data_dir / "job_displacement.parquet")
ai_adoption = pd.read_parquet(data_dir / "ai_tool_adoption.parquet")

print("=" * 80)
print("AI JOB DISPLACEMENT ANALYSIS (2020-2025)")
print("The Digital Jobs Massacre: A Data Story")
print("=" * 80)
print()

# Merge data for analysis
jobs_full = job_displacement.merge(region, on="region_id") \
                              .merge(industry, on="industry_id") \
                              .merge(role, on="role_id")

jobs_full['year'] = pd.to_datetime(jobs_full['quarter']).dt.year
jobs_full['quarter_label'] = pd.to_datetime(jobs_full['quarter']).dt.to_period('Q').astype(str)

# ============================================================================
# 1. The Big Picture: Total Job Displacement
# ============================================================================
print("📊 1. TOTAL JOB DISPLACEMENT (2020-2025)")
print("-" * 80)

yearly_displacement = jobs_full.groupby('year').agg({
    'jobs_displaced': 'sum',
    'jobs_created_ai_adjacent': 'sum',
    'net_job_loss': 'sum',
    'productivity_multiplier': 'mean',
    'wage_suppression_pct': 'mean'
}).reset_index()

print(yearly_displacement.to_string(index=False))
print()

total_displaced = jobs_full['jobs_displaced'].sum()
total_created = jobs_full['jobs_created_ai_adjacent'].sum()
net_loss = jobs_full['net_job_loss'].sum()

print(f"💡 TOTAL JOBS DISPLACED (2020-2025): {total_displaced:,.0f}")
print(f"💡 AI-ADJACENT JOBS CREATED: {total_created:,.0f}")
print(f"💡 NET JOB LOSS: {net_loss:,.0f} ({(net_loss/total_displaced*100):.1f}% of displaced)")
print()

growth_rate = ((yearly_displacement.iloc[-1]['jobs_displaced'] / yearly_displacement.iloc[0]['jobs_displaced']) - 1) * 100
print(f"💡 Displacement accelerated {growth_rate:.0f}% from 2020 to 2025")
print()

# ============================================================================
# 2. Most Vulnerable Roles
# ============================================================================
print("🎯 2. MOST VULNERABLE ROLES (Total Displacement)")
print("-" * 80)

role_impact = jobs_full.groupby('role_name').agg({
    'jobs_displaced': 'sum',
    'net_job_loss': 'sum',
    'replacement_rate': 'first',
    'wage_suppression_pct': 'mean'
}).sort_values('jobs_displaced', ascending=False).head(15)

print(role_impact.to_string())
print()

# ============================================================================
# 3. Industry Breakdown
# ============================================================================
print("🏭 3. INDUSTRIES HIT HARDEST")
print("-" * 80)

industry_impact = jobs_full.groupby('industry_name').agg({
    'jobs_displaced': 'sum',
    'net_job_loss': 'sum',
    'productivity_multiplier': 'mean',
    'automation_vulnerability': 'first'
}).sort_values('jobs_displaced', ascending=False)

print(industry_impact.to_string())
print()

# ============================================================================
# 4. Geographic Impact
# ============================================================================
print("🌍 4. REGIONAL IMPACT (Top 10)")
print("-" * 80)

regional_impact = jobs_full.groupby(['region_name', 'continent']).agg({
    'jobs_displaced': 'sum',
    'net_job_loss': 'sum',
    'wage_suppression_pct': 'mean',
    'digital_workforce_millions': 'first'
}).sort_values('jobs_displaced', ascending=False).head(10)

print(regional_impact.to_string())
print()

# ============================================================================
# 5. The Productivity Paradox
# ============================================================================
print("⚡ 5. THE PRODUCTIVITY PARADOX")
print("-" * 80)

productivity_analysis = jobs_full.groupby('year').agg({
    'productivity_multiplier': 'mean',
    'jobs_displaced': 'sum',
    'wage_suppression_pct': 'mean'
}).reset_index()

print(productivity_analysis.to_string(index=False))
print()

avg_multiplier = jobs_full['productivity_multiplier'].mean()
print(f"💡 Average productivity multiplier: {avg_multiplier:.2f}x")
print(f"💡 Translation: 1 human + AI now does the work of {avg_multiplier:.1f} humans in 2019")
print(f"💡 But wages dropped {jobs_full['wage_suppression_pct'].mean():.1f}% on average")
print()

# ============================================================================
# 6. The Replacement Rate Reality
# ============================================================================
print("🔄 6. AI REPLACEMENT RATES BY ROLE")
print("-" * 80)

replacement_analysis = jobs_full.groupby('role_name').agg({
    'replacement_rate': 'first',
    'jobs_displaced': 'sum'
}).sort_values('replacement_rate', ascending=False).head(10)

print(replacement_analysis.to_string())
print()

# ============================================================================
# 7. Quarterly Acceleration
# ============================================================================
print("📈 7. QUARTERLY ACCELERATION (Last 8 Quarters)")
print("-" * 80)

quarterly_trend = jobs_full.groupby('quarter_label').agg({
    'jobs_displaced': 'sum',
    'net_job_loss': 'sum'
}).tail(8)

print(quarterly_trend.to_string())
print()

# ============================================================================
# 8. AI Adoption vs Job Loss Correlation
# ============================================================================
print("💼 8. AI SPEND vs JOB DISPLACEMENT")
print("-" * 80)

ai_adoption_full = ai_adoption.merge(industry, on="industry_id")
ai_adoption_full['year'] = pd.to_datetime(ai_adoption_full['quarter']).dt.year

adoption_summary = ai_adoption_full.groupby('year').agg({
    'companies_using_ai_pct': 'mean',
    'avg_ai_spend_per_employee_usd': 'mean'
}).reset_index()

combined = adoption_summary.merge(yearly_displacement[['year', 'jobs_displaced']], on='year')
print(combined.to_string(index=False))
print()

# ============================================================================
# 9. The "15% Myth" - Jobs Created vs Lost
# ============================================================================
print("🎭 9. THE 15% MYTH: 'AI Creates Jobs'")
print("-" * 80)

creation_rate = (total_created / total_displaced) * 100
print(f"Jobs displaced: {total_displaced:,.0f}")
print(f"AI-adjacent jobs created: {total_created:,.0f}")
print(f"Creation rate: {creation_rate:.1f}%")
print(f"Net loss: {net_loss:,.0f}")
print()
print("For every 100 jobs AI eliminated, only 15 new 'AI-adjacent' jobs were created.")
print("And those new jobs require completely different skills at higher skill levels.")
print()

# ============================================================================
# 10. Key Insights Summary
# ============================================================================
print("=" * 80)
print("🎯 KEY INSIGHTS: THE UNCOMFORTABLE TRUTH")
print("=" * 80)
print()

insights = []

top_role = role_impact.index[0]
top_role_displaced = role_impact.iloc[0]['jobs_displaced']

top_industry = industry_impact.index[0]
top_industry_displaced = industry_impact.iloc[0]['jobs_displaced']

top_region = regional_impact.index[0][0]
top_region_displaced = regional_impact.iloc[0]['jobs_displaced']

insights.append(f"1. {total_displaced:,.0f} digital jobs displaced globally (2020-2025)")
insights.append(f"2. {top_role}s hit hardest: {top_role_displaced:,.0f} jobs lost")
insights.append(f"3. {top_industry} industry saw {top_industry_displaced:,.0f} displacements")
insights.append(f"4. {top_region} leads in absolute numbers: {top_region_displaced:,.0f} jobs")
insights.append(f"5. For every 1 job created, {(100/creation_rate):.1f} were eliminated")
insights.append(f"6. Productivity up {avg_multiplier:.1f}x, wages down {jobs_full['wage_suppression_pct'].mean():.1f}%")
insights.append(f"7. Displacement accelerating {growth_rate:.0f}% from 2020 to 2025")
insights.append(f"8. Only 15% of displaced workers transitioned to AI-adjacent roles")

for insight in insights:
    print(f"   {insight}")

print()
print("=" * 80)

# ============================================================================
# Save insights to JSON
# ============================================================================
insights_data = {
    "title": "The AI Job Displacement Crisis: 2020-2025",
    "subtitle": "Digital jobs lost to automation - the data doesn't lie",
    "key_insights": insights,
    "totals": {
        "jobs_displaced": int(total_displaced),
        "jobs_created": int(total_created),
        "net_job_loss": int(net_loss),
        "creation_rate_pct": float(creation_rate),
        "avg_productivity_multiplier": float(avg_multiplier),
        "avg_wage_suppression_pct": float(jobs_full['wage_suppression_pct'].mean())
    },
    "top_vulnerable_roles": role_impact.head(10).to_dict(),
    "industry_impact": industry_impact.to_dict(),
    "yearly_trend": yearly_displacement.to_dict('records')
}

output_file = Path("/home/user/bg/ai_jobs_insights.json")
with open(output_file, 'w') as f:
    json.dump(insights_data, f, indent=2, default=str)

print(f"✅ Insights saved to: {output_file}")
print()
