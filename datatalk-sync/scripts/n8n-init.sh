#!/bin/sh
set -e

echo "[n8n-init] Starting workflow import..."

# Wait for PostgreSQL to be ready
echo "[n8n-init] Waiting for PostgreSQL..."
sleep 5

# Import all workflows from /workflows/*.json
IMPORTED_COUNT=0
FAILED_COUNT=0

for workflow in /workflows/*.json; do
    if [ -f "$workflow" ]; then
        WORKFLOW_NAME=$(basename "$workflow")
        echo "[n8n-init] Importing $WORKFLOW_NAME..."

        if n8n import:workflow --input="$workflow" --separate 2>&1 | tee /tmp/import.log; then
            # Check if import was successful or already exists
            if grep -q "Successfully imported" /tmp/import.log || grep -q "already exists" /tmp/import.log; then
                IMPORTED_COUNT=$((IMPORTED_COUNT + 1))
                echo "[n8n-init]   ✓ $WORKFLOW_NAME processed"
            else
                FAILED_COUNT=$((FAILED_COUNT + 1))
                echo "[n8n-init]   ✗ $WORKFLOW_NAME failed"
            fi
        else
            FAILED_COUNT=$((FAILED_COUNT + 1))
            echo "[n8n-init]   ✗ $WORKFLOW_NAME error"
        fi
    fi
done

echo "[n8n-init] Workflow import complete!"
echo "[n8n-init] Summary: $IMPORTED_COUNT processed, $FAILED_COUNT failed"

# Exit successfully even if some workflows failed (idempotent)
exit 0
