#!/bin/bash
#
# Create SMTP credential in n8n via API
# Usage: ./create-smtp-credential.sh
#
set -e

# Load .env if exists
if [ -f .env ]; then
  set -a
  source .env
  set +a
else
  echo "Error: .env file not found"
  exit 1
fi

# Validate required vars
if [ -z "$N8N_USER" ] || [ -z "$N8N_PASSWORD" ] || [ -z "$SENDGRID_API_KEY" ]; then
  echo "Error: Missing required env vars (N8N_USER, N8N_PASSWORD, SENDGRID_API_KEY)"
  exit 1
fi

# Config
N8N_HOST="http://5.75.160.39:5678"
AUTH=$(echo -n "$N8N_USER:$N8N_PASSWORD" | base64)

echo "[create-smtp-credential] Creating SMTP credential in n8n..."

# Create SMTP credential
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
  -H "Authorization: Basic $AUTH" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"SMTP\",
    \"type\": \"smtp\",
    \"data\": {
      \"host\": \"smtp.sendgrid.net\",
      \"port\": 587,
      \"secure\": true,
      \"user\": \"apikey\",
      \"password\": \"$SENDGRID_API_KEY\"
    }
  }" \
  "$N8N_HOST/rest/credentials" 2>&1)

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
RESPONSE_BODY=$(echo "$RESPONSE" | sed '$d')

echo ""
echo "HTTP Status: $HTTP_CODE"
echo "Response:"
echo "$RESPONSE_BODY" | jq '.' 2>/dev/null || echo "$RESPONSE_BODY"
echo ""

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "201" ]; then
  echo "✅ SUCCESS: SMTP credential created!"
  echo ""
  echo "Next step: Test workflows"
  echo "  curl http://5.75.160.39:5678/form/datatalk-signup"
elif echo "$RESPONSE_BODY" | grep -qi "already exists\|duplicate"; then
  echo "ℹ️  SMTP credential already exists (this is OK)"
  echo ""
  echo "Workflows should be functional now!"
else
  echo "❌ ERROR: Failed to create SMTP credential"
  echo ""
  echo "Troubleshooting:"
  echo "1. Check n8n is running: curl http://5.75.160.39:5678/healthz"
  echo "2. Check credentials in .env are correct"
  echo "3. Try manual creation in n8n UI"
  exit 1
fi
