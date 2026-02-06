# Deployment Guide

## Prostředí

### Development (lokální)

```bash
cd datatalk-sync

# Vytvoř .env ze šablony
cp .env.example .env

# Vyplň minimální konfiguraci
N8N_USER=admin
N8N_PASSWORD=devpassword123
N8N_ENCRYPTION_KEY=$(openssl rand -hex 16)

# Spusť
docker compose up -d

# Přístup
open http://localhost:5678
```

**Dev specifika:**
- `N8N_SECURE_COOKIE=false` (HTTP přístup)
- Workflows se ukládají do Docker volume `n8n_data`
- Bez SMTP - emaily se logují do konzole

### Production (Hetzner Cloud)

```bash
# Prerekvizity
export HCLOUD_TOKEN="your-hetzner-token"

# Vyplň produkční .env
cp .env.example .env
nano .env  # Viz CREDENTIALS.md

# Deploy
./deploy.sh
```

**Server:**
- Typ: `cax11` (ARM64, 2 vCPU, 4GB RAM)
- Lokace: `nbg1` (Nuremberg, DE)
- OS: Ubuntu 24.04
- Cena: ~€3.29/měsíc

**Přístupové body:**
| Služba | URL | Popis |
|--------|-----|-------|
| n8n | http://IP:5678 | Workflow editor |
| ttyd | http://IP:7681 | Web shell |
| SSH | IP:22 | Root přístup |

## Produkční checklist

### Bezpečnost

- [ ] **HTTPS/TLS** - Přidat Caddy nebo nginx reverse proxy
- [ ] **Firewall** - Omezit přístup k portům 7681 (ttyd)
- [ ] **Silná hesla** - N8N_PASSWORD min. 16 znaků
- [ ] **Rotace klíčů** - N8N_ENCRYPTION_KEY backup

### Konfigurace

- [ ] **WEBHOOK_URL** - Veřejná URL pro n8n webhooky
- [ ] **SMTP** - Produkční email provider (SendGrid, Mailgun)
- [ ] **OpenAI API** - Platný API klíč s limity
- [ ] **Telegram Bot** - Produkční bot token

### Monitoring

- [ ] **Healthcheck** - `/healthz` endpoint monitoring
- [ ] **Logy** - Centralizované logování (Loki, etc.)
- [ ] **Alerting** - Notifikace při výpadku
- [ ] **Backup** - Automatický backup n8n_data volume

### Škálování

- [ ] **Rate limiting** - Pro webhook endpointy
- [ ] **Queue** - Pro velký objem emailů
- [ ] **CDN** - Pro statický obsah (volitelné)

## Cloud-init proces

Při vytvoření serveru se automaticky:

1. **Aktualizace systému** - `apt-get update && upgrade`
2. **Instalace Docker** - Docker CE + docker-compose-plugin
3. **Klonování repo** - Z GitHub branch `claude/learn-n8n-skills-ZSXUn`
4. **Vytvoření .env** - S embedded secrets z deploy scriptu
5. **Patch konfigurace** - Přidání `N8N_SECURE_COOKIE=false`
6. **Start n8n** - `docker compose up -d`
7. **Start ttyd** - Web terminal na portu 7681

Čas: ~3-5 minut

## Troubleshooting

### n8n nereaguje

```bash
# V ttyd (http://IP:7681) nebo SSH
docker ps -a
docker logs datatalk-n8n
docker compose -f /opt/datatalk-sync/docker-compose.yml restart
```

### Secure cookie error

Přidej do docker-compose.yml:
```yaml
- N8N_SECURE_COOKIE=false
```

Nebo nastav HTTPS (doporučeno pro produkci).

### Cloud-init selhal

```bash
# Kontrola logu
cat /var/log/cloud-init-output.log

# Ruční restart
cd /opt/datatalk-sync
docker compose down
docker compose up -d
```

## Aktualizace

```bash
# V ttyd nebo SSH
cd /opt/bg
git pull origin claude/learn-n8n-skills-ZSXUn
cp -r datatalk-sync/* /opt/datatalk-sync/
cd /opt/datatalk-sync
docker compose pull
docker compose up -d
```
