# DataTalk Event Sync

Automatizovaný systém pro scraping eventů z DataTalk.cz, LLM extrakci a notifikace odběratelům.

## Architektura

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────────┐
│  DataTalk.cz    │────▶│  n8n Server  │────▶│  Subscribers    │
│  (Web Scraper)  │     │  (Workflows) │     │  (Email/TG)     │
└─────────────────┘     └──────────────┘     └─────────────────┘
                              │
                              ▼
                        ┌──────────────┐
                        │  OpenAI API  │
                        │  (Extrakce)  │
                        └──────────────┘
```

## Komponenty

| Komponenta | Popis | Port |
|------------|-------|------|
| n8n | Workflow automation engine | 5678 |
| ttyd | Web terminal pro správu | 7681 |

## Dokumentace

- **[DEPLOY.md](./DEPLOY.md)** - Nasazení (dev/prod)
- **[WORKFLOWS.md](./WORKFLOWS.md)** - Popis workflow
- **[CREDENTIALS.md](./CREDENTIALS.md)** - Konfigurace secrets
- **[config.yml](../config.yml)** - Referenční konfigurace

## Quick Start

```bash
# 1. Zkopíruj konfiguraci
cp config.yml.example config.yml
cp datatalk-sync/.env.example datatalk-sync/.env

# 2. Vyplň credentials v .env

# 3. Deploy
./deploy.sh
```

## Co chybí pro produkci

Viz [DEPLOY.md#produkční-checklist](./DEPLOY.md#produkční-checklist)
