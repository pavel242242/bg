#!/bin/bash
#
# Setup GitHub Actions secrets for DataTalk Sync
# Run this locally after authenticating with: gh auth login
#
set -e

REPO="chocholous/bg"

echo "Setting up GitHub Actions secrets for $REPO"
echo "============================================"

# Check gh auth
if ! gh auth status &>/dev/null; then
  echo "Please authenticate first: gh auth login"
  exit 1
fi

# Load .env if exists
if [ -f .env ]; then
  echo "Loading secrets from .env..."
  export $(grep -v '^#' .env | xargs)
fi

# Set secrets
set_secret() {
  local name=$1
  local value=$2
  if [ -n "$value" ]; then
    echo "$value" | gh secret set "$name" --repo "$REPO"
    echo "  Set: $name"
  else
    echo "  Skip: $name (not set)"
  fi
}

echo ""
echo "Setting Hetzner secrets..."
set_secret "HCLOUD_TOKEN" "$HCLOUD_TOKEN"

echo ""
echo "Setting n8n secrets..."
set_secret "N8N_USER" "$N8N_USER"
set_secret "N8N_PASSWORD" "$N8N_PASSWORD"
set_secret "N8N_ENCRYPTION_KEY" "$N8N_ENCRYPTION_KEY"
set_secret "WEBHOOK_URL" "$WEBHOOK_URL"

echo ""
echo "Setting API secrets..."
set_secret "OPENAI_API_KEY" "$OPENAI_API_KEY"
set_secret "TELEGRAM_BOT_TOKEN" "$TELEGRAM_BOT_TOKEN"

echo ""
echo "Setting SMTP secrets..."
set_secret "SMTP_HOST" "$SMTP_HOST"
set_secret "SMTP_PORT" "$SMTP_PORT"
set_secret "SMTP_USER" "$SMTP_USER"
set_secret "SMTP_PASS" "$SMTP_PASS"
set_secret "SMTP_SENDER" "$SMTP_SENDER"

echo ""
echo "Setting deploy secrets..."
set_secret "DEPLOY_SSH_KEY" "$DEPLOY_SSH_KEY"
set_secret "DEPLOY_SSH_KEY_PUB" "$DEPLOY_SSH_KEY_PUB"

echo ""
echo "Done! Verify with: gh secret list --repo $REPO"
