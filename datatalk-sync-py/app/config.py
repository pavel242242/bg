"""Configuration management with validation."""
from pydantic_settings import BaseSettings
from pydantic import EmailStr, field_validator
from functools import lru_cache


class Settings(BaseSettings):
    # App
    app_name: str = "DataTalk Event Sync"
    debug: bool = False

    # Database
    database_url: str = "sqlite:///data/app.db"

    # Scraper
    scrape_url: str = "https://datatalk.cz/events"
    scrape_schedule: str = "0 8 * * 1"  # Monday 8:00

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    # Email (Resend.com - jednodušší než SMTP)
    resend_api_key: str = ""
    email_from: str = "events@yourdomain.com"

    # Telegram (optional)
    telegram_bot_token: str = ""

    # Security
    secret_key: str = "change-me-in-production"

    @field_validator('openai_api_key', 'resend_api_key')
    @classmethod
    def warn_if_empty(cls, v, info):
        if not v:
            import logging
            logging.warning(f"{info.field_name} is empty - feature disabled")
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
