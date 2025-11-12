# Voronoi AI Replacement Infographic

An interactive data journalism infographic that visualizes how AI agents are replacing various professions using Voronoi diagrams.

## Overview

This project creates a satirical yet informative visualization showing the automation risk across different professions. Using Voronoi tessellation, each profession occupies a region of the map, with colors indicating the level of AI replacement.

## Features

- **Interactive Voronoi Diagram**: Each profession is represented by a Voronoi cell
- **Color-Coded Risk Levels**: From red (high replacement) to blue (not yet replaced)
- **Interactive Tooltips**: Hover over any profession to see detailed replacement statistics
- **Professional Design**: Clean, data journalism-style aesthetic
- **Responsive Layout**: Works on desktop and mobile devices
- **Animated Transitions**: Smooth animations on page load

## Professions Tracked

### High Risk (75-100%)
- Programmers (85%)
- Email Readers (90%)
- Designers (80%)
- Agile Coaches (75%)

### Medium-High Risk (50-75%)
- Movie Makers (65%)
- Content Writers (70%)
- Data Analysts (68%)

### Medium Risk (25-50%)
- Customer Service Reps (45%)
- Talkative Grooming Attendees (40%)
- Social Media Managers (48%)
- Translators (42%)

### Low Risk (10-25%)
- HR Managers (20%)
- Therapists (15%)
- Sales Executives (22%)

### Minimal Risk (0-10%)
- Plumbers (5%)
- Electricians (6%)

### Not Yet Replaced
- **Lumber Jacks** (2%)
- **Teachers** (3%)
- Nurses (4%)
- Construction Workers (3%)

## Usage

### Local Development

Simply open `index.html` in a web browser:

```bash
# Using Python
python3 -m http.server 8000

# Or using Node.js
npx http-server

# Then visit http://localhost:8000
```

### File Structure

```
voronoi-app/
├── index.html      # Main HTML structure
├── styles.css      # Professional styling
├── app.js          # D3.js visualization logic
└── README.md       # This file
```

## Technology Stack

- **D3.js v7**: For Voronoi diagram generation and data visualization
- **HTML5**: Structure and semantic markup
- **CSS3**: Styling with gradients, animations, and responsive design
- **Vanilla JavaScript**: Interactive behavior and data management

## Customization

### Adding New Professions

Edit the `professions` array in `app.js`:

```javascript
const professions = [
    { name: "Your Profession", replacement: 50, x: 400, y: 400 },
    // ...
];
```

### Adjusting Color Scheme

Modify the `getColor()` function in `app.js`:

```javascript
function getColor(replacement) {
    if (replacement >= 75) return "#d73027"; // High - Red
    // ... adjust colors as needed
}
```

### Changing Layout

Adjust the visualization dimensions:

```javascript
const width = 900;   // SVG width
const height = 900;  // SVG height
```

## Data Sources

This is a satirical infographic created for demonstration purposes. The replacement percentages are synthesized estimates based on:
- Industry reports on AI adoption
- Labor market analysis
- Technology capability assessments
- Educated speculation

**Note**: This should not be used as actual career guidance!

## Key Insights

1. **White-collar vulnerability**: Technical and creative professions face highest replacement rates
2. **Communication automation**: Routine communication and facilitation roles are being automated
3. **Physical labor safety**: Jobs requiring physical presence remain relatively safe
4. **Human connection**: Roles requiring empathy and human relationships (teachers, nurses) are resilient

## Future Enhancements

- [ ] Add time-series animation showing replacement trends over years
- [ ] Include data source citations and methodology
- [ ] Add export functionality (PNG, SVG, PDF)
- [ ] Include search/filter functionality
- [ ] Add comparison mode for different industries
- [ ] Integrate real API data sources

## License

MIT License - Feel free to use and modify for your own projects!

## Credits

Created as part of the Voronoi AI Replacement Infographic project.

Built with ❤️ and D3.js
