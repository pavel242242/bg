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

  # Generate cloud-init with embedded secrets
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  CLOUD_INIT_TEMPLATE="$SCRIPT_DIR/cloud-init.yml"
  CLOUD_INIT_GENERATED="/tmp/cloud-init-generated.yml"

  if [ ! -f "$CLOUD_INIT_TEMPLATE" ]; then
    error "cloud-init.yml not found at $CLOUD_INIT_TEMPLATE"
  fi

  # Create .env content
  ENV_CONTENT="N8N_USER=${N8N_USER:-admin}
N8N_PASSWORD=${N8N_PASSWORD:-changeme}
N8N_ENCRYPTION_KEY=${N8N_ENCRYPTION_KEY:-$(openssl rand -hex 16)}
WEBHOOK_URL=${WEBHOOK_URL:-}
OPENAI_API_KEY=${OPENAI_API_KEY:-}
TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN:-}
SMTP_HOST=${SMTP_HOST:-}
SMTP_PORT=${SMTP_PORT:-587}
SMTP_USER=${SMTP_USER:-}
SMTP_PASS=${SMTP_PASS:-}
SMTP_SENDER=${SMTP_SENDER:-}"

  # Generate cloud-init with embedded .env
  cat > "$CLOUD_INIT_GENERATED" << CLOUD_INIT_EOF
#cloud-config

package_update: true
package_upgrade: true

packages:
  - ca-certificates
  - curl
  - gnupg
  - git

write_files:
  - path: /opt/datatalk-sync/.env
    content: |
$(echo "$ENV_CONTENT" | sed 's/^/      /')
    owner: root:root
    permissions: '0600'

runcmd:
  # Install Docker
  - install -m 0755 -d /etc/apt/keyrings
  - curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  - chmod a+r /etc/apt/keyrings/docker.gpg
  - echo "deb [arch=\$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \$(. /etc/os-release && echo \$VERSION_CODENAME) stable" > /etc/apt/sources.list.d/docker.list
  - apt-get update
  - apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
  - systemctl enable docker
  - systemctl start docker
  # Clone repo and deploy (use the branch with datatalk-sync)
  - git clone -b claude/learn-n8n-skills-ZSXUn https://github.com/chocholous/bg.git /opt/bg
  - cp -r /opt/bg/datatalk-sync/* /opt/datatalk-sync/
  # Patch docker-compose to allow HTTP (no secure cookie)
  - sed -i '/N8N_PROTOCOL/a\      - N8N_SECURE_COOKIE=false' /opt/datatalk-sync/docker-compose.yml
  # Start n8n
  - cd /opt/datatalk-sync && docker compose up -d
  # Web terminal via Docker (port 7681)
  - docker run -d --name ttyd --restart unless-stopped -p 7681:7681 -v /opt:/opt -v /var/log:/var/log tsl0922/ttyd:latest ttyd -W bash
  # Signal ready
  - touch /opt/.cloud-init-complete
CLOUD_INIT_EOF

  log "Generated cloud-init with embedded config"

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

deploy() {
  # Auto-create server if it doesn't exist
  if ! hcloud server describe $SERVER_NAME >/dev/null 2>&1; then
    log "Server $SERVER_NAME not found, creating..."
    create_server
  fi

  SERVER_IP=$(hcloud server ip $SERVER_NAME)
  log "Deploying to $SERVER_IP..."

  # Check required vars (minimum to start n8n)
  MISSING_REQUIRED=0
  for var in N8N_USER N8N_PASSWORD N8N_ENCRYPTION_KEY; do
    if [ -z "${!var}" ]; then
      warn "Required: $var"
      MISSING_REQUIRED=1
    fi
  done

  if [ "$MISSING_REQUIRED" -eq 1 ]; then
    log "Server created at $SERVER_IP but skipping app deploy (missing required env vars)"
    log "Add vars to .env and run ./deploy.sh again"
    return
  fi

  # Warn about optional vars
  for var in WEBHOOK_URL OPENAI_API_KEY TELEGRAM_BOT_TOKEN SMTP_HOST; do
    if [ -z "${!var}" ]; then
      warn "Optional missing: $var (some features won't work)"
    fi
  done

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
