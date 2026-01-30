#!/bin/bash
#
# Deploy DataTalk Sync to Hetzner Cloud
#
# Usage:
#   ./deploy.sh              # Deploy using .env
#   ./deploy.sh --create     # Create server if not exists
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

# Load .env if exists
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

# Check hcloud
command -v hcloud >/dev/null 2>&1 || error "hcloud CLI not installed. Run: brew install hcloud"

# Check token
[ -z "$HCLOUD_TOKEN" ] && error "HCLOUD_TOKEN not set. Add to .env or export it."

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

  # Create server
  hcloud server create \
    --name $SERVER_NAME \
    --type $SERVER_TYPE \
    --image $SERVER_IMAGE \
    --location $SERVER_LOCATION \
    --ssh-key "$SSH_KEY" \
    --label app=datatalk-sync \
    --label managed-by=deploy-script

  log "Server created! Waiting for it to be ready..."
  sleep 30

  SERVER_IP=$(hcloud server ip $SERVER_NAME)
  log "Server IP: $SERVER_IP"

  # Install Docker
  log "Installing Docker..."
  ssh -o StrictHostKeyChecking=no root@$SERVER_IP << 'SETUP'
    apt-get update
    apt-get install -y ca-certificates curl gnupg
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" > /etc/apt/sources.list.d/docker.list
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    systemctl enable docker
    mkdir -p /opt/datatalk-sync
SETUP

  log "Docker installed!"
}

deploy() {
  # Auto-create server if it doesn't exist
  if ! hcloud server describe $SERVER_NAME >/dev/null 2>&1; then
    log "Server $SERVER_NAME not found, creating..."
    create_server
  fi

  SERVER_IP=$(hcloud server ip $SERVER_NAME)
  log "Deploying to $SERVER_IP..."

  # Check required vars (skip if just creating server)
  MISSING_VARS=0
  for var in N8N_USER N8N_PASSWORD N8N_ENCRYPTION_KEY WEBHOOK_URL OPENAI_API_KEY TELEGRAM_BOT_TOKEN SMTP_HOST; do
    if [ -z "${!var}" ]; then
      warn "Missing: $var"
      MISSING_VARS=1
    fi
  done

  if [ "$MISSING_VARS" -eq 1 ]; then
    log "Server created at $SERVER_IP but skipping app deploy (missing env vars)"
    log "Add vars to .env and run ./deploy.sh again"
    return
  fi

  # Create local .env for datatalk-sync
  cat > datatalk-sync/.env << EOF
N8N_USER=$N8N_USER
N8N_PASSWORD=$N8N_PASSWORD
N8N_ENCRYPTION_KEY=$N8N_ENCRYPTION_KEY
WEBHOOK_URL=$WEBHOOK_URL
OPENAI_API_KEY=$OPENAI_API_KEY
TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN
SMTP_HOST=$SMTP_HOST
SMTP_PORT=${SMTP_PORT:-587}
SMTP_USER=$SMTP_USER
SMTP_PASS=$SMTP_PASS
SMTP_SENDER=$SMTP_SENDER
EOF

  # Sync files
  log "Syncing files..."
  rsync -avz --delete \
    -e "ssh -o StrictHostKeyChecking=no" \
    datatalk-sync/ root@$SERVER_IP:/opt/datatalk-sync/

  # Deploy
  log "Starting containers..."
  ssh -o StrictHostKeyChecking=no root@$SERVER_IP << 'DEPLOY'
    cd /opt/datatalk-sync
    docker compose pull
    docker compose up -d
    docker compose ps
DEPLOY

  # Health check
  log "Health check..."
  sleep 10
  if curl -sf http://$SERVER_IP:5678/healthz >/dev/null 2>&1; then
    log "n8n is healthy!"
  else
    warn "n8n may still be starting..."
  fi

  echo ""
  log "Deployment complete!"
  echo "  URL: http://$SERVER_IP:5678"
  echo "  User: $N8N_USER"
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
    deploy
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
    echo "Usage: $0 [--create|--destroy|--status]"
    exit 1
    ;;
esac
