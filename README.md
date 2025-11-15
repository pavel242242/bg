# Apify Data Collector with Claude Agent SDK

A powerful Apify actor that collects run data from all your actors and exports it via Claude Agent SDK, with a web UI for easy control.

## Features

- **📊 Data Collection**: Fetches runs from all actors in your Apify account
- **🤖 Claude Agent SDK Integration**: Exports data using Anthropic's Claude for processing
- **🌐 Web UI Control**: Easy-to-use dashboard for managing data collection
- **🔗 Public Access**: Expose UI via bore.pub or Cloudflare tunnel
- **🖥️ Local Browser Integration**: Auto-open browser with xli
- **🔐 Secure Authentication**: Token-based auth for web UI

## Setup

### Prerequisites

1. **Apify Account**: Get your API token from [Apify Console](https://console.apify.com/account/integrations)
2. **Anthropic API Key**: Get from [Anthropic Console](https://console.anthropic.com/)
3. **xli** (optional, for local browser opening): Install from [xli](https://github.com/your-xli-link)

### Environment Variables

Configure these in the Apify Console or `.env` file:

```bash
APIFY_TOKEN=your_apify_token_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
WEB_UI_AUTH_TOKEN=your_custom_auth_token  # Optional, defaults to 'default-token'
```

### Installation

#### Option 1: Deploy to Apify

1. Push this actor to your Apify account:
```bash
apify login
apify push
```

2. Configure environment variables in the Apify Console
3. Run the actor

#### Option 2: Run Locally

1. Install dependencies:
```bash
npm install
```

2. Create `.env` file with required variables:
```bash
APIFY_TOKEN=your_token
ANTHROPIC_API_KEY=your_key
WEB_UI_AUTH_TOKEN=my-secret-token
```

3. Run:
```bash
npm start
```

## Usage

### Input Configuration

```json
{
  "tunnelMethod": "bore",      // "bore" or "cloudflare"
  "webUiPort": 3000,           // Port for web UI
  "autoExport": false,         // Auto-export on startup
  "openBrowser": true          // Open browser with xli
}
```

### Web UI

Once the actor starts, you'll see:

```
✅ Web UI listening on port 3000
🔗 Local URL: http://localhost:3000
✅ Public URL: http://bore.pub:12345
```

#### Accessing the UI

**Local access:**
```
http://localhost:3000?auth=your-auth-token
```

**Public access (via tunnel):**
```
http://bore.pub:12345?auth=your-auth-token
```

#### UI Features

- **Start Collection**: Begin fetching actor runs
- **Stop Collection**: Pause data collection
- **Export via Claude Agent**: Send data to Claude for processing
- **Auto-refresh**: Status updates every 5 seconds

### API Endpoints

All endpoints require authentication via `Authorization: Bearer <token>` header or `?auth=<token>` query param.

#### `GET /api/status`
Get current status and collected runs.

**Response:**
```json
{
  "active": true,
  "runCount": 150,
  "runs": [...],
  "serverUrl": "http://bore.pub:12345"
}
```

#### `POST /api/start`
Start data collection.

#### `POST /api/stop`
Stop data collection.

#### `POST /api/export`
Export collected data via Claude Agent SDK.

**Response:**
```json
{
  "success": true,
  "exportedAt": "2025-11-15T10:30:00.000Z",
  "recordCount": 150,
  "claudeResponse": "Data processed successfully..."
}
```

## xli Integration

The actor automatically outputs the server URL and port to logs in a format that xli can parse:

```
🔗 Local URL: http://localhost:3000
✅ Public URL: http://bore.pub:12345
```

### Using xli to Auto-Open

If `openBrowser: true` is set in input, the actor will automatically call:

```bash
xli open "http://bore.pub:12345?auth=your-token"
```

This opens your default browser with the authenticated URL.

### Manual xli Usage

You can also use xli manually by parsing the logs:

```bash
# Get the URL from actor logs
apify log

# Parse and open with xli
xli open "$(grep 'Public URL:' actor-log.txt | awk '{print $4}')?auth=your-token"
```

## Tunnel Options

### Bore.pub (Default)

Simple, no configuration needed:
- Automatically generates public URL
- No account required
- Port is randomly assigned

### Cloudflare Tunnel

More stable, custom domains possible:
- Requires cloudflared installed in Docker image
- Free Cloudflare account
- Better performance for production

Set `tunnelMethod: "cloudflare"` in input to use.

## Data Export with Claude

The actor uses Claude Agent SDK to process and export data. The exported data includes:

```json
{
  "timestamp": "2025-11-15T10:30:00Z",
  "totalRuns": 150,
  "runs": [...],
  "summary": {
    "byStatus": {
      "SUCCEEDED": 120,
      "FAILED": 20,
      "RUNNING": 10
    },
    "byActor": {
      "web-scraper": 50,
      "data-processor": 100
    }
  }
}
```

Claude processes this data and can:
- Analyze patterns and anomalies
- Generate insights and reports
- Transform data for downstream systems
- Trigger alerts based on conditions

## Development

### Project Structure

```
.
├── .actor/
│   ├── actor.json              # Actor configuration
│   └── input_schema.json       # Input schema
├── src/
│   └── main.js                 # Main actor code
├── Dockerfile                  # Docker configuration
├── package.json               # Dependencies
└── README.md                  # This file
```

### Local Development

```bash
# Install dependencies
npm install

# Run locally
npm start

# Test endpoints
curl -H "Authorization: Bearer your-token" http://localhost:3000/api/status
```

## Troubleshooting

### Tunnel Not Starting

**Issue**: Tunnel fails to start
**Solution**:
- Check if bore/cloudflared is installed
- Verify network connectivity
- Try alternative tunnel method

### Authentication Errors

**Issue**: 401 Unauthorized
**Solution**:
- Verify WEB_UI_AUTH_TOKEN is set correctly
- Include token in request: `?auth=your-token` or header `Authorization: Bearer your-token`

### No Data Collected

**Issue**: Zero runs collected
**Solution**:
- Verify APIFY_TOKEN has correct permissions
- Check if actors exist in your account
- Review logs for API errors

### Claude Export Fails

**Issue**: Export endpoint returns error
**Solution**:
- Verify ANTHROPIC_API_KEY is valid
- Check API quota/limits
- Ensure data is collected before export

## License

MIT

## Support

For issues and questions:
- GitHub Issues: [Create an issue](https://github.com/your-repo/issues)
- Apify Forum: [forum.apify.com](https://forum.apify.com)

## Version History

**1.0.0** (2025-11-15)
- Initial release
- Actor runs collection
- Claude Agent SDK integration
- Web UI with bore.pub/Cloudflare support
- xli integration for local browser opening
