# Publishing AI Jobs Data to Flourish Studio
## Step-by-Step Guide

---

## Quick Start (5 Visualizations in 15 Minutes)

All CSV files are ready in `ai_jobs_flourish/`. Follow this guide to create publication-ready visualizations.

---

## Prerequisites

1. **Flourish Account:** Go to https://flourish.studio and create a free account
2. **Files Ready:** All CSVs are in `ai_jobs_flourish/` directory

---

## Visualization 1: Racing Bar Chart - Role Displacement Over Time

**Impact:** Shows which roles got decimated quarter-by-quarter

### Steps
1. Go to https://flourish.studio
2. Click **"New visualization"**
3. Search for **"Bar chart race"** template
4. Click **"Data"** tab
5. Click **"Upload data"** → Select `quarterly_by_role.csv`

### Configuration
- **Data bindings:**
  - Label: `Role`
  - Values: `Jobs Displaced`
  - Time: `Quarter`
- **Chart settings:**
  - Number of bars to show: `10`
  - Animation duration: `0.5` seconds per frame
  - Color by: `Role` (Flourish will auto-assign colors)
- **Title:** "The AI Job Displacement Race: Which Roles Lost Most (2020-2025)"
- **Subtitle:** "Quarterly job losses by role - QA Testers and Junior Analysts decimated"

### Publish
- Click **"Preview"** to see animation
- Click **"Publish"** → Get shareable link
- **Embed:** Use iframe code for websites

**Expected result:** Animated bar chart showing QA Testers, Junior Analysts, and Transcriptionists racing to the top (most displaced)

---

## Visualization 2: Line Chart - The Productivity-Wage Paradox

**Impact:** Shows productivity up 3x, wages down 12% - who captured the value?

### Steps
1. New visualization → **"Line chart"**
2. Upload `yearly_trend.csv`

### Configuration
- **Data bindings:**
  - X-axis: `Year`
  - Y-axis (primary): `Jobs Displaced`, `Jobs Created (AI-Adjacent)`
  - Y-axis (secondary): `Productivity Multiplier`, `Wage Suppression %`
- **Chart settings:**
  - Line style: Smooth curves
  - Show data points: Yes
  - Grid lines: Yes (horizontal only)
- **Colors:**
  - Jobs Displaced: Red (#E74C3C)
  - Jobs Created: Green (#27AE60)
  - Productivity Multiplier: Blue (#3498DB)
  - Wage Suppression: Orange (#E67E22)
- **Title:** "The Productivity-Wage Paradox"
- **Subtitle:** "Productivity tripled, wages dropped 12% - workers didn't capture the gains"
- **Footer:** "Source: AI Job Displacement Analysis 2020-2025"

**Expected result:** Dual-axis line chart showing the divergence between productivity gains and wage suppression

---

## Visualization 3: Horizontal Bar Chart - Top Vulnerable Roles

**Impact:** Clear ranking of which jobs are most at risk

### Steps
1. New visualization → **"Bar chart"** (horizontal)
2. Upload `top_roles.csv`

### Configuration
- **Data bindings:**
  - Category: `Role`
  - Value: `Total Jobs Displaced`
  - Color by: `Wage Suppression %` (optional - shows severity gradient)
- **Chart settings:**
  - Sort: Descending (highest displacement first)
  - Show values: Yes
  - Number format: Comma separator (491,880)
- **Title:** "Most Vulnerable Roles: AI Job Displacement 2020-2025"
- **Subtitle:** "Total jobs lost by role - nearly 500K QA Testers displaced"
- **Annotations:**
  - Add note on QA Tester bar: "7.4x replacement rate"

**Expected result:** Clean horizontal bars showing QA Testers at ~492K displaced, followed by Junior Analysts at ~304K

---

## Visualization 4: Scatter Plot - AI Spend vs Job Displacement

**Impact:** More AI investment = more job loss (data proves it)

### Steps
1. New visualization → **"Scatter plot"**
2. Upload `ai_adoption_correlation.csv`

### Configuration
- **Data bindings:**
  - X-axis: `AI Spend per Employee (USD)`
  - Y-axis: `Jobs Displaced`
  - Size: `Net Job Loss`
  - Color: Use gradient by `AI Adoption %`
  - Label: `Year`
- **Chart settings:**
  - Show trend line: Yes (linear regression)
  - Point size range: Medium (10-50 pixels)
  - Show labels: Yes
- **Title:** "AI Investment Drives Job Displacement"
- **Subtitle:** "Companies spending $3-4K per employee on AI saw highest job losses"
- **Axes labels:**
  - X: "AI Spend per Employee (USD/year)"
  - Y: "Total Jobs Displaced"

**Expected result:** Positive correlation scatter plot - higher AI spend correlates with more displacement

---

## Visualization 5: Treemap - Industry Breakdown

**Impact:** Shows which industries got hit hardest

### Steps
1. New visualization → **"Hierarchy"** → Select "Treemap"
2. Upload `industry_impact.csv`

### Configuration
- **Data bindings:**
  - Label: `Industry`
  - Size: `Jobs Displaced`
  - Color: `Vulnerability Score` (gradient: low vulnerability = green, high = red)
- **Chart settings:**
  - Show values: Yes
  - Show percentages: Yes
  - Color scheme: Red-Yellow-Green (reversed - red for high vulnerability)
- **Title:** "AI Job Displacement by Industry"
- **Subtitle:** "E-commerce, Creative & Media, Healthcare hit hardest"

**Expected result:** Treemap with E-commerce taking ~25% of space (largest), colored by vulnerability

---

## Bonus: Multi-Slide Story (Advanced)

Combine all visualizations into a narrative story:

### Steps
1. New visualization → **"Story"** template
2. Add slides:
   - **Slide 1:** "The Scale" - Line chart (yearly trend)
   - **Slide 2:** "The Roles" - Racing bar chart (quarterly by role)
   - **Slide 3:** "The Industries" - Treemap (industry impact)
   - **Slide 4:** "The Paradox" - Dual-axis line (productivity vs wages)
   - **Slide 5:** "The Correlation" - Scatter plot (AI spend vs displacement)

### Narrative Flow
```
Slide 1: "2.3 million digital jobs lost to AI (2020-2025)"
         → Show yearly trend, highlight 85% net loss

Slide 2: "Some roles were decimated"
         → Animate role displacement race
         → Pause on QA Testers (492K lost)

Slide 3: "Industries transformed overnight"
         → Show treemap
         → Highlight E-commerce (522K displaced)

Slide 4: "Productivity up. Wages down. Who won?"
         → Show paradox lines
         → Annotation: "3x productivity, -12% wages"

Slide 5: "More AI spending = More job losses"
         → Show scatter plot
         → End with: "The data doesn't lie"
```

### Publish Story
- Publish as interactive story
- Share link on social media, LinkedIn, Twitter
- Embed in blog posts or Medium articles

---

## Publishing Checklist

Before publishing each visualization:

✅ **Data accuracy:**
- [ ] Check data loaded correctly
- [ ] Verify numbers match analysis (e.g., total displaced = 2.3M)
- [ ] Ensure dates/quarters display properly

✅ **Design:**
- [ ] Title is clear and compelling
- [ ] Subtitle provides context
- [ ] Colors are meaningful (not random)
- [ ] Text is readable (font size ≥12px)

✅ **Attribution:**
- [ ] Add footer: "Source: AI Job Displacement Analysis 2020-2025 | Data: Synthetic (datagen)"
- [ ] Include your name/organization if applicable

✅ **Settings:**
- [ ] Mobile-responsive (preview on phone)
- [ ] Animations are smooth (not too fast/slow)
- [ ] Tooltips show relevant info on hover

---

## Sharing Your Visualizations

Once published, each viz gets a unique URL like:
```
https://public.flourish.studio/visualisation/[ID]/
```

### Share Options
1. **Direct link:** Copy URL, share anywhere
2. **Embed code:** Get iframe, embed in websites
3. **Social media:** Flourish auto-generates preview images
4. **Export:** Download as PNG/SVG (paid plans only)

### Recommended Platforms
- **Twitter/X:** Share with hashtags #DataViz #AI #Jobs #Automation
- **LinkedIn:** Post with professional commentary
- **Medium/Substack:** Embed in articles
- **GitHub:** Add to README with screenshots
- **Reddit:** r/dataisbeautiful, r/artificial, r/economics

---

## Tips for Maximum Impact

### 1. Lead with the Shocking Number
> "2.3 million digital jobs lost to AI. Only 350K created. Here's the data:"

### 2. Use the "15% Myth" Hook
> "They said AI creates more jobs than it destroys. The data says otherwise:"

### 3. Highlight the Paradox
> "Productivity up 3x. Wages down 12%. Who captured the value? Not the workers."

### 4. Make it Personal
> "Check if your role is on this list. QA Testers: 492K jobs lost. Junior Analysts: 304K."

### 5. Show the Acceleration
> "Racing bar chart: Watch QA testing jobs vanish quarter by quarter."

---

## Sample Social Media Post

```
🚨 The AI Job Displacement Crisis: What the Data Shows

2.3M digital jobs displaced (2020-2025)
Only 350K AI-adjacent jobs created (15% replacement rate)
85% net loss

Most vulnerable roles:
• QA Testers: 492K lost (7.4x replacement rate)
• Junior Analysts: 304K lost
• Transcriptionists: 259K lost

The paradox: Productivity ↑3x, Wages ↓12%

Interactive charts: [Flourish link]
Full analysis: [GitHub link]

#DataViz #AI #Automation #FutureOfWork
```

---

## Troubleshooting

### CSV Upload Issues
**Problem:** "Invalid date format"
**Solution:** Flourish expects YYYY-MM-DD or ISO8601. Our CSVs already use this format.

**Problem:** "Column not found"
**Solution:** Check exact column names (case-sensitive). Our CSVs use human-readable names like "Jobs Displaced" not "jobs_displaced"

### Visualization Not Showing Data
**Problem:** Bars/lines not appearing
**Solution:**
1. Check data bindings (map columns correctly)
2. Verify data type (numbers vs strings)
3. Preview data in Flourish's data tab

### Animation Too Fast/Slow
**Problem:** Bar chart race is too fast
**Solution:** Adjust "Duration per section" in settings (recommend 0.5-1.0 seconds)

---

## Alternative: Programmatic Publishing (API)

If you have a Flourish Business/Enterprise account with API access:

```bash
# Install flourishcharts
pip install flourishcharts

# Set API key
export FLOURISH_API_KEY="your_key"

# Run the API example (requires API key)
python3 flourish_api_example.py
```

See `FLOURISH_INTEGRATION_GUIDE.md` for API details.

**Note:** Free tier doesn't have API access. Manual upload (this guide) works perfectly.

---

## Files Reference

| File | Best For | Rows | Use Case |
|------|----------|------|----------|
| `yearly_trend.csv` | Line charts | 6 | Overall trends 2020-2025 |
| `top_roles.csv` | Bar charts | 16 | Most vulnerable roles |
| `industry_impact.csv` | Treemap, bars | 12 | Industry breakdown |
| `regional_impact.csv` | Maps, bars | 15 | Geographic analysis |
| `quarterly_by_role.csv` | Racing bars | 240 | Time series by role |
| `quarterly_by_industry.csv` | Racing bars | 179 | Time series by industry |
| `ai_adoption_correlation.csv` | Scatter plots | 6 | AI spend vs displacement |
| `replacement_rates.csv` | Scatter, bars | 13 | AI replacement analysis |

---

## Next Steps

1. **Create 1-2 key visualizations** (start with racing bar chart)
2. **Get feedback** (share with colleagues, friends)
3. **Iterate** (adjust colors, titles, annotations)
4. **Publish widely** (social media, blog, GitHub)
5. **Track engagement** (Flourish shows view counts)

---

## Support

**Flourish Help:**
- Help center: https://help.flourish.studio
- Templates: https://flourish.studio/visualisations
- Community: Twitter @f_l_o_u_r_i_s_h

**This Analysis:**
- Full guide: `AI_JOBS_README.md`
- Data queries: `ai_jobs_displacement.duckdb`
- Raw data: `ai_jobs_data/`

---

**Time to first published visualization: < 10 minutes**

**Start here:** https://flourish.studio → New visualization → Bar chart race → Upload `quarterly_by_role.csv`

**Let the data tell the story.** 📊
