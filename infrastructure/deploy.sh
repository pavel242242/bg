#!/bin/bash
#
# Deploy DataTalk Sync to Hetzner Cloud
#
# Usage:
#   ./deploy.sh              # Deploy (create if new, rebuild if exists)
#   ./deploy.sh --create     # Create new server
#   ./deploy.sh --rebuild    # Rebuild existing server (destroys data!)
#   ./deploy.sh --destroy    # Destroy server
#   ./deploy.sh --status     # Show server status
#
set -e

# Config
SERVER_NAME="chochomesh"
SERVER_TYPE="cax11"          # Smallest EU: 2 vCPU ARM, 4GB RAM, €3.29/mo
SERVER_IMAGE="ubuntu-24.04"
SERVER_LOCATION="nbg1"       # Nuremberg, Germany (Europe)
MAX_SERVERS=3

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[+]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
error() { echo -e "${RED}[x]${NC} $1"; exit 1; }

# Load .env if exists (safer method that handles special characters)
if [ -f .env ] && [ -z "$SKIP_ENV_LOAD" ]; then
  set -a
  source .env 2>/dev/null || warn ".env has syntax errors, skipping..."
  set +a
else
  [ -n "$SKIP_ENV_LOAD" ] && warn "Skipping .env load (SKIP_ENV_LOAD set)"
fi

# Check hcloud
command -v hcloud >/dev/null 2>&1 || error "hcloud CLI not installed. Run: brew install hcloud"

# Check token (either env var or active context)
if [ -z "$HCLOUD_TOKEN" ]; then
  # Try to get token from active hcloud context
  ACTIVE_CONTEXT=$(hcloud context active 2>/dev/null)
  if [ -z "$ACTIVE_CONTEXT" ]; then
    error "HCLOUD_TOKEN not set and no active hcloud context. Run: hcloud context create <name>"
  fi

  # Read token from hcloud config file
  HCLOUD_CONFIG="${HCLOUD_CONFIG:-$HOME/.config/hcloud/cli.toml}"
  if [ -f "$HCLOUD_CONFIG" ]; then
    HCLOUD_TOKEN=$(grep -A 2 "name = \"$ACTIVE_CONTEXT\"" "$HCLOUD_CONFIG" | grep "^token" | cut -d'"' -f2)
  fi

  if [ -z "$HCLOUD_TOKEN" ]; then
    error "Could not read token from hcloud config for context: $ACTIVE_CONTEXT"
  fi

  warn "Using token from active hcloud context: $ACTIVE_CONTEXT"
fi

#
# Commands
#

status() {
  log "Server status:"
  if hcloud server describe $SERVER_NAME >/dev/null 2>&1; then
    hcloud server describe $SERVER_NAME
  else
    warn "Server $SERVER_NAME does not exist"
  fi
}

create_server() {
  # Check server count
  SERVER_COUNT=$(hcloud server list -o noheader | wc -l)
  log "Current servers: $SERVER_COUNT / $MAX_SERVERS"

  if [ "$SERVER_COUNT" -ge "$MAX_SERVERS" ]; then
    if ! hcloud server describe $SERVER_NAME >/dev/null 2>&1; then
      error "Max servers ($MAX_SERVERS) reached and $SERVER_NAME doesn't exist"
    fi
  fi

  if hcloud server describe $SERVER_NAME >/dev/null 2>&1; then
    warn "Server $SERVER_NAME already exists"
    return
  fi

  log "Creating server $SERVER_NAME..."

  # Find SSH key to use
  SSH_KEY=""
  if hcloud ssh-key describe deploy-key >/dev/null 2>&1; then
    SSH_KEY="deploy-key"
  elif [ -n "$DEPLOY_SSH_KEY_PUB" ]; then
    echo "$DEPLOY_SSH_KEY_PUB" > /tmp/deploy-key.pub
    hcloud ssh-key create --name deploy-key --public-key-from-file /tmp/deploy-key.pub
    rm /tmp/deploy-key.pub
    SSH_KEY="deploy-key"
    log "Created SSH key: deploy-key"
  else
    # Use first available SSH key
    SSH_KEY=$(hcloud ssh-key list -o noheader -o columns=name | head -1)
    if [ -z "$SSH_KEY" ]; then
      error "No SSH key available. Add DEPLOY_SSH_KEY_PUB to .env or create one in Hetzner"
    fi
    log "Using existing SSH key: $SSH_KEY"
  fi

  # Generate cloud-init with embedded secrets
  CLOUD_INIT_GENERATED=$(generate_cloud_init)

  # Create server with cloud-init
  hcloud server create \
    --name $SERVER_NAME \
    --type $SERVER_TYPE \
    --image $SERVER_IMAGE \
    --location $SERVER_LOCATION \
    --ssh-key "$SSH_KEY" \
    --user-data-from-file "$CLOUD_INIT_GENERATED" \
    --label app=datatalk-sync \
    --label managed-by=deploy-script

  rm -f "$CLOUD_INIT_GENERATED"

  log "Server created! Will auto-deploy via cloud-init (~3-5 min)"

  SERVER_IP=$(hcloud server ip $SERVER_NAME)
  log "Server IP: $SERVER_IP"
  log "n8n will be at: http://$SERVER_IP:5678"
  log "Check progress: ssh root@$SERVER_IP 'tail -f /var/log/cloud-init-output.log'"
}

generate_cloud_init() {
  # Generate cloud-init from template with embedded secrets
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  CLOUD_INIT_TEMPLATE="$SCRIPT_DIR/cloud-init.yml"
  CLOUD_INIT_GENERATED="/tmp/cloud-init-generated.yml"

  if [ ! -f "$CLOUD_INIT_TEMPLATE" ]; then
    error "cloud-init.yml not found at $CLOUD_INIT_TEMPLATE"
  fi

  # Check required vars
  for var in N8N_USER N8N_PASSWORD N8N_ENCRYPTION_KEY POSTGRES_PASSWORD; do
    if [ -z "${!var}" ]; then
      error "Required env var missing: $var (add to .env)"
    fi
  done

  # Substitute placeholders in cloud-init template
  sed -e "s|__N8N_USER__|${N8N_USER}|g" \
      -e "s|__N8N_PASSWORD__|${N8N_PASSWORD}|g" \
      -e "s|__N8N_ENCRYPTION_KEY__|${N8N_ENCRYPTION_KEY}|g" \
      -e "s|__WEBHOOK_URL__|${WEBHOOK_URL:-}|g" \
      -e "s|__POSTGRES_PASSWORD__|${POSTGRES_PASSWORD}|g" \
      -e "s|__OPENAI_API_KEY__|${OPENAI_API_KEY:-}|g" \
      -e "s|__TELEGRAM_BOT_TOKEN__|${TELEGRAM_BOT_TOKEN:-}|g" \
      -e "s|__SENDGRID_API_KEY__|${SENDGRID_API_KEY:-}|g" \
      -e "s|__SMTP_SENDER__|${SMTP_SENDER:-}|g" \
      -e "s|__SMTP_SENDER_DOMAIN__|${SMTP_SENDER_DOMAIN:-}|g" \
      -e "s|__HCLOUD_TOKEN__|${HCLOUD_TOKEN}|g" \
      "$CLOUD_INIT_TEMPLATE" > "$CLOUD_INIT_GENERATED"

  log "Generated cloud-init with embedded secrets" >&2
  echo "$CLOUD_INIT_GENERATED"
}

rebuild_server() {
  if ! hcloud server describe $SERVER_NAME >/dev/null 2>&1; then
    error "Server $SERVER_NAME doesn't exist. Use --create first."
  fi

  log "Rebuilding server $SERVER_NAME (will destroy data!)..."

  # Get all SSH key IDs from Hetzner account
  SSH_KEY_IDS=$(hcloud ssh-key list -o json | jq -r '.[].id' | tr '\n' ',' | sed 's/,$//')

  if [ -z "$SSH_KEY_IDS" ]; then
    warn "No SSH keys found in account - you won't be able to SSH after rebuild"
  else
    log "Will attach SSH keys: $SSH_KEY_IDS"
  fi

  # Generate cloud-init
  CLOUD_INIT_FILE=$(generate_cloud_init)

  # Get server ID
  SERVER_ID=$(hcloud server describe $SERVER_NAME -o json | jq -r '.id')
  SERVER_IP=$(hcloud server ip $SERVER_NAME)

  log "Server ID: $SERVER_ID, IP: $SERVER_IP"

  # Encode cloud-init to base64
  CLOUD_INIT_BASE64=$(cat "$CLOUD_INIT_FILE" | base64)

  # Build JSON payload with SSH keys
  if [ -n "$SSH_KEY_IDS" ]; then
    # Convert comma-separated IDs to JSON array
    SSH_KEYS_JSON=$(echo "[$SSH_KEY_IDS]")
    JSON_PAYLOAD=$(jq -n \
      --arg image "$SERVER_IMAGE" \
      --arg userdata "$CLOUD_INIT_BASE64" \
      --argjson sshkeys "$SSH_KEYS_JSON" \
      '{image: $image, user_data: $userdata, ssh_keys: $sshkeys}')
  else
    JSON_PAYLOAD=$(jq -n \
      --arg image "$SERVER_IMAGE" \
      --arg userdata "$CLOUD_INIT_BASE64" \
      '{image: $image, user_data: $userdata}')
  fi

  # Rebuild via API
  log "Calling rebuild API..."
  RESPONSE=$(curl -s -X POST \
    -H "Authorization: Bearer $HCLOUD_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$JSON_PAYLOAD" \
    "https://api.hetzner.cloud/v1/servers/$SERVER_ID/actions/rebuild")

  # Check for errors
  if echo "$RESPONSE" | jq -e '.error' > /dev/null 2>&1; then
    ERROR_MSG=$(echo "$RESPONSE" | jq -r '.error.message')
    error "Rebuild failed: $ERROR_MSG"
  fi

  # Wait for rebuild
  ACTION_ID=$(echo "$RESPONSE" | jq -r '.action.id')
  log "Waiting for rebuild action $ACTION_ID..."

  for i in {1..60}; do
    STATUS=$(curl -s -H "Authorization: Bearer $HCLOUD_TOKEN" \
      "https://api.hetzner.cloud/v1/actions/$ACTION_ID" | jq -r '.action.status')

    if [ "$STATUS" = "success" ]; then
      log "Rebuild completed!"
      break
    elif [ "$STATUS" = "error" ]; then
      error "Rebuild failed!"
    fi
    echo "  Status: $STATUS (attempt $i/60)"
    sleep 5
  done

  rm -f "$CLOUD_INIT_FILE"

  log "Server rebuilt! Cloud-init will deploy everything (~3-5 min)"
  log "n8n URL: http://$SERVER_IP:5678"
  log "Check progress: ssh root@$SERVER_IP 'tail -f /var/log/cloud-init-output.log'"
}

deploy() {
  # Check if server exists
  if hcloud server describe $SERVER_NAME >/dev/null 2>&1; then
    # Server exists - delete and recreate for clean deployment
    warn "Server exists. For clean deployment with SSH keys, will delete and recreate."
    read -p "Continue? (yes/no): " confirm
    [ "$confirm" != "yes" ] && { log "Deployment cancelled"; return; }

    log "Deleting server $SERVER_NAME..."
    hcloud server delete $SERVER_NAME
    sleep 5
  fi

  # Create server
  log "Creating server..."
  create_server
}

destroy() {
  warn "This will destroy server $SERVER_NAME"
  read -p "Are you sure? (yes/no): " confirm
  [ "$confirm" != "yes" ] && exit 0

  if hcloud server describe $SERVER_NAME >/dev/null 2>&1; then
    hcloud server delete $SERVER_NAME
    log "Server destroyed"
  else
    warn "Server doesn't exist"
  fi
}

#
# Main
#

case "${1:-deploy}" in
  --create)
    create_server
    ;;
  --rebuild)
    rebuild_server
    ;;
  --destroy)
    destroy
    ;;
  --status)
    status
    ;;
  deploy|"")
    deploy
    ;;
  *)
    echo "Usage: $0 [--create|--rebuild|--destroy|--status]"
    exit 1
    ;;
esac
