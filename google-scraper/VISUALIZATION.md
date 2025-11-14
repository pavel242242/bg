# Data Journalism Visualization

## "What People Hate" - Interactive Data Story

A beautiful, interactive HTML visualization exploring Google autocomplete suggestions for "I hate" queries.

## Features

- **Interactive Letter Navigation**: Click any letter (A-Z) to see what people hate starting with that letter
- **Word Clouds**: Dynamic word clouds generated from suggestion data
- **Top 10 Lists**: Ranked list of autocomplete suggestions for each letter
- **Statistics Dashboard**: Overview of total suggestions, queries analyzed, and unique concepts
- **Responsive Design**: Works beautifully on desktop, tablet, and mobile
- **Data Journalism Aesthetic**: Clean, modern design inspired by NYT/Guardian data visualizations

## Technology Stack

- **HTML5/CSS3**: Modern, responsive layout
- **D3.js v7**: Data visualization and word cloud generation
- **Vanilla JavaScript**: No framework dependencies
- **Static Site**: No backend required

## Usage

### Option 1: Local File
Simply open `index.html` in a web browser.

### Option 2: HTTP Server (Recommended)
```bash
# Start server
python -m http.server 8000

# Open in browser
http://localhost:8000/index.html
```

### Option 3: Deploy to Static Hosting
Upload these files to any static hosting service:
- `index.html`
- `data.json`

**Hosting options:**
- GitHub Pages
- Netlify
- Vercel
- AWS S3 + CloudFront
- Cloudflare Pages

## Data Export

To update the data from Keboola:

```bash
python export_data.py
```

This will fetch the latest data from Keboola Storage and generate `data.json`.

## File Structure

```
google-scraper/
├── index.html          # Main visualization page
├── data.json           # Exported data from Keboola
├── export_data.py      # Script to export data from Keboola
└── VISUALIZATION.md    # This file
```

## Customization

### Change Color Scheme
Edit the CSS gradient in `index.html`:
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

### Adjust Word Cloud
Modify the D3.js word cloud parameters:
```javascript
.size([width, height])
.padding(5)
.rotate(() => (~~(Math.random() * 2) * 90))
.fontSize(d => d.size)
```

### Update Insights
Edit the insights section in the HTML:
```html
<div class="insight-card">
    <h3>Your Title</h3>
    <p>Your insight text</p>
</div>
```

## Browser Support

- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support
- Mobile browsers: ✅ Responsive design

## License

MIT
