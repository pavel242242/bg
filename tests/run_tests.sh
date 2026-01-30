#!/bin/bash
# Run all tests
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "================================"
echo "  DataTalk Sync Test Suite"
echo "================================"
echo ""

# Run workflow tests
./test_workflows.sh
echo ""

# Run docker tests
./test_docker.sh
echo ""

echo "================================"
echo "  All tests passed!"
echo "================================"
