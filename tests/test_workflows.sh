#!/bin/bash
# Test n8n workflow JSON files
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
WORKFLOWS_DIR="$ROOT_DIR/datatalk-sync/workflows"

echo "=== Testing n8n Workflows ==="

# Test 1: All JSON files are valid
echo -n "Validating JSON syntax... "
for file in "$WORKFLOWS_DIR"/*.json; do
  if ! python3 -m json.tool "$file" > /dev/null 2>&1; then
    echo "FAIL"
    echo "Invalid JSON: $file"
    exit 1
  fi
done
echo "OK"

# Test 2: All workflows have required fields
echo -n "Checking required fields... "
for file in "$WORKFLOWS_DIR"/*.json; do
  name=$(python3 -c "import json; print(json.load(open('$file')).get('name', ''))")
  nodes=$(python3 -c "import json; print(len(json.load(open('$file')).get('nodes', [])))")

  if [ -z "$name" ]; then
    echo "FAIL"
    echo "Missing 'name' in $file"
    exit 1
  fi

  if [ "$nodes" -eq 0 ]; then
    echo "FAIL"
    echo "No nodes in $file"
    exit 1
  fi
done
echo "OK"

# Test 3: All nodes have required properties
echo -n "Validating node structure... "
python3 << 'PYTHON'
import json
import sys
from pathlib import Path

workflows_dir = Path("datatalk-sync/workflows")
errors = []

for f in workflows_dir.glob("*.json"):
    data = json.load(open(f))
    for node in data.get("nodes", []):
        if "type" not in node:
            errors.append(f"{f.name}: node missing 'type'")
        if "name" not in node:
            errors.append(f"{f.name}: node missing 'name'")
        if "position" not in node:
            errors.append(f"{f.name}: node '{node.get('name', '?')}' missing 'position'")

if errors:
    print("FAIL")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
print("OK")
PYTHON

# Test 4: Connections reference valid nodes
echo -n "Validating connections... "
python3 << 'PYTHON'
import json
import sys
from pathlib import Path

workflows_dir = Path("datatalk-sync/workflows")
errors = []

for f in workflows_dir.glob("*.json"):
    data = json.load(open(f))
    node_names = {n["name"] for n in data.get("nodes", [])}

    for source, targets in data.get("connections", {}).items():
        if source not in node_names:
            errors.append(f"{f.name}: connection from unknown node '{source}'")

        for output in targets.get("main", []):
            for conn in output:
                if conn.get("node") not in node_names:
                    errors.append(f"{f.name}: connection to unknown node '{conn.get('node')}'")

if errors:
    print("FAIL")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
print("OK")
PYTHON

echo ""
echo "All workflow tests passed!"
