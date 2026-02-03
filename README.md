# DataTalk Event Sync

Self-hosted n8n workflow automation for scraping DataTalk events, extracting structured data using AI, and notifying subscribers via Email and Telegram.

## 🎯 Features

- **Automated Event Scraping** - Weekly scraping of https://www.datatalk.cz/kalendar-akci/
- **AI-Powered Extraction** - LLM-based extraction of event details (title, dates, location, speakers, summary)
- **Double Verification** - Email + Telegram verification for subscribers
- **Multi-Channel Notifications** - Email and Telegram notifications
- **Self-Contained** - All data stored in n8n Data Tables (no external database needed)

## 📁 Project Structure

This is a monorepo with clear separation between infrastructure and application layers:

```
datamesh/
├── README.md                    # This file
├── .gitignore                   # Git ignore rules
│
├── infrastructure/              # 🚀 Deployment Layer
│   ├── .env.tpl                # Deployment secrets template (1Password)
│   ├── deploy.sh               # Hetzner Cloud deployment script
│   ├── cloud-init.yml          # Server initialization config
│   ├── create-smtp-*.sh        # SMTP credential setup scripts
│   └── README.md               # Deployment documentation
│
└── app/                        # 📦 Application Layer
    ├── .env.tpl                # Runtime secrets template (1Password)
    ├── docker-compose.yml      # Docker orchestration
    ├── workflows/              # n8n workflow definitions
    ├── scripts/                # Initialization scripts
    └── README.md               # Application documentation
```

## 🚀 Quick Start

### Local Development

1. **Prerequisites**
   - Docker and Docker Compose
   - 1Password CLI (for secrets management)
   - OpenAI API key
   - Telegram Bot token

2. **Setup Secrets**
   ```bash
   cd app
   op inject -i .env.tpl -o .env
   # Edit .env with your values if needed
   ```

3. **Start Services**
   ```bash
   docker compose up -d
   ```

4. **Access n8n**
   - Open http://localhost:5678
   - Import workflows from `app/workflows/`

See [app/README.md](app/README.md) for detailed application setup.

### Production Deployment

1. **Prerequisites**
   - Hetzner Cloud account
   - `hcloud` CLI installed
   - 1Password CLI with secrets configured

2. **Setup Infrastructure Secrets**
   ```bash
   cd infrastructure
   op inject -i .env.tpl -o .env
   ```

3. **Deploy to Hetzner**
   ```bash
   ./deploy.sh
   ```

See [infrastructure/README.md](infrastructure/README.md) for deployment details.

## 🔐 Secrets Management

This project uses **1Password CLI** for secure secrets management:

- **No .env files in git** - All secrets are stored in 1Password
- **Template-based** - `.env.tpl` files contain `op://` references
- **CI/CD Ready** - Inject secrets at deployment time
- **Team Friendly** - Share access via 1Password vaults

### 1Password Structure

```
Vault: gh-projects
├── chocholous__bg__infrastructure    # Deployment secrets
│   ├── hcloud_token
│   ├── deploy_ssh_key
│   └── deploy_ssh_key_pub
│
└── chocholous__bg__app              # Runtime secrets
    ├── n8n_password
    ├── n8n_encryption_key
    ├── postgres_password
    ├── openai_api_key
    ├── telegram_bot_token
    └── sendgrid_api_key
```

## 📚 Documentation

- **[Application Setup](app/README.md)** - n8n workflows, Data Tables, local development
- **[Deployment Guide](infrastructure/README.md)** - Hetzner Cloud deployment, cloud-init
- **[Quick Start](QUICK-START.md)** - Fastest path to deployment

## 🛠️ Technology Stack

- **n8n** - Workflow automation (2.7.1)
- **PostgreSQL** - Database backend (18-alpine)
- **OpenAI** - AI-powered event data extraction
- **Telegram Bot API** - Notifications
- **SendGrid** - Email delivery
- **Docker** - Containerization
- **Hetzner Cloud** - Infrastructure hosting

## 📊 Architecture

```
┌─────────────────┐    ┌──────────────────┐
│  Signup Form    │───▶│  Save Subscriber │
└─────────────────┘    └──────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    │
┌─────────────────┐    ┌──────────────────┐        │
│  Email Verify   │    │  Telegram Verify │        │
│    Webhook      │    │     Webhook      │        │
└─────────────────┘    └──────────────────┘        │
         │                    │                    │
         └────────────────────┼────────────────────┘
                              ▼
                    ┌──────────────────┐
                    │ Active Subscriber│
                    └──────────────────┘

┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Weekly Schedule │───▶│  Scrape Events   │───▶│  OpenAI Extract │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                       │
                                                       ▼
                              ┌─────────────────────────────────────┐
                              │         For Each New Event          │
                              │  ┌──────────┐    ┌───────────────┐  │
                              │  │   Email  │    │   Telegram    │  │
                              │  │  Notify  │    │    Notify     │  │
                              │  └──────────┘    └───────────────┘  │
                              └─────────────────────────────────────┘
```

## 🤝 Contributing

This is a personal project, but suggestions and improvements are welcome!

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 Links

- **DataTalk Events**: https://www.datatalk.cz/kalendar-akci/
- **n8n Documentation**: https://docs.n8n.io/
- **Hetzner Cloud**: https://www.hetzner.com/cloud

## 📧 Support

For questions or issues, please open a GitHub issue.

---

**🤖 Built with Claude Code** - AI-powered development assistant
