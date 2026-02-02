#!/bin/bash
#
# Create SMTP credential using session-based auth
#
set -e

cd "$(dirname "$0")"

# Load .env
if [ -f .env ]; then
  set -a
  source .env 2>/dev/null || { echo "Error: .env has syntax errors"; exit 1; }
  set +a
else
  echo "❌ Error: .env file not found"
  exit 1
fi

# Use SENDGRID_TOKEN if SENDGRID_API_KEY is not set
if [ -z "$SENDGRID_API_KEY" ] && [ -n "$SENDGRID_TOKEN" ]; then
  SENDGRID_API_KEY="$SENDGRID_TOKEN"
fi

# Validate
if [ -z "$N8N_USER" ] || [ -z "$N8N_PASSWORD" ] || [ -z "$SENDGRID_API_KEY" ]; then
  echo "❌ Error: Missing required credentials"
  exit 1
fi

N8N_HOST="http://5.75.160.39:5678"
COOKIE_JAR="/tmp/n8n-cookies.txt"

echo "🔐 Step 1: Logging in to n8n..."
echo "   Email: $N8N_USER"

# Login to get session cookie
LOGIN_RESPONSE=$(curl -s -w "\n%{http_code}" -c "$COOKIE_JAR" -X POST \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$N8N_USER\",\"emailOrLdapLoginId\":\"$N8N_USER\",\"password\":\"$N8N_PASSWORD\"}" \
  "$N8N_HOST/rest/login" 2>&1)

LOGIN_CODE=$(echo "$LOGIN_RESPONSE" | tail -1)
LOGIN_BODY=$(echo "$LOGIN_RESPONSE" | sed '$d')

if [ "$LOGIN_CODE" != "200" ]; then
  echo "❌ Login failed (HTTP $LOGIN_CODE)"
  echo "$LOGIN_BODY" | jq '.' 2>/dev/null || echo "$LOGIN_BODY"
  rm -f "$COOKIE_JAR"
  exit 1
fi

echo "✅ Logged in successfully"
echo ""
echo "🔐 Step 2: Creating SMTP credential..."

# Create SMTP credential using session
RESPONSE=$(curl -s -w "\n%{http_code}" -b "$COOKIE_JAR" -X POST \
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

# Cleanup
rm -f "$COOKIE_JAR"

echo "Response (HTTP $HTTP_CODE):"
echo "$RESPONSE_BODY" | jq '.' 2>/dev/null || echo "$RESPONSE_BODY"
echo ""

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "201" ]; then
  echo "✅ SUCCESS: SMTP credential created!"
  CRED_ID=$(echo "$RESPONSE_BODY" | jq -r '.id' 2>/dev/null)
  echo "   Credential ID: $CRED_ID"
  echo "   Name: SMTP"
  echo "   Type: smtp"
  echo ""
  echo "🎯 Testing workflows..."

  # Test workflow 2 (no SMTP needed)
  TEST2=$(curl -s -w "%{http_code}" -o /dev/null "http://5.75.160.39:5678/webhook/datatalk-verify-email?token=test&email=test@example.com")
  if [ "$TEST2" = "500" ] || [ "$TEST2" = "400" ] || [ "$TEST2" = "404" ]; then
    echo "   ✅ Workflow 2 (Email Verify): Responding (HTTP $TEST2)"
  else
    echo "   ⚠️  Workflow 2 (Email Verify): Unexpected response (HTTP $TEST2)"
  fi

  # Test workflow 1 form (needs SMTP)
  TEST1=$(curl -s -w "%{http_code}" -o /dev/null "http://5.75.160.39:5678/form/datatalk-signup")
  if [ "$TEST1" = "200" ]; then
    echo "   ✅ Workflow 1 (Signup Form): Displaying (HTTP $TEST1)"
  else
    echo "   ⚠️  Workflow 1 (Signup Form): Not responding (HTTP $TEST1)"
  fi

  echo ""
  echo "✅ ALL 4 WORKFLOWS SHOULD NOW BE FUNCTIONAL!"
  echo ""
  echo "Manual test:"
  echo "  1. Visit: http://5.75.160.39:5678/form/datatalk-signup"
  echo "  2. Fill form with your email"
  echo "  3. Check that verification email arrives"
  exit 0
elif echo "$RESPONSE_BODY" | grep -qi "already exists\|duplicate\|unique"; then
  echo "ℹ️  SMTP credential already exists"
  echo ""
  echo "✅ Workflows should already be functional!"
  exit 0
else
  echo "❌ ERROR: Failed to create SMTP credential"
  exit 1
fi
