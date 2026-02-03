#!/bin/sh
set -e

echo "[n8n-init] Starting workflow import..."

# Wait for PostgreSQL to be ready
echo "[n8n-init] Waiting for PostgreSQL..."
sleep 5

# Pre-create 'datatalk' tag to avoid duplicate key errors during import
echo "[n8n-init] Pre-creating 'datatalk' tag..."
n8n create:tag --name="datatalk" >/dev/null 2>&1 || echo "[n8n-init]   ℹ Tag may already exist (OK)"

# Import all workflows from /workflows directory (n8n CLI requires directory input)
echo "[n8n-init] Importing workflows from /workflows directory..."

if n8n import:workflow --input=/workflows --separate 2>&1 | tee /tmp/import.log; then
    # Count successes and failures
    IMPORTED=$(grep -c "Successfully imported" /tmp/import.log || echo "0")
    EXISTING=$(grep -c "already exists" /tmp/import.log || echo "0")
    FAILED=$(grep -c "Failed to import" /tmp/import.log || echo "0")

    echo "[n8n-init]   ✓ Imported: $IMPORTED"
    echo "[n8n-init]   ℹ Already exists: $EXISTING"
    echo "[n8n-init]   ✗ Failed: $FAILED"
else
    echo "[n8n-init]   ⚠ Import command failed, check logs"
fi

echo "[n8n-init] Workflow import complete!"

# Activate all workflows
echo "[n8n-init] Activating workflows..."

# Get all workflow IDs from database using n8n CLI
if n8n list:workflow 2>&1 | tee /tmp/workflows.log; then
    # Extract workflow IDs (format: "ID|Name")
    # Filter only lines with pipe and extract first field
    WORKFLOW_IDS=$(grep '|' /tmp/workflows.log | cut -d'|' -f1 | tr '\n' ' ')

    if [ -z "$WORKFLOW_IDS" ]; then
        echo "[n8n-init]   ℹ No workflows found to activate"
    else
        ACTIVATED=0
        for wf_id in $WORKFLOW_IDS; do
            echo "[n8n-init]   Activating workflow: $wf_id"
            if n8n update:workflow --id="$wf_id" --active=true >/dev/null 2>&1; then
                ACTIVATED=$((ACTIVATED + 1))
                echo "[n8n-init]     ✓ Activated"
            else
                echo "[n8n-init]     ⚠ Failed to activate (may already be active)"
            fi
        done
        echo "[n8n-init]   ✓ Summary: $ACTIVATED/$( echo "$WORKFLOW_IDS" | wc -w) workflows activated"
    fi
else
    echo "[n8n-init]   ⚠ Could not list workflows"
fi

echo "[n8n-init] Complete!"

# Exit successfully even if some workflows failed (idempotent)
exit 0
