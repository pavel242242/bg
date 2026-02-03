#!/bin/sh
set -e

echo "[n8n-init] Starting workflow import..."

# Wait for PostgreSQL to be ready
echo "[n8n-init] Waiting for PostgreSQL..."
sleep 5

# Pre-create 'datatalk' tag to avoid duplicate key errors during import
echo "[n8n-init] Pre-creating 'datatalk' tag via SQL..."
export PGPASSWORD="$DB_POSTGRESDB_PASSWORD"
psql -h postgres -U n8n -d n8n -c "INSERT INTO tag_entity (id, name, \"createdAt\", \"updatedAt\") VALUES (gen_random_uuid()::text, 'datatalk', NOW(), NOW()) ON CONFLICT (name) DO NOTHING;" >/dev/null 2>&1 && echo "[n8n-init]   ✓ Tag created" || echo "[n8n-init]   ℹ Tag may already exist (OK)"

# Import workflows one by one to avoid tag conflicts
echo "[n8n-init] Importing workflows from /workflows directory..."

IMPORTED=0
EXISTING=0
FAILED=0

for workflow_file in /workflows/*.json; do
    # Skip backup files
    if echo "$workflow_file" | grep -q '\.bak$'; then
        continue
    fi

    echo "[n8n-init]   Importing $(basename "$workflow_file")..."

    if n8n import:workflow --input="$workflow_file" 2>&1 | tee /tmp/import_single.log; then
        if grep -q "Successfully imported" /tmp/import_single.log; then
            IMPORTED=$((IMPORTED + 1))
            echo "[n8n-init]     ✓ Success"
        elif grep -q "already exists" /tmp/import_single.log; then
            EXISTING=$((EXISTING + 1))
            echo "[n8n-init]     ℹ Already exists"
        fi
    else
        FAILED=$((FAILED + 1))
        echo "[n8n-init]     ✗ Failed"
    fi
done

echo "[n8n-init]   ✓ Imported: $IMPORTED"
echo "[n8n-init]   ℹ Already exists: $EXISTING"
echo "[n8n-init]   ✗ Failed: $FAILED"

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
