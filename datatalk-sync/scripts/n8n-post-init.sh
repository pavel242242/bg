#!/bin/sh
set -e

echo "[n8n-post-init] Starting post-initialization..."

AUTH=$(echo -n "$N8N_USER:$N8N_PASSWORD" | base64)
API="$N8N_HOST/api/v1"

# Wait for n8n API to be ready
echo "[n8n-post-init] Waiting for n8n API..."
for i in $(seq 1 30); do
    if curl -sf -H "Authorization: Basic $AUTH" "$API/workflows" >/dev/null 2>&1; then
        echo "[n8n-post-init] n8n API ready!"
        break
    fi
    echo "[n8n-post-init]   Attempt $i/30..."
    sleep 2
done

# Check if we successfully connected
if ! curl -sf -H "Authorization: Basic $AUTH" "$API/workflows" >/dev/null 2>&1; then
    echo "[n8n-post-init] ERROR: Could not connect to n8n API"
    exit 1
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

echo "[n8n-post-init] Post-initialization complete!"
exit 0
