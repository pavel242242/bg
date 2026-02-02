#!/bin/sh
set -e

echo "[n8n-init] Starting workflow import..."

# Wait for PostgreSQL to be ready
echo "[n8n-init] Waiting for PostgreSQL..."
sleep 5

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

# Exit successfully even if some workflows failed (idempotent)
exit 0
