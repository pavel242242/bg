# Environment Configuration Template
# Generated from .env.example - secrets stored in 1Password
# Usage: op inject -i .env.tpl -o .env

# === N8N Configuration ===
N8N_USER="admin@datatalk.local"
N8N_PASSWORD="op://gh-projects/chocholous__bg__datatalk-sync__env.example/n8n_password"
N8N_ENCRYPTION_KEY="op://gh-projects/chocholous__bg__datatalk-sync__env.example/n8n_encryption_key"

# Webhook URL (public)
WEBHOOK_URL="https://n8n.yourdomain.com"

# === Database ===
POSTGRES_PASSWORD="op://gh-projects/chocholous__bg__datatalk-sync__env.example/postgres_password"

# === External Services ===
OPENAI_API_KEY="op://gh-projects/chocholous__bg__datatalk-sync__env.example/openai_api_key"
TELEGRAM_BOT_TOKEN="op://gh-projects/chocholous__bg__datatalk-sync__env.example/telegram_bot_token"

# === SMTP (SendGrid) ===
SENDGRID_API_KEY="op://gh-projects/chocholous__bg__datatalk-sync__env.example/sendgrid_api_key"
SMTP_SENDER="noreply@yourdomain.com"
SMTP_SENDER_DOMAIN="yourdomain.com"

# === Deployment (Hetzner Cloud) ===
HCLOUD_TOKEN="op://gh-projects/chocholous__bg__datatalk-sync__env.example/hcloud_token"
DEPLOY_SSH_KEY="op://gh-projects/chocholous__bg__datatalk-sync__env.example/deploy_ssh_key"
DEPLOY_SSH_KEY_PUB="op://gh-projects/chocholous__bg__datatalk-sync__env.example/deploy_ssh_key_pub"
