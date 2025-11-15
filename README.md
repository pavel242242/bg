# Claude + Keboola Data Agent

A minimal Apify actor that provides a conversational interface to Claude AI with Apify and Keboola Storage integration. Move data from anywhere to anywhere through natural language.

## Features

- **Claude AI Integration**: Powered by Claude Sonnet 4.5 via Claude Agent SDK
- **Apify Automation**: Design and orchestrate web scrapers, crawlers, and data workflows
- **Keboola Storage**: Read table samples, analyze data, and design ETL pipelines
- **Chat Interface**: Clean web UI for interactive conversations
- **Table Analysis**: Quick CSV sampling with `!table` command

## Architecture

```
┌─────────────┐
│   Browser   │ ←→ Chat Interface (HTML)
└─────────────┘
       ↓
┌─────────────────────────────────────┐
│  Apify Actor (HTTP Server)          │
│  ┌────────────────────────────────┐ │
│  │  Agent Orchestrator            │ │
│  │  - Claude Agent SDK            │ │
│  │  - System Prompt               │ │
│  │  - Response Handler            │ │
│  └────────────────────────────────┘ │
│  ┌────────────────────────────────┐ │
│  │  Keboola Helper                │ │
│  │  - Storage API Client          │ │
│  │  - Table Sampling              │ │
│  └────────────────────────────────┘ │
└─────────────────────────────────────┘
       ↓                    ↓
┌─────────────┐      ┌─────────────┐
│  Anthropic  │      │   Keboola   │
│     API     │      │   Storage   │
└─────────────┘      └─────────────┘
```

## Quick Start

### Prerequisites

- Python 3.11+
- [Apify CLI](https://docs.apify.com/cli/) (`npm install -g apify-cli`)
- [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/) (for local dev)
- Anthropic API key ([console.anthropic.com](https://console.anthropic.com))
- Keboola connection (optional, for table analysis)

### Local Development

1. **Clone and setup**
   ```bash
   git clone <repo-url>
   cd bg
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-..."
   export KBC_URL="https://connection.keboola.com"  # Optional
   export KBC_TOKEN="your-token"                     # Optional
   export APIFY_ACTOR_WEB_SERVER_PORT="8080"
   ```

4. **Run locally with Apify CLI**
   ```bash
   apify run
   ```

5. **Expose with Cloudflare Tunnel**
   ```bash
   cloudflared tunnel --url http://localhost:8080
   ```

6. **Open the generated HTTPS URL in your browser**

### Deploy to Apify Cloud

1. **Login to Apify**
   ```bash
   apify login
   ```

2. **Push to Apify**
   ```bash
   apify push
   ```

3. **Set environment variables** in the Apify Console:
   - `ANTHROPIC_API_KEY`
   - `KBC_URL` (optional)
   - `KBC_TOKEN` (optional)

4. **Run the actor** and access via the web server URL

## Usage

### Chat Interface

Simply type questions or requests in natural language:

- "Design a scraper for product data from example.com"
- "How do I set up a Keboola pipeline to clean CSV data?"
- "Show me an example of incremental data loading"

### Table Analysis

Use the `!table` command to analyze Keboola tables:

```
!table <table_id> <limit> [question]
```

**Examples:**

```
!table in.c-main.orders 10 what are the top products?
```

```
!table out.c-analytics.revenue 20 summarize the revenue trends
```

**Parameters:**
- `table_id`: Full table ID (e.g., `in.c-main.orders`)
- `limit`: Number of rows to sample (default: 5)
- `question`: Optional question about the data

The agent will receive the CSV sample and provide analysis, insights, or suggestions.

## Project Structure

```
.
├── src/
│   ├── main.py              # Apify actor + HTTP server
│   ├── agent.py             # Claude Agent SDK integration
│   ├── keboola_helper.py    # Keboola Storage API wrapper
│   └── templates/
│       └── chat.html        # Chat interface
├── .actor/
│   ├── actor.json           # Apify actor configuration
│   └── input_schema.json    # Input schema definition
├── requirements.txt         # Python dependencies
├── Dockerfile              # Container definition
└── README.md               # This file
```

## API Reference

### POST /chat

Send a message to the agent.

**Request:**
```json
{
  "message": "Design a scraper for product prices"
}
```

**Response:**
```json
{
  "reply": "Here's how to design a product price scraper..."
}
```

**Error Response:**
```json
{
  "error": "Error description"
}
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Anthropic API key for Claude |
| `KBC_URL` | No | Keboola connection URL |
| `KBC_TOKEN` | No | Keboola Storage API token |
| `APIFY_ACTOR_WEB_SERVER_PORT` | No | HTTP server port (default: 8080) |

## System Prompt

The agent is configured with a comprehensive system prompt that enables it to:

- Design and orchestrate Apify actors and web scrapers
- Configure Keboola Storage operations (read, write, transform)
- Propose data pipelines from any source to any destination
- Provide concrete, copy-pasteable examples
- Ask for missing details rather than making assumptions

See `src/agent.py` for the full system prompt.

## Development

### Running Tests

```bash
pytest
```

### Code Structure

- **main.py**: HTTP server setup, request routing, command parsing
- **agent.py**: Claude agent initialization, prompt building, response handling
- **keboola_helper.py**: Keboola Storage API operations, table sampling
- **chat.html**: Minimal frontend with JavaScript fetch API

### Extending

Add new commands by:
1. Creating a parser in `ChatHandler.parse_*_command()`
2. Adding context gathering logic
3. Updating the system prompt if needed

## Troubleshooting

**Agent not responding:**
- Check `ANTHROPIC_API_KEY` is set correctly
- Verify API key has sufficient credits
- Check actor logs for errors

**Keboola tables not accessible:**
- Verify `KBC_URL` points to correct connection
- Check `KBC_TOKEN` has read permissions
- Ensure table ID is correct (full format: `bucket.table`)

**HTTP server not accessible:**
- Check port is not in use
- Verify firewall rules
- Ensure web server is enabled in Apify settings

## License

Apache-2.0

## Links

- [Apify Documentation](https://docs.apify.com)
- [Claude AI Documentation](https://docs.anthropic.com)
- [Keboola Storage API](https://developers.keboola.com/integrate/storage/)
- [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
