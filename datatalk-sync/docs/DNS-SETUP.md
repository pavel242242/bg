# DNS Setup pro SendGrid Email Delivery

Tento dokument popisuje, jak nastavit DNS záznamy pro SendGrid, aby emaily z n8n pracovního prostředí nedopadaly do spamu.

## Prerequisity

- ✅ SendGrid účet vytvořen
- ✅ SendGrid API key vygenerován (začíná `SG.`)
- ✅ Doména k dispozici (např. `datatalk.events` nebo `mail.chocholous.cz`)

## Kroky

### 1. SendGrid Domain Authentication

1. Přihlásit se do [SendGrid Dashboard](https://app.sendgrid.com)
2. Jít na **Settings** → **Sender Authentication**
3. Kliknout na **Authenticate Your Domain**
4. Vybrat DNS provider (např. Cloudflare, Route53, GoDaddy...)
5. Zadat vaši doménu

SendGrid vygeneruje DNS záznamy, které je třeba přidat do vaší domény.

### 2. DNS Záznamy

Přidat následující záznamy do DNS správy vaší domény:

#### A. SPF Record (Sender Policy Framework)

**Účel**: Specifikuje, které servery mohou posílat emaily z vaší domény.

```
Type:  TXT
Name:  @ (nebo subdoména, např. mail)
Value: v=spf1 include:sendgrid.net ~all
TTL:   3600
```

**Vysvětlení**:
- `v=spf1` - verze SPF
- `include:sendgrid.net` - povoluje SendGrid servery
- `~all` - soft fail pro ostatní (doporučeno pro produkci)

#### B. DKIM Records (DomainKeys Identified Mail)

**Účel**: Kryptografický podpis ověřující, že email nebyl změněn.

SendGrid poskytne 2 CNAME záznamy (hodnoty se liší podle účtu):

```
Type:  CNAME
Name:  s1._domainkey
Value: s1.domainkey.u12345678.wl.sendgrid.net
TTL:   3600

Type:  CNAME
Name:  s2._domainkey
Value: s2.domainkey.u12345678.wl.sendgrid.net
TTL:   3600
```

**⚠️ Důležité**: Hodnoty `u12345678` jsou ukázkové - použijte hodnoty z SendGrid dashboardu!

#### C. DMARC Record (Domain-based Message Authentication)

**Účel**: Definuje, co má příjemce dělat s emaily, které neprošly SPF/DKIM.

```
Type:  TXT
Name:  _dmarc
Value: v=DMARC1; p=none; rua=mailto:dmarc@yourdomain.com
TTL:   3600
```

**Vysvětlení**:
- `p=none` - jen monitorovat, nezavrhovat (pro start doporučeno)
- `p=quarantine` - posílat do spamu (použít po testování)
- `p=reject` - odmítnout (nejpřísnější, použít až jste si jisti)
- `rua=mailto:...` - kam posílat DMARC reporty

#### D. (Volitelné) Subdoména pro emaily

Pokud nechcete použít hlavní doménu, vytvořte subdoménu:

```
Type:  A nebo CNAME
Name:  mail
Value: <IP serveru nebo CNAME na SendGrid>
TTL:   3600
```

A všechny výše uvedené záznamy pak vytvořte s prefixem `mail.`:
- `mail` místo `@` pro SPF
- `s1._domainkey.mail` místo `s1._domainkey` pro DKIM
- `_dmarc.mail` místo `_dmarc` pro DMARC

### 3. Verifikace DNS

Po přidání záznamů počkat **24-48 hodin** na DNS propagaci.

#### Automatická verifikace v SendGrid

1. SendGrid dashboard → Sender Authentication
2. Kliknout na **Verify** u vaší domény
3. Pokud vše proběhlo OK, uvidíte zelené checkmarky

#### Manuální verifikace

Použít online nástroje:

1. **SPF Check**:
   - https://mxtoolbox.com/spf.aspx
   - Zadat doménu, zkontrolovat, že obsahuje `include:sendgrid.net`

2. **DKIM Check**:
   - https://mxtoolbox.com/dkim.aspx
   - Zadat `s1._domainkey.yourdomain.com`
   - Zkontrolovat, že CNAME vrací SendGrid hodnotu

3. **DMARC Check**:
   - https://dmarcian.com/dmarc-inspector/
   - Zadat doménu
   - Zkontrolovat, že policy je nastavená

4. **Full Email Test**:
   - https://www.mail-tester.com/
   - Poslat testovací email z n8n na vygenerovanou adresu
   - **Target score: 8/10 nebo víc**

### 4. Aktualizace .env

Po nastavení DNS upravit `.env` soubor:

```bash
# Změnit z placeholder hodnot na skutečné:
SMTP_SENDER=noreply@yourdomain.com
SMTP_SENDER_DOMAIN=yourdomain.com
```

A znovu deployovat:

```bash
./deploy.sh
```

### 5. Testování

#### Test 1: N8N Signup Form

1. Otevřít: `http://SERVER_IP:5678/form/datatalk-signup`
2. Zadat testovací email (Gmail, Outlook, Seznam...)
3. Zkontrolovat:
   - ✅ Email dorazil
   - ✅ Není ve spamu
   - ✅ Verification link funguje

#### Test 2: SendGrid Dashboard

1. SendGrid → **Activity**
2. Zkontrolovat poslední email:
   - Status: **Delivered**
   - SPF: **Pass**
   - DKIM: **Pass**
   - Open/Click tracking (pokud povoleno)

#### Test 3: Email Headers

Otevřít přijatý email → Show original/View headers → hledat:

```
spf=pass
dkim=pass
dmarc=pass
```

## Troubleshooting

### Problem: DNS záznamy se neaktualizují

**Řešení**:
```bash
# Linux/Mac - zkontrolovat DNS
dig TXT yourdomain.com
dig TXT _dmarc.yourdomain.com
dig CNAME s1._domainkey.yourdomain.com

# Nebo použít online nástroj:
# https://dnschecker.org/
```

Počkat 24-48h. DNS propagace trvá.

### Problem: SendGrid neověřil doménu

**Možné příčiny**:
1. DNS záznamy ještě nejsou propagované (počkat)
2. Špatně zkopírované hodnoty (zkontrolovat překlepy)
3. TTL je příliš dlouhé (zkrátit na 300s pro testování)

### Problem: Emaily jdou do spamu

**Diagnóza**:
1. Poslat email na https://www.mail-tester.com/
2. Zkontrolovat score a chyby

**Časté příčiny**:
- ❌ DNS není nastavené → Dokončit kroky 1-3
- ❌ SMTP_SENDER neodpovídá doméně → Změnit v `.env`
- ❌ SendGrid doména není ověřená → Verifikovat v dashboardu
- ❌ Příliš agresivní DMARC policy → Změnit na `p=none`
- ❌ Nový SendGrid účet (reputation) → Posílat postupně, ne hromadně

### Problem: "Authentication failed" při posílání

**Řešení**:
```bash
# Zkontrolovat, že SENDGRID_API_KEY je správně v .env
ssh root@SERVER_IP
cd /opt/datatalk-sync
cat .env | grep SENDGRID_API_KEY

# Zkontrolovat n8n logy
docker logs datatalk-n8n --tail 50 | grep -i smtp

# Test SMTP připojení
docker exec -it datatalk-n8n sh -c "
  wget -q -O - \
    --user=apikey \
    --password=\$SENDGRID_API_KEY \
    smtp://smtp.sendgrid.net:587
"
```

### Problem: Credential "SMTP" not found

**Řešení**:
```bash
# Re-run post-init container
ssh root@SERVER_IP
cd /opt/datatalk-sync
docker compose up datatalk-n8n-post-init

# Nebo vytvořit manuálně v n8n UI:
# Credentials → Add Credential → SMTP
# Name: SMTP (PŘESNĚ toto jméno!)
# Host: smtp.sendgrid.net
# Port: 587
# User: apikey
# Password: <SENDGRID_API_KEY>
```

## Best Practices

### Produkce

- ✅ Použít **vlastní doménu** (ne Gmail/Outlook)
- ✅ Nastavit **DMARC reporty** a sledovat je
- ✅ **Rotovat SendGrid API key** každých 90 dní
- ✅ Povolit **2FA** na SendGrid účtu
- ✅ **Monitorovat bounce rate** (cíl: <5%)
- ✅ **Warm-up**: První týden posílat malé množství (10-50/den)

### Bezpečnost

- ❌ NIKDY necommitovat API key do gitu
- ✅ Uložit API key v **GitHub Secrets**
- ✅ API key scope: **pouze "Mail Send"**, ne full access
- ✅ Používat **SendGrid Subusers** pro oddělení prostředí (dev/staging/prod)

### Deliverability

- ✅ **From email** by měl být na vaší doméně
- ✅ **Reply-To** nastavit na reálný email, kde odpovídáte
- ✅ **Unsubscribe link** v každém emailu (zákonný požadavek)
- ✅ **Text + HTML verze** emailu (vyšší deliverability)
- ❌ Neposílat ze `@gmail.com`, `@outlook.com` apod.

## Reference

- [SendGrid Domain Authentication Guide](https://docs.sendgrid.com/ui/account-and-settings/how-to-set-up-domain-authentication)
- [SPF Record Syntax](https://dmarcian.com/spf-syntax-table/)
- [DMARC Guide](https://dmarc.org/overview/)
- [Email Deliverability Best Practices](https://sendgrid.com/blog/email-deliverability-best-practices/)

## Next Steps

Po úspěšném nastavení DNS:

1. ✅ Zkontrolovat všechny 3 testy (signup, dashboard, headers)
2. 📊 Nastavit monitoring (Uptime Robot pro n8n healthcheck)
3. 💾 Nastavit PostgreSQL backup (cron job pro pg_dump)
4. 🔒 Přidat HTTPS pomocí Caddy nebo Nginx + Let's Encrypt
5. 📈 Sledovat SendGrid statistiky (opens, clicks, bounces)
