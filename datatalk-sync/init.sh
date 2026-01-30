#!/bin/sh
set -e

echo "=== n8n Init Script ==="

# Check if workflows have already been imported (marker file)
MARKER_FILE="/home/node/.n8n/.workflows-imported"

if [ -f "$MARKER_FILE" ]; then
    echo "Workflows already imported, skipping..."
    exit 0
fi

echo "Importing workflows..."

# Import each workflow file
for workflow in /workflows/*.json; do
    if [ -f "$workflow" ]; then
        echo "Importing: $workflow"
        n8n import:workflow --input="$workflow" || echo "Warning: Failed to import $workflow"
    fi
done

# Create SQLite credential
echo "Creating SQLite credential..."
cat > /tmp/sqlite-cred.json << 'EOF'
{
  "name": "SQLite DB",
  "type": "sqlite",
  "data": {
    "database": "/home/node/.n8n/datatalk.db"
  }
}
EOF

n8n import:credentials --input=/tmp/sqlite-cred.json || echo "Warning: Failed to import SQLite credential"
rm -f /tmp/sqlite-cred.json

# Create SMTP credential placeholder
echo "Creating SMTP credential..."
cat > /tmp/smtp-cred.json << 'EOF'
{
  "name": "SMTP",
  "type": "smtp",
  "data": {
    "host": "",
    "port": 587,
    "secure": false,
    "user": "",
    "password": ""
  }
}
EOF

n8n import:credentials --input=/tmp/smtp-cred.json || echo "Warning: Failed to import SMTP credential"
rm -f /tmp/smtp-cred.json

# Create OpenAI API Key credential placeholder
echo "Creating OpenAI API Key credential..."
cat > /tmp/openai-cred.json << 'EOF'
{
  "name": "OpenAI API Key",
  "type": "httpHeaderAuth",
  "data": {
    "name": "Authorization",
    "value": "Bearer "
  }
}
EOF

n8n import:credentials --input=/tmp/openai-cred.json || echo "Warning: Failed to import OpenAI credential"
rm -f /tmp/openai-cred.json

# Mark as imported
touch "$MARKER_FILE"
echo "=== Init complete ==="
