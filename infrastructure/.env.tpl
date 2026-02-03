# Infrastructure Environment Configuration
# Deployment secrets for Hetzner Cloud
# Usage: op inject -i .env.tpl -o .env

# === Hetzner Cloud ===
HCLOUD_TOKEN="op://gh-projects/chocholous__bg__infrastructure/hcloud_token"

# === SSH Deployment Keys ===
DEPLOY_SSH_KEY="op://gh-projects/chocholous__bg__infrastructure/deploy_ssh_key"
DEPLOY_SSH_KEY_PUB="op://gh-projects/chocholous__bg__infrastructure/deploy_ssh_key_pub"
