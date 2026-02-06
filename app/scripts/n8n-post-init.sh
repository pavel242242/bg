#!/bin/sh
set -e

echo "[n8n-post-init] Installing dependencies..."
apk add --no-cache curl jq >/dev/null 2>&1

echo "[n8n-post-init] Starting post-initialization..."

API="$N8N_HOST/rest"

# Wait for n8n to respond
echo "[n8n-post-init] Waiting for n8n to start..."
for i in $(seq 1 60); do
    if curl -sf "$N8N_HOST/" >/dev/null 2>&1; then
        echo "[n8n-post-init] n8n is responding!"
        sleep 5  # Extra wait for full initialization
        break
    fi
    echo "[n8n-post-init]   Attempt $i/60..."
    sleep 2
done

# Create owner account (idempotent - fails silently if exists)
# Use jq to safely build JSON with special characters in password
echo "[n8n-post-init] Creating owner account..."
SETUP_PAYLOAD=$(jq -n \
  --arg email "$N8N_USER" \
  --arg password "$N8N_PASSWORD" \
  '{email: $email, password: $password, firstName: "Admin", lastName: "User"}')

OWNER_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
  -H "Content-Type: application/json" \
  -d "$SETUP_PAYLOAD" \
  "$N8N_HOST/rest/owner/setup" 2>&1)

HTTP_CODE=$(echo "$OWNER_RESPONSE" | tail -1)
RESPONSE_BODY=$(echo "$OWNER_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    echo "[n8n-post-init]   ✓ Owner account created: $N8N_USER"
elif echo "$RESPONSE_BODY" | grep -qi "already.*set.up\|already exists"; then
    echo "[n8n-post-init]   ℹ Owner account already exists"
else
    echo "[n8n-post-init]   ⚠ Setup response (HTTP $HTTP_CODE): $RESPONSE_BODY"
fi

# Login to get session cookie for API calls
echo "[n8n-post-init] Logging in..."
LOGIN_PAYLOAD=$(jq -n \
  --arg email "$N8N_USER" \
  --arg password "$N8N_PASSWORD" \
  '{emailOrLdapLoginId: $email, password: $password}')

COOKIE_JAR="/tmp/n8n_cookies"
LOGIN_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
  -H "Content-Type: application/json" \
  -c "$COOKIE_JAR" \
  -d "$LOGIN_PAYLOAD" \
  "$N8N_HOST/rest/login" 2>&1)

LOGIN_CODE=$(echo "$LOGIN_RESPONSE" | tail -1)
if [ "$LOGIN_CODE" = "200" ]; then
    echo "[n8n-post-init]   ✓ Logged in"
else
    echo "[n8n-post-init]   ⚠ Login failed (HTTP $LOGIN_CODE), skipping API operations"
    echo "[n8n-post-init] Post-initialization complete (partial)!"
    exit 0
fi

# 1. Create SMTP credential
echo "[n8n-post-init] Creating SMTP credential..."
SMTP_PAYLOAD=$(jq -n \
  --arg host "$SMTP_HOST" \
  --arg port "$SMTP_PORT" \
  --arg user "$SMTP_USER" \
  --arg pass "$SMTP_PASS" \
  '{name: "SMTP", type: "smtp", data: {host: $host, port: ($port | tonumber), secure: true, user: $user, password: $pass}}')

SMTP_RESPONSE=$(curl -s -X POST \
  -b "$COOKIE_JAR" \
  -H "Content-Type: application/json" \
  -d "$SMTP_PAYLOAD" \
  "$API/credentials" 2>&1 || true)

if echo "$SMTP_RESPONSE" | grep -q '"id"'; then
    echo "[n8n-post-init]   ✓ SMTP credential created"
elif echo "$SMTP_RESPONSE" | grep -qi "already exists\|duplicate"; then
    echo "[n8n-post-init]   ℹ SMTP credential already exists"
else
    echo "[n8n-post-init]   ⚠ Could not create SMTP credential: $SMTP_RESPONSE"
fi

# 2. Activate all workflows
echo "[n8n-post-init] Activating workflows..."
WORKFLOWS=$(curl -s -b "$COOKIE_JAR" "$API/workflows" 2>/dev/null || echo "")

if [ -z "$WORKFLOWS" ]; then
    echo "[n8n-post-init]   ⚠ No workflows found or API error"
else
    WORKFLOW_IDS=$(echo "$WORKFLOWS" | jq -r '.data[]?.id // empty' 2>/dev/null)

    if [ -z "$WORKFLOW_IDS" ]; then
        echo "[n8n-post-init]   ℹ No workflows to activate"
    else
        ACTIVATED=0
        for wf_id in $WORKFLOW_IDS; do
            echo "[n8n-post-init]   Activating workflow: $wf_id"
            if curl -s -X PATCH \
              -b "$COOKIE_JAR" \
              -H "Content-Type: application/json" \
              -d '{"active":true}' \
              "$API/workflows/$wf_id" >/dev/null 2>&1; then
                ACTIVATED=$((ACTIVATED + 1))
                echo "[n8n-post-init]     ✓ Activated"
            else
                echo "[n8n-post-init]     ⚠ Failed to activate"
            fi
        done
        echo "[n8n-post-init]   Summary: $ACTIVATED workflows activated"
    fi
fi

rm -f "$COOKIE_JAR"
echo "[n8n-post-init] Post-initialization complete!"
exit 0
