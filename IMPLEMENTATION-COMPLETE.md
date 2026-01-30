# ✅ N8N As Code + Production SMTP - Implementace Dokončena

## Co bylo implementováno

Všech **8 fází** z implementačního plánu bylo úspěšně dokončeno:

### ✅ FÁZE 1: PostgreSQL Migrace
- Přidán PostgreSQL 16 Alpine container
- N8N nakonfigurován pro použití PostgreSQL místo SQLite
- SMTP změněn na přímé SendGrid připojení (smtp.sendgrid.net:587)
- Přidány Docker networks a healthchecks

**Soubory změněny:**
- `datatalk-sync/docker-compose.yml`

### ✅ FÁZE 2: Init Container
- Vytvořen `scripts/n8n-init.sh` pro automatický import workflows při startu
- Přidán `n8n-init` service do Docker Compose
- Workflows se automaticky importují z `/workflows/*.json` při každém restartu

**Soubory vytvořeny:**
- `datatalk-sync/scripts/n8n-init.sh` (executable)

**Soubory změněny:**
- `datatalk-sync/docker-compose.yml`

### ✅ FÁZE 3: Post-Init Container
- Vytvořen `scripts/n8n-post-init.sh` pro automatické vytvoření SMTP credentials
- Automatická aktivace všech workflows přes n8n API
- Přidán `n8n-post-init` service do Docker Compose

**Soubory vytvořeny:**
- `datatalk-sync/scripts/n8n-post-init.sh` (executable)

**Soubory změněny:**
- `datatalk-sync/docker-compose.yml`

### ✅ FÁZE 4: Environment Variables
- Aktualizován `.env.example` s novými proměnnými:
  - `POSTGRES_PASSWORD`
  - `SENDGRID_API_KEY`
  - `SMTP_SENDER`
  - `SMTP_SENDER_DOMAIN`
- GitHub Actions aktualizováno pro použití nových secrets

**Soubory změněny:**
- `datatalk-sync/.env.example`
- `.github/workflows/deploy.yml`

### ✅ FÁZE 5: Cloud-Init Update
- Přidán git clone specifického branch: `claude/learn-n8n-skills-ZSXUn`
- Automatický chmod pro executable skripty
- Wait loop pro verifikaci úspěšné inicializace
- Logování init containerů

**Soubory změněny:**
- `cloud-init.yml`

### ✅ FÁZE 6: Workflow JSON Cleanup
- Odstraněny hardcoded credential IDs z workflows
- Ponechány pouze credential names (n8n je najde automaticky)

**Soubory změněny:**
- `datatalk-sync/workflows/01-subscriber-signup.json`
- `datatalk-sync/workflows/04-event-scraper.json`

### ✅ FÁZE 7: DNS Setup Dokumentace
- Vytvořen kompletní průvodce nastavením DNS pro SendGrid
- SPF, DKIM, DMARC konfigurace
- Troubleshooting guide
- Verifikační checklist

**Soubory vytvořeny:**
- `datatalk-sync/docs/DNS-SETUP.md`

### ✅ FÁZE 8: Deploy Script Update
- Přidány nové env vars do deploy.sh
- Aktualizován required/optional vars check
- Přidán wait for initialization loop
- Automatický chmod pro skripty při deploy

**Soubory změněny:**
- `deploy.sh`

---

## 🚀 Další Kroky

### 1. GitHub Secrets Setup (KRITICKÉ!)

Před prvním deploy je nutné nastavit GitHub Secrets v repozitáři:

**Jít na:** `https://github.com/chocholous/bg/settings/secrets/actions`

**Přidat tyto secrets:**

```bash
# Existující (zkontrolovat, že jsou nastavené)
N8N_USER=admin
N8N_PASSWORD=<silné heslo>
N8N_ENCRYPTION_KEY=<openssl rand -hex 32>
WEBHOOK_URL=https://n8n.yourdomain.com  # nebo http://SERVER_IP:5678
OPENAI_API_KEY=<z OpenAI dashboardu>
TELEGRAM_BOT_TOKEN=<z BotFather>
HCLOUD_TOKEN=<z Hetzner Cloud>
DEPLOY_SSH_KEY=<SSH private key>
DEPLOY_SSH_KEY_PUB=<SSH public key>

# NOVÉ (nutno přidat)
POSTGRES_PASSWORD=<vygenerovat: openssl rand -base64 32>
SENDGRID_API_KEY=SG.xxxxx...  # z SendGrid dashboardu
SMTP_SENDER=noreply@yourdomain.com  # nebo dočasně noreply@localhost
SMTP_SENDER_DOMAIN=yourdomain.com  # nebo dočasně localhost
```

### 2. SendGrid Account Setup

1. **Registrace:** https://sendgrid.com
2. **API Key:**
   - Settings → API Keys → Create API Key
   - Name: `datatalk-smtp-relay`
   - Permission: **Mail Send** (full access)
   - Zkopírovat API key (začíná `SG.`)
   - Uložit do GitHub Secrets jako `SENDGRID_API_KEY`

3. **Single Sender Verification** (pro testing - pokud ještě nemáš doménu):
   - Settings → Sender Authentication → Verify Single Sender
   - Zadat svůj email
   - Ověřit potvrzovací email
   - Použít tento email jako `SMTP_SENDER`

### 3. Testovací Deploy

Po nastavení všech secrets:

```bash
# Lokální test (doporučeno)
cd /Users/chocho/datamesh
./deploy.sh

# Nebo push do branch (GitHub Actions)
git add .
git commit -m "feat: implement n8n as code + production SMTP

- PostgreSQL persistence
- Auto workflow import on restart
- SendGrid SMTP integration
- Init containers for automation

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
git push origin claude/learn-n8n-skills-ZSXUn
```

### 4. Verifikace Po Deploy

Po úspěšném deploy zkontrolovat:

#### A. Container Status
```bash
ssh root@SERVER_IP
cd /opt/datatalk-sync

# Všechny containery běží?
docker compose ps

# Očekávaný output:
# datatalk-postgres      Up (healthy)
# datatalk-n8n           Up (healthy)
# datatalk-n8n-init      Exited (0)
# datatalk-n8n-post-init Exited (0)

# Zkontrolovat logy
docker logs datatalk-n8n-init | tail -20
docker logs datatalk-n8n-post-init | tail -20
```

#### B. Workflows Imported?
```bash
# Otevřít n8n UI
open http://SERVER_IP:5678

# Nebo přes API
curl -u admin:password http://SERVER_IP:5678/api/v1/workflows | jq '.data[] | {name: .name, active: .active}'

# Očekáváno:
# - 4 workflows
# - Všechny active: true
```

#### C. SMTP Credentials Created?
```bash
curl -u admin:password http://SERVER_IP:5678/api/v1/credentials | jq '.data[] | {name: .name, type: .type}'

# Očekáváno:
# {
#   "name": "SMTP",
#   "type": "smtp"
# }
```

#### D. PostgreSQL Data
```bash
docker exec -it datatalk-postgres psql -U n8n -d n8n

# V psql konzoli:
\dt
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
\q

# Očekáváno:
# - n8n systémové tabulky (workflows, credentials, ...)
# - n8n Tables: subscribers, events (pokud již existují)
```

#### E. Test Signup Form
```bash
curl http://SERVER_IP:5678/form/datatalk-signup

# Měl by vrátit HTML signup form

# Nebo otevřít v prohlížeči:
open http://SERVER_IP:5678/form/datatalk-signup
```

### 5. DNS Setup (Když máš doménu)

Po získání domény následovat průvodce:

```bash
cat datatalk-sync/docs/DNS-SETUP.md
```

**Klíčové kroky:**
1. Domain Authentication v SendGrid dashboardu
2. Přidat SPF, DKIM, DMARC DNS záznamy
3. Počkat 24-48h na propagaci
4. Verifikovat pomocí mxtoolbox.com
5. Aktualizovat `SMTP_SENDER` a `SMTP_SENDER_DOMAIN` v GitHub Secrets
6. Re-deploy

### 6. Monitoring & Maintenance

#### Doporučené monitorování:

- **Uptime Robot:** https://uptimerobot.com/
  - Endpoint: `http://SERVER_IP:5678/healthz`
  - Interval: 5 minut

- **SendGrid Dashboard:** https://app.sendgrid.com/statistics
  - Sledovat: Deliverability, Bounce Rate (<5%), Spam Reports

- **PostgreSQL Backup:**
```bash
# Cron job na serveru (každý den 2:00)
0 2 * * * docker exec datatalk-postgres pg_dump -U n8n n8n | gzip > /opt/backups/n8n_$(date +\%Y\%m\%d).sql.gz
```

#### Rotace API Keys:
- SendGrid API key rotovat každých **90 dní**
- N8N_ENCRYPTION_KEY **NIKDY** neměnit (ztráta dat!)

---

## 📋 Checklist před Produkcí

- [ ] Všechny GitHub Secrets nastaveny (12 secrets)
- [ ] SendGrid účet vytvořen a API key získán
- [ ] Testovací deploy proběhl úspěšně
- [ ] Všechny 4 containery běží správně
- [ ] Workflows jsou importované a aktivní
- [ ] SMTP credentials vytvořeny v n8n
- [ ] PostgreSQL obsahuje správná data
- [ ] Signup form je přístupný a funguje
- [ ] (Volitelné) Doména získána a DNS nastaveno
- [ ] (Volitelné) Email test prošel (mail-tester.com score >8)
- [ ] (Doporučeno) Monitoring nastaven (Uptime Robot)
- [ ] (Doporučeno) Backup cron job nakonfigurován

---

## 🐛 Troubleshooting

### Problem: Init container failuje

**Diagnóza:**
```bash
docker logs datatalk-n8n-init

# Možné příčiny:
# - PostgreSQL není ready
# - Workflows JSON jsou invalid
# - N8N_ENCRYPTION_KEY chybí
```

**Fix:**
```bash
# Re-run init container
docker compose up datatalk-n8n-init

# Nebo manuální import
docker exec -it datatalk-n8n n8n import:workflow --input=/workflows/01-subscriber-signup.json
```

### Problem: Post-init container failuje

**Diagnóza:**
```bash
docker logs datatalk-n8n-post-init

# Možné příčiny:
# - N8n API ještě není ready
# - N8N_USER/PASSWORD nesprávné
# - SENDGRID_API_KEY chybí
```

**Fix:**
```bash
# Re-run post-init
docker compose up datatalk-n8n-post-init

# Nebo vytvořit credentials manuálně v n8n UI
```

### Problem: PostgreSQL connection error

**Diagnóza:**
```bash
docker logs datatalk-postgres
docker logs datatalk-n8n | grep -i postgres

# Možné příčiny:
# - POSTGRES_PASSWORD nesprávné
# - Postgres container není healthy
```

**Fix:**
```bash
# Zkontrolovat healthcheck
docker inspect datatalk-postgres | jq '.[0].State.Health'

# Zkontrolovat logs
docker logs datatalk-postgres --tail 50
```

### Problem: Workflows nejsou aktivní

**Možné příčiny:**
- Post-init container nestihl doběhnout
- API timeout při aktivaci

**Fix:**
```bash
# Re-run post-init
docker compose up datatalk-n8n-post-init

# Nebo manuálně v n8n UI aktivovat workflows
```

---

## 📚 Dokumentace

- **DNS Setup:** `datatalk-sync/docs/DNS-SETUP.md`
- **Implementační Plán:** Původní dokument v `plan.md` (pokud existuje)
- **Docker Compose:** `datatalk-sync/docker-compose.yml`
- **Deploy Script:** `deploy.sh`
- **GitHub Actions:** `.github/workflows/deploy.yml`

---

## 🎉 Co Dalšího?

Po úspěšném testovacím deploy:

1. **Získat produkční doménu** (doporučeno: `.events`, `.app`, nebo `.io`)
2. **Nastavit HTTPS** pomocí Caddy nebo Nginx + Let's Encrypt
3. **Merge do main** branch pro produkční deployment
4. **Monitorovat SendGrid statistics** první týden
5. **Warm-up period:** První týden posílat max 50 emailů/den
6. **Nastavit DMARC monitoring** pro sledování authentication failures

---

**Implementováno:** 2026-01-30
**Status:** ✅ Připraveno k testování
**Next Step:** Nastavit GitHub Secrets a spustit testovací deploy
