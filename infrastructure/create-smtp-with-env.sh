#!/bin/bash
#
# Wrapper to load .env and create SMTP credential
#
set -e

cd "$(dirname "$0")"

# Load .env (same method as deploy.sh)
if [ -f .env ]; then
  set -a
  source .env 2>/dev/null || { echo "Error: .env has syntax errors"; exit 1; }
  set +a
  echo "✅ Loaded .env"
else
  echo "❌ Error: .env file not found"
  exit 1
fi

# Use SENDGRID_TOKEN if SENDGRID_API_KEY is not set
if [ -z "$SENDGRID_API_KEY" ] && [ -n "$SENDGRID_TOKEN" ]; then
  SENDGRID_API_KEY="$SENDGRID_TOKEN"
fi

# Validate required vars
if [ -z "$N8N_USER" ] || [ -z "$N8N_PASSWORD" ] || [ -z "$SENDGRID_API_KEY" ]; then
  echo "❌ Error: Missing required env vars"
  echo "   N8N_USER: ${N8N_USER:+set}"
  echo "   N8N_PASSWORD: ${N8N_PASSWORD:+set}"
  echo "   SENDGRID_API_KEY: ${SENDGRID_API_KEY:+set}"
  echo "   SENDGRID_TOKEN: ${SENDGRID_TOKEN:+set}"
  exit 1
fi

echo "✅ All credentials loaded"
echo ""

# Config
N8N_HOST="http://5.75.160.39:5678"
AUTH=$(echo -n "$N8N_USER:$N8N_PASSWORD" | base64)

echo "🔐 Creating SMTP credential in n8n..."
echo "   Host: $N8N_HOST"
echo "   User: $N8N_USER"
echo ""

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

echo "Response (HTTP $HTTP_CODE):"
echo "$RESPONSE_BODY" | jq '.' 2>/dev/null || echo "$RESPONSE_BODY"
echo ""

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "201" ]; then
  echo "✅ SUCCESS: SMTP credential created!"
  CRED_ID=$(echo "$RESPONSE_BODY" | jq -r '.id' 2>/dev/null)
  echo "   Credential ID: $CRED_ID"
  echo ""
  echo "🎯 Next: Test workflows"
  echo "   curl http://5.75.160.39:5678/form/datatalk-signup"
  echo ""
  echo "✅ All 4 workflows should now be executable!"
  exit 0
elif echo "$RESPONSE_BODY" | grep -qi "already exists\|duplicate\|unique constraint"; then
  echo "ℹ️  SMTP credential already exists"
  echo ""
  echo "✅ Workflows should already be functional!"
  echo ""
  echo "Test workflows:"
  echo "  curl http://5.75.160.39:5678/form/datatalk-signup"
  exit 0
else
  echo "❌ ERROR: Failed to create SMTP credential"
  echo ""
  if [ "$HTTP_CODE" = "401" ]; then
    echo "🔍 Authentication failed. Possible causes:"
    echo "   1. Wrong N8N_USER or N8N_PASSWORD in .env"
    echo "   2. Owner account not set up yet"
    echo "   3. n8n using different auth method"
  elif [ "$HTTP_CODE" = "404" ]; then
    echo "🔍 API endpoint not found. Check n8n version."
  else
    echo "🔍 Unexpected error. Check n8n logs:"
    echo "   docker logs datatalk-n8n"
  fi
  exit 1
fi
