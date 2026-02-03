# Infrastructure Deployment

Hetzner Cloud deployment configuration and scripts for DataTalk Event Sync.

## Prerequisites

- Hetzner Cloud account
- `hcloud` CLI installed and configured
- 1Password CLI for secrets management

## Setup

### 1. Configure Secrets

Generate .env from 1Password template:

```bash
op inject -i .env.tpl -o .env
```

Required secrets:
- `HCLOUD_TOKEN` - Hetzner Cloud API token
- `DEPLOY_SSH_KEY` - SSH private key for server access
- `DEPLOY_SSH_KEY_PUB` - SSH public key

### 2. Deploy to Hetzner Cloud

```bash
./deploy.sh
```

This will:
- Create a new Hetzner Cloud server
- Install Docker and Docker Compose
- Deploy the n8n application
- Configure SSL certificates (if WEBHOOK_URL is set)

## Scripts

- **deploy.sh** - Main deployment script
- **cloud-init.yml** - Server initialization configuration
- **create-smtp-*.sh** - SMTP credential setup scripts

## Configuration

Edit `cloud-init.yml` to customize:
- Server specifications
- Docker version
- Startup services

## Troubleshooting

### SSH Connection Issues

```bash
# Check server status
hcloud server list

# SSH to server
ssh root@<server-ip>
```

### Deployment Logs

```bash
# On the server
journalctl -u cloud-final -b
```

## Security

**Never commit .env files!** All secrets are managed via 1Password and injected at runtime.
