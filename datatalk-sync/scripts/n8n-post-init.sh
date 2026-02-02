#!/bin/sh
set -e

echo "[n8n-post-init] Installing dependencies..."
apk add --no-cache curl jq >/dev/null 2>&1

echo "[n8n-post-init] Starting post-initialization..."

AUTH=$(echo -n "$N8N_USER:$N8N_PASSWORD" | base64)
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
echo "[n8n-post-init] Creating owner account..."
OWNER_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$N8N_USER\",
    \"password\": \"$N8N_PASSWORD\",
    \"firstName\": \"Admin\",
    \"lastName\": \"User\"
  }" \
  "$N8N_HOST/rest/owner/setup" 2>&1)

HTTP_CODE=$(echo "$OWNER_RESPONSE" | tail -1)
RESPONSE_BODY=$(echo "$OWNER_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    echo "[n8n-post-init]   ✓ Owner account created: $N8N_USER"
elif echo "$RESPONSE_BODY" | grep -q "owner has already been set up"; then
    echo "[n8n-post-init]   ℹ Owner account already exists"
else
    echo "[n8n-post-init]   ⚠ Setup response (HTTP $HTTP_CODE): $RESPONSE_BODY"
fi

# Wait for owner to be fully initialized
sleep 10

# Now try to authenticate (may fail if using session-based auth)
echo "[n8n-post-init] Checking API access..."
WORKFLOWS_TEST=$(curl -s -w "\n%{http_code}" "$API/workflows" 2>/dev/null)
TEST_HTTP_CODE=$(echo "$WORKFLOWS_TEST" | tail -1)

if [ "$TEST_HTTP_CODE" = "401" ]; then
    echo "[n8n-post-init]   ℹ API requires authentication (normal for owner accounts)"
elif [ "$TEST_HTTP_CODE" = "200" ]; then
    echo "[n8n-post-init]   ✓ API accessible"
else
    echo "[n8n-post-init]   ⚠ Unexpected response: HTTP $TEST_HTTP_CODE"
fi

# 1. Create SMTP credential
echo "[n8n-post-init] Creating SMTP credential..."
SMTP_RESPONSE=$(curl -s -X POST \
  -H "Authorization: Basic $AUTH" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"SMTP\",
    \"type\": \"smtp\",
    \"data\": {
      \"host\": \"$SMTP_HOST\",
      \"port\": $SMTP_PORT,
      \"secure\": true,
      \"user\": \"$SMTP_USER\",
      \"password\": \"$SMTP_PASS\"
    }
  }" \
  "$API/credentials" 2>&1 || true)

if echo "$SMTP_RESPONSE" | grep -q "id"; then
    echo "[n8n-post-init]   ✓ SMTP credential created"
elif echo "$SMTP_RESPONSE" | grep -qi "already exists\|duplicate"; then
    echo "[n8n-post-init]   ℹ SMTP credential already exists"
else
    echo "[n8n-post-init]   ⚠ Could not create SMTP credential (may already exist)"
fi

# 2. Activate all workflows
echo "[n8n-post-init] Activating workflows..."
WORKFLOWS=$(curl -s -H "Authorization: Basic $AUTH" "$API/workflows" 2>/dev/null || echo "")

if [ -z "$WORKFLOWS" ]; then
    echo "[n8n-post-init]   ⚠ No workflows found or API error"
else
    # Extract workflow IDs (simple grep approach for Alpine sh)
    WORKFLOW_IDS=$(echo "$WORKFLOWS" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)

    if [ -z "$WORKFLOW_IDS" ]; then
        echo "[n8n-post-init]   ℹ No workflows to activate"
    else
        ACTIVATED=0
        for wf_id in $WORKFLOW_IDS; do
            echo "[n8n-post-init]   Activating workflow: $wf_id"
            if curl -s -X PATCH \
              -H "Authorization: Basic $AUTH" \
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

# Import workflows
echo "[n8n-post-init] Importing workflows..."
IMPORTED=0
SKIPPED=0

# Get auth cookie
AUTH_COOKIE=$(curl -s -c - -X POST \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$N8N_USER\",\"password\":\"$N8N_PASSWORD\"}" \
  "$N8N_HOST/rest/login" | grep -o 'n8n-auth[^\t]*' | head -1)

for workflow_file in /workflows/*.json; do
    if [ -f "$workflow_file" ]; then
        WORKFLOW_NAME=$(basename "$workflow_file")
        echo "[n8n-post-init]   Importing $WORKFLOW_NAME..."

        # Read workflow JSON
        WORKFLOW_DATA=$(cat "$workflow_file")

        # Import via API
        IMPORT_RESPONSE=$(curl -s -X POST \
          -H "Content-Type: application/json" \
          -H "Cookie: $AUTH_COOKIE" \
          -d "$WORKFLOW_DATA" \
          "$N8N_HOST/rest/workflows" 2>&1)

        if echo "$IMPORT_RESPONSE" | grep -q "\"id\""; then
            IMPORTED=$((IMPORTED + 1))
            echo "[n8n-post-init]     ✓ Imported"
        elif echo "$IMPORT_RESPONSE" | grep -qi "already exists\|duplicate"; then
            SKIPPED=$((SKIPPED + 1))
            echo "[n8n-post-init]     ℹ Already exists"
        else
            echo "[n8n-post-init]     ⚠ Failed: $(echo "$IMPORT_RESPONSE" | head -c 100)"
        fi
    fi
done

echo "[n8n-post-init]   Summary: $IMPORTED imported, $SKIPPED skipped"

echo "[n8n-post-init] Post-initialization complete!"
exit 0
