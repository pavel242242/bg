# 🚀 Quick Start Guide

Tento dokument obsahuje **nejrychlejší cestu** k deployment po implementaci.

## 1️⃣ SendGrid Setup (5 minut)

```bash
# 1. Registrace
open https://sendgrid.com

# 2. Vytvoř API Key
# Dashboard → Settings → API Keys → Create API Key
# Name: datatalk-smtp
# Permission: Mail Send (full access)
# Zkopíruj klíč (začíná SG.xxx...)

# 3. (Volitelné pro testing) Single Sender Verification
# Settings → Sender Authentication → Verify Single Sender
# Zadej svůj email → Ověř email
```

## 2️⃣ GitHub Secrets (3 minuty)

```bash
# Otevři GitHub repo secrets
open https://github.com/chocholous/bg/settings/secrets/actions

# Přidej tyto 3 NOVÉ secrets:
POSTGRES_PASSWORD=$(openssl rand -base64 32)
SENDGRID_API_KEY=SG.xxx...  # z kroku 1
SMTP_SENDER=noreply@yourdomain.com  # nebo verified email z kroku 1.3
SMTP_SENDER_DOMAIN=yourdomain.com  # nebo doména z verified emailu

# Zkontroluj, že máš ostatní secrets:
# ✅ N8N_USER
# ✅ N8N_PASSWORD
# ✅ N8N_ENCRYPTION_KEY
# ✅ WEBHOOK_URL
# ✅ OPENAI_API_KEY
# ✅ TELEGRAM_BOT_TOKEN
# ✅ HCLOUD_TOKEN
# ✅ DEPLOY_SSH_KEY
# ✅ DEPLOY_SSH_KEY_PUB
```

## 3️⃣ Deploy (1 minuta)

```bash
cd /Users/chocho/datamesh

# Option A: Lokální deploy (doporučeno pro první test)
./deploy.sh

# Option B: GitHub Actions deploy
git add .
git commit -m "feat: n8n as code + production SMTP"
git push origin claude/learn-n8n-skills-ZSXUn
```

## 4️⃣ Verifikace (2 minuty)

```bash
# 1. Získej IP serveru
SERVER_IP=$(hcloud server ip chochomesh)
echo "Server IP: $SERVER_IP"

# 2. Zkontroluj containery
ssh root@$SERVER_IP "cd /opt/datatalk-sync && docker compose ps"

# Očekávaný output:
# NAME                      STATUS
# datatalk-postgres         Up (healthy)
# datatalk-n8n              Up (healthy)
# datatalk-n8n-init         Exited (0)
# datatalk-n8n-post-init    Exited (0)

# 3. Zkontroluj logy
ssh root@$SERVER_IP "docker logs datatalk-n8n-post-init | tail -5"
# Měl by obsahovat: "Post-initialization complete!"

# 4. Test signup form
open http://$SERVER_IP:5678/form/datatalk-signup
```

## 5️⃣ Email Test (1 minuta)

```bash
# 1. Otevři signup form
open http://$SERVER_IP:5678/form/datatalk-signup

# 2. Zadej svůj email a submit

# 3. Zkontroluj inbox
# ✅ Email by měl dorazit do 30 sekund
# ⚠️ Pokud není ve inbox, zkontroluj spam

# 4. Zkontroluj SendGrid dashboard
open https://app.sendgrid.com/stats/overview
# Status by měl být: Delivered
```

---

## ⚡ Troubleshooting (pokud něco nefunguje)

### Problem: Init container failoval

```bash
ssh root@$SERVER_IP
cd /opt/datatalk-sync
docker logs datatalk-n8n-init

# Fix: Re-run init
docker compose up datatalk-n8n-init
```

### Problem: Post-init container failoval

```bash
docker logs datatalk-n8n-post-init

# Fix: Re-run post-init
docker compose up datatalk-n8n-post-init
```

### Problem: Email nedorazil

```bash
# 1. Zkontroluj n8n logy
docker logs datatalk-n8n --tail 50 | grep -i smtp

# 2. Zkontroluj SendGrid API key
docker exec -it datatalk-n8n env | grep SENDGRID

# 3. Test SMTP connection
docker exec -it datatalk-n8n wget -q --spider \
  --user=apikey \
  --password=$SENDGRID_API_KEY \
  smtp://smtp.sendgrid.net:587

# 4. Zkontroluj SendGrid dashboard
open https://app.sendgrid.com/stats/overview
# Pokud tam nic není, email se vůbec neposlal (zkontroluj credentials v n8n)
```

### Problem: "Credential not found" v n8n

```bash
# SMTP credential nebyl vytvořen - re-run post-init
docker compose up datatalk-n8n-post-init

# Nebo vytvořit manuálně v n8n UI:
open http://$SERVER_IP:5678
# → Credentials → Add Credential → SMTP
# Name: SMTP (PŘESNĚ!)
# Host: smtp.sendgrid.net
# Port: 587
# User: apikey
# Password: <SENDGRID_API_KEY>
```

---

## 📚 Další Kroky

Po úspěšném testu:

1. **DNS Setup** (pokud máš doménu):
   ```bash
   cat datatalk-sync/docs/DNS-SETUP.md
   ```

2. **HTTPS Setup**:
   - Doporučeno: Caddy nebo Nginx + Let's Encrypt
   - Nebo použít Cloudflare pro SSL

3. **Monitoring**:
   - Uptime Robot: https://uptimerobot.com/
   - Endpoint: `http://$SERVER_IP:5678/healthz`

4. **Backup**:
   ```bash
   # Cron job na serveru
   0 2 * * * docker exec datatalk-postgres pg_dump -U n8n n8n | gzip > /opt/backups/n8n_$(date +\%Y\%m\%d).sql.gz
   ```

---

**Total Time:** ~12 minut od začátku do funkčního systému! 🎉

Pro kompletní dokumentaci viz: `IMPLEMENTATION-COMPLETE.md`
