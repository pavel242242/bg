# Workflows

## Přehled

| Workflow | Trigger | Popis |
|----------|---------|-------|
| 01-subscriber-signup | Webhook (form) | Registrace nového odběratele |
| 02-email-verify | Webhook (link) | Verifikace emailu |
| 03-telegram-verify | Webhook (bot) | Verifikace Telegram účtu |
| 04-event-scraper | Schedule (weekly) | Scraping a notifikace |

## 01 - Subscriber Signup

**Účel:** Přijímá registraci nového odběratele přes webový formulář.

**Trigger:** `POST /webhook/subscribe`

**Input:**
```json
{
  "email": "user@example.com",
  "telegram": "@username",        // volitelné
  "preferences": {
    "topics": ["AI", "Data"],
    "frequency": "weekly"
  }
}
```

**Proces:**
1. Validace emailu (regex)
2. Kontrola duplicit v databázi
3. Generování verifikačního tokenu
4. Uložení odběratele (status: pending)
5. Odeslání verifikačního emailu
6. (Volitelně) Odeslání Telegram zprávy

**Output:**
```json
{
  "success": true,
  "message": "Verification email sent"
}
```

**Chybové stavy:**
- `400` - Neplatný email
- `409` - Email již registrován
- `500` - SMTP chyba

---

## 02 - Email Verify

**Účel:** Potvrzení emailové adresy odběratele.

**Trigger:** `GET /webhook/verify-email?token=xxx`

**Proces:**
1. Dekódování tokenu
2. Kontrola expirace (24h)
3. Nalezení odběratele
4. Aktualizace statusu na "verified"
5. Přesměrování na success stránku

**Token formát:**
```
base64(JSON.stringify({
  email: "user@example.com",
  exp: timestamp,
  type: "email"
}))
```

---

## 03 - Telegram Verify

**Účel:** Propojení Telegram účtu s odběratelem.

**Trigger:** Telegram Bot webhook (`/start` command)

**Proces:**
1. Přijetí `/start <token>` zprávy
2. Validace tokenu
3. Uložení `chat_id` k odběrateli
4. Potvrzovací zpráva v Telegramu

**Bot commands:**
- `/start <token>` - Propojení účtu
- `/stop` - Odhlášení notifikací
- `/status` - Stav předplatného

---

## 04 - Event Scraper

**Účel:** Hlavní workflow - scraping, extrakce, notifikace.

**Trigger:** Schedule (každé pondělí 8:00 CET)

**Proces:**

### 4.1 Scraping
```
HTTP Request → datatalk.cz/events
Parse HTML → Extract event cards
```

**Extrahovaná data:**
- Název eventu
- Datum a čas
- Místo (online/offline)
- Popis
- URL

### 4.2 LLM Extrakce
```
OpenAI GPT-4 → Structured extraction
```

**Prompt template:**
```
Analyzuj následující eventy a extrahuj:
- Hlavní témata (AI, Data, ML, etc.)
- Typ (workshop, přednáška, meetup)
- Úroveň (beginner, intermediate, advanced)
- Jazyk (CS/EN)

Eventy:
{{events_json}}

Odpověz jako JSON array.
```

### 4.3 Matching
```
Pro každého odběratele:
  - Filtruj eventy podle preferencí
  - Seřaď podle relevance
```

### 4.4 Notifikace
```
Email: Formátovaný HTML newsletter
Telegram: Markdown zprávy s inline buttons
```

**Email template:**
```html
<h1>Nové eventy tento týden</h1>
{{#each events}}
<div class="event">
  <h2>{{title}}</h2>
  <p>{{date}} | {{location}}</p>
  <p>{{description}}</p>
  <a href="{{url}}">Více info →</a>
</div>
{{/each}}
```

---

## Datový model

### Subscriber
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "telegram_chat_id": "123456789",
  "status": "verified|pending|unsubscribed",
  "preferences": {
    "topics": ["AI", "Data"],
    "frequency": "weekly|daily",
    "language": "cs|en"
  },
  "verification_token": "xxx",
  "created_at": "2026-01-30T00:00:00Z",
  "verified_at": "2026-01-30T01:00:00Z"
}
```

### Event
```json
{
  "id": "uuid",
  "title": "AI Workshop",
  "date": "2026-02-15T18:00:00Z",
  "location": "online",
  "description": "...",
  "url": "https://datatalk.cz/events/xxx",
  "topics": ["AI", "ML"],
  "type": "workshop",
  "level": "intermediate",
  "language": "cs",
  "scraped_at": "2026-01-30T08:00:00Z"
}
```

---

## Webhook URLs

Pro produkci nastav `WEBHOOK_URL` v .env:

```
WEBHOOK_URL=https://your-domain.com

# Výsledné endpointy:
POST https://your-domain.com/webhook/subscribe
GET  https://your-domain.com/webhook/verify-email
POST https://your-domain.com/webhook/telegram
```

Pro development (lokálně):
```
WEBHOOK_URL=http://localhost:5678

# Nebo s ngrok:
ngrok http 5678
WEBHOOK_URL=https://xxx.ngrok.io
```
