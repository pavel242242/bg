# Voronoi Infographic: The Great AI Replacement

An interactive data journalism infographic visualizing how AI agents are replacing various professions across different industries.

## Overview

This experiment uses **Voronoi diagrams** to create a visually compelling representation of job displacement by AI. Each profession occupies a territory in the diagram, with:

- **Color coding** indicating replacement risk level
- **Territory size** weighted by number of workers affected
- **Interactive tooltips** providing detailed statistics
- **Satirical data journalism** narrative with fake statistics

## Features

- **D3.js Voronoi Diagram**: Dynamic spatial partitioning based on profession data
- **26 Professions**: From Programmers (87% replaced) to Lumberjacks (3% replaced)
- **Risk Categories**:
  - 🔴 **Critical Risk (80-95%)**: Programmers, Email Readers, Telemarketers, Agile Coaches, etc.
  - 🟠 **High Risk (60-79%)**: Movie Makers, Designers, Content Writers
  - 🟡 **Moderate Risk (40-59%)**: Music Composers, Pharmacists, Radiologists
  - 🟢 **Safe (0-39%)**: Teachers, Nurses, Lumberjacks, Electricians
- **Hover Interactions**: Detailed statistics on replacement rates, workers affected, and descriptions
- **Responsive Design**: Professional layout with header, statistics cards, and conclusion

## Data Highlights

The infographic includes satirical "fake data journalism" about:

- **23.4 million workers replaced** in the past 18 months
- **67% average replacement rate** across studied professions
- **892K AI agents** doing the work of 23.4M humans
- **2,627% productivity gain** per AI agent vs human

### Notable Findings

- **Talkative Grooming Attendees**: 89% replaced (meeting participants who spend hours discussing minutiae)
- **Email Readers**: 94% replaced (AI agents triage and respond to emails)
- **Agile Coaches**: 91% replaced (AI sprint planning and retrospectives)
- **Lumberjacks**: Only 3% replaced (complex forest terrain resists automation)
- **Teachers**: 28% replaced (human mentorship remains crucial)

## Usage

Simply open `index.html` in a web browser:

```bash
# Option 1: Direct file open
open experiments/voronoi-infographic/index.html

# Option 2: With a local server
cd experiments/voronoi-infographic
python3 -m http.server 8000
# Then visit http://localhost:8000
```

## Technical Details

- **Dependencies**: D3.js v7 (loaded from CDN)
- **File Size**: Single HTML file (~25 KB)
- **Browser Compatibility**: Modern browsers with SVG support
- **Data Format**: JavaScript array of profession objects with replacement rates and worker counts

## Disclaimer

All data in this infographic is completely fabricated for entertainment and demonstration purposes. This is a creative exercise in data visualization, not a real study.

## Future Enhancements

- Add animation showing replacement rates over time
- Export diagram as PNG/SVG
- Allow users to input custom professions and replacement rates
- Add filters to show/hide risk categories
- Create mobile-responsive version
