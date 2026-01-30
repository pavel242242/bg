#!/bin/bash
# Test Docker configuration
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== Testing Docker Configuration ==="

# Test 1: docker-compose.yml is valid
echo -n "Validating docker-compose.yml... "
cd "$ROOT_DIR/datatalk-sync"
if docker compose config --quiet 2>/dev/null; then
  echo "OK"
else
  echo "FAIL"
  exit 1
fi

# Test 2: Required environment variables are referenced
echo -n "Checking env var references... "
REQUIRED_VARS=(
  "N8N_USER"
  "N8N_PASSWORD"
  "N8N_ENCRYPTION_KEY"
  "WEBHOOK_URL"
  "OPENAI_API_KEY"
  "TELEGRAM_BOT_TOKEN"
  "SMTP_HOST"
)

for var in "${REQUIRED_VARS[@]}"; do
  if ! grep -q "\${$var}" docker-compose.yml; then
    echo "FAIL"
    echo "Missing reference to $var"
    exit 1
  fi
done
echo "OK"

# Test 3: .env.example exists and has all vars
echo -n "Checking .env.example... "
if [ ! -f .env.example ]; then
  echo "FAIL"
  echo ".env.example not found"
  exit 1
fi

for var in "${REQUIRED_VARS[@]}"; do
  if ! grep -q "^$var=" .env.example; then
    echo "FAIL"
    echo "Missing $var in .env.example"
    exit 1
  fi
done
echo "OK"

# Test 4: No secrets in committed files
echo -n "Checking for leaked secrets... "
if grep -rE "(sk-[a-zA-Z0-9]{20,}|[0-9]+:[A-Za-z0-9_-]{35})" \
   --include="*.json" --include="*.yml" --include="*.yaml" \
   "$ROOT_DIR/datatalk-sync" 2>/dev/null; then
  echo "FAIL"
  echo "Potential secrets found in committed files!"
  exit 1
fi
echo "OK"

echo ""
echo "All Docker tests passed!"
