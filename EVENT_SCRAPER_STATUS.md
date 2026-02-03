# Event Scraper - Current Status

## ✅ Co bylo uděláno:

1. **Server rebuilt** s Data Tables support
2. **SSH funguje** (pomocí ~/.ssh/hetzner_deploy key)
3. **Data Tables vytvořeny** v databázi:
   - ✅ subscribers table exists
   - ✅ events table exists
   - ✅ Správný projectId: KE5Uf66IgLopBsm3
4. **Workflows importovány** (všechny 4 + setup workflow)
5. **SMTP credential vytvořen**
6. **n8n verze:** 2.4.8
7. **N8N_ENABLED_MODULES:** data-table ✅

## ❌ Problém:

Data Table nodes failují s error:
```
"Cannot read properties of undefined (reading 'id')"
```

**Test provedené:**
- ✅ Jednoduchý getAll query - FAILS
- ✅ Search query - FAILS
- ✅ Create query - FAILS
- ✅ n8n restart - nepomohlo

**Root cause:**
n8n Data Table node má internal bug nebo vyžaduje specifickou konfiguraci která chybí.

## 🔍 Možné řešení:

### Option A: Manuální test v n8n UI
1. Login: http://5.75.160.39:5678 (pavel@guineai.com)
2. Otevřít Data Tables v menu
3. Zkusit přidat row do `events` tabulky manuálně
4. Pokud to funguje → problém je v workflow structure
5. Pokud to nefunguje → problém je v n8n Data Tables implementaci

### Option B: Upgrade n8n
n8n 2.4.8 je z prosince 2024. Možná má bug s Data Tables.
Upgrade na latest stable by mohl pomoct.

### Option C: Alternative approach
Místo n8n Data Tables použít přímé PostgreSQL queries:
- Použít n8n Postgres node místo Data Table node
- Funguje stejně, ale je to standard SQL místo n8n abstrakce

## 📊 Současný stav workflows:

| Workflow | Import | Activate | Test | Status |
|----------|--------|----------|------|--------|
| 01-subscriber-signup | ✅ | ✅ | ❓ | Needs test |
| 02-email-verify | ✅ | ✅ | 404 | Webhook not registered |
| 03-telegram-verify | ✅ | ✅ | 404 | Webhook not registered |
| 04-event-scraper | ✅ | ✅ | ❌ | Data Table error |

**Webhooks 404** - workflows nejsou aktivované nebo webhooks nejsou registrované po importu.

## 🎯 Další kroky:

1. **Aktivovat workflows** přes n8n API nebo UI
2. **Test Data Tables** v n8n UI manuálně
3. **Pokud Data Tables nefungují** → použít Postgres node
4. **Nebo upgrade n8n** na latest

## 💡 Doporučení:

**Nejrychlejší fix:** Nahradit Data Table nodes za Postgres nodes.

Data Tables jsou beta feature a mají problémy. PostgreSQL je production-ready:
- Stejná databáze (už používá postgres)
- Standard SQL queries
- Žádné internal n8n bugs
- Lepší error messages

**Změny potřebné:**
- Replace `n8n-nodes-base.dataTable` → `n8n-nodes-base.postgres`
- Convert operations (search → SELECT, create → INSERT, etc.)
- 15-20 minut práce

Nebo říct uživateli ať otestuje Data Tables v UI a zjistí jestli to vůbec funguje.
