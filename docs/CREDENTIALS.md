# Credentials & Secrets

## Přehled

| Proměnná | Povinná | Popis |
|----------|---------|-------|
| N8N_USER | ✅ | Login do n8n UI |
| N8N_PASSWORD | ✅ | Heslo do n8n UI |
| N8N_ENCRYPTION_KEY | ✅ | Šifrování credentials v n8n |
| WEBHOOK_URL | ⚠️ | URL pro webhooky (nutné pro produkci) |
| OPENAI_API_KEY | ⚠️ | OpenAI API pro LLM extrakci |
| TELEGRAM_BOT_TOKEN | ⚠️ | Telegram bot pro notifikace |
| SMTP_* | ⚠️ | Email notifikace |
| HCLOUD_TOKEN | 🔧 | Pouze pro deploy script |

✅ = povinné, ⚠️ = potřebné pro plnou funkcionalitu, 🔧 = deploy only

---

## n8n Authentication

### N8N_USER
```
Popis: Uživatelské jméno pro přihlášení do n8n web UI
Formát: string (bez speciálních znaků)
Příklad: admin
Default: admin
```

### N8N_PASSWORD
```
Popis: Heslo pro přihlášení do n8n web UI
Formát: string (min. 8 znaků, doporučeno 16+)
Příklad: SecureP@ssw0rd2026!
Default: changeme (ZMĚNIT!)
```

**Generování silného hesla:**
```bash
openssl rand -base64 24
```

### N8N_ENCRYPTION_KEY
```
Popis: Klíč pro šifrování uložených credentials v n8n
Formát: hex string (32 znaků = 128-bit)
Příklad: a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6
```

**Generování:**
```bash
openssl rand -hex 16
```

**⚠️ DŮLEŽITÉ:**
- Tento klíč NELZE změnit po uložení credentials
- Pokud se ztratí, všechny credentials budou nečitelné
- Bezpečně zálohuj!

---

## Webhook Configuration

### WEBHOOK_URL
```
Popis: Veřejná URL pro příjem webhooků
Formát: https://domain.com (bez trailing slash)
Příklad: https://n8n.example.com
```

**Použití:**
- Verifikační linky v emailech
- Telegram bot webhook
- Externí integrace

**Development:**
```bash
# Lokálně
WEBHOOK_URL=http://localhost:5678

# S ngrok
ngrok http 5678
WEBHOOK_URL=https://abc123.ngrok.io
```

**Produkce:**
```bash
# S vlastní doménou + Caddy/nginx
WEBHOOK_URL=https://n8n.yourdomain.com
```

---

## OpenAI API

### OPENAI_API_KEY
```
Popis: API klíč pro OpenAI (GPT-4 pro extrakci)
Formát: sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Získání: https://platform.openai.com/api-keys
```

**Doporučené nastavení v OpenAI:**
- Billing: Nastav spending limit
- Usage: Monitor v dashboardu
- Model: gpt-4-turbo (cost-effective pro extrakci)

**Odhadované náklady:**
- ~$0.01-0.05 za scrape (záleží na počtu eventů)
- ~$1-5/měsíc při weekly schedule

---

## Telegram Bot

### TELEGRAM_BOT_TOKEN
```
Popis: Token pro Telegram bota
Formát: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz
Získání: @BotFather na Telegramu
```

**Vytvoření bota:**
1. Otevři @BotFather v Telegramu
2. `/newbot`
3. Zadej jméno bota
4. Zadej username (musí končit `bot`)
5. Zkopíruj token

**Nastavení webhooků:**
```bash
# Automaticky v n8n workflow, nebo manuálně:
curl "https://api.telegram.org/bot<TOKEN>/setWebhook?url=<WEBHOOK_URL>/webhook/telegram"
```

---

## SMTP (Email)

### SMTP_HOST
```
Popis: SMTP server hostname
Příklady:
  - smtp.sendgrid.net (SendGrid)
  - smtp.mailgun.org (Mailgun)
  - smtp.gmail.com (Gmail - nedoporučeno pro produkci)
```

### SMTP_PORT
```
Popis: SMTP port
Hodnoty:
  - 587 (TLS, doporučeno)
  - 465 (SSL)
  - 25 (nezabezpečené, nedoporučeno)
Default: 587
```

### SMTP_USER
```
Popis: SMTP autentizační uživatel
Příklad: apikey (SendGrid), postmaster@domain (Mailgun)
```

### SMTP_PASS
```
Popis: SMTP heslo nebo API klíč
Příklad: SG.xxxxx (SendGrid API key)
```

### SMTP_SENDER
```
Popis: Email adresa odesílatele
Formát: email@domain.com nebo "Name <email@domain.com>"
Příklad: events@datatalk.cz
```

**Doporučení pro produkci:**
1. **SendGrid** - Free tier 100 emails/den
2. **Mailgun** - Free tier 5000 emails/měsíc
3. **Amazon SES** - Nejlevnější pro vysoký objem

**⚠️ Spam prevence:**
- Nastav SPF, DKIM, DMARC záznamy
- Používej ověřenou doménu
- Začni s nízkým objemem

---

## Hetzner Cloud (Deploy only)

### HCLOUD_TOKEN
```
Popis: API token pro Hetzner Cloud
Formát: 64 znaků hexadecimální
Získání: https://console.hetzner.cloud → Project → Security → API Tokens
```

**Oprávnění:** Read & Write

**Použití:** Pouze v `deploy.sh`, není potřeba v n8n.

---

## Soubory s credentials

### .env (datatalk-sync/)
```bash
# === POVINNÉ ===
N8N_USER=admin
N8N_PASSWORD=your-secure-password
N8N_ENCRYPTION_KEY=abcdef1234567890

# === PRO PLNOU FUNKCIONALITU ===
WEBHOOK_URL=https://your-domain.com
OPENAI_API_KEY=sk-xxxxx
TELEGRAM_BOT_TOKEN=123456:ABCxxx

# === SMTP ===
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASS=SG.xxxxx
SMTP_SENDER=events@yourdomain.com
```

### .env (root - deploy only)
```bash
HCLOUD_TOKEN=your-hetzner-token
```

---

## Bezpečnostní doporučení

1. **Nikdy necommituj .env soubory**
   ```bash
   # .gitignore obsahuje:
   .env
   *.env
   .env.*
   !.env.example
   ```

2. **Používej secret management v produkci**
   - HashiCorp Vault
   - AWS Secrets Manager
   - Doppler

3. **Rotuj credentials pravidelně**
   - API klíče: každé 3 měsíce
   - Hesla: při podezření na kompromitaci

4. **Audituj přístupy**
   - Loguj použití API klíčů
   - Monitoruj neobvyklou aktivitu
