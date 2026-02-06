"""Business logic services."""
import httpx
import json
import hashlib
import logging
from datetime import datetime
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential
from sqlmodel import Session, select

from .models import Subscriber, Event, NotificationLog, SubscriberStatus
from .config import get_settings

log = logging.getLogger(__name__)
settings = get_settings()


# === Scraper ===
class Scraper:
    """Scrape events from DataTalk.cz"""

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def fetch_page(self, url: str) -> str:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text

    def parse_events(self, html: str) -> list[dict]:
        """Parse event cards from HTML."""
        soup = BeautifulSoup(html, "html.parser")
        events = []

        # Adjust selectors based on actual DataTalk.cz structure
        for card in soup.select(".event-card, .event-item, article"):
            title = card.select_one("h2, h3, .title")
            link = card.select_one("a[href]")
            date = card.select_one(".date, time")

            if title and link:
                events.append({
                    "title": title.get_text(strip=True),
                    "url": link.get("href", ""),
                    "date_text": date.get_text(strip=True) if date else None,
                    "description": card.get_text(strip=True)[:500],
                })

        return events

    async def scrape(self) -> list[dict]:
        """Main scrape method."""
        log.info(f"Scraping {settings.scrape_url}")
        html = await self.fetch_page(settings.scrape_url)
        events = self.parse_events(html)
        log.info(f"Found {len(events)} events")
        return events


# === LLM Extractor ===
class EventExtractor:
    """Extract structured data using LLM."""

    PROMPT = """Analyze these events and extract structured data.
Return a JSON array with objects containing:
- title: string
- date: ISO date string or null
- location: "online" or city name
- topics: array of tags like ["AI", "Data", "Python"]
- type: "workshop" | "meetup" | "conference" | "webinar"
- level: "beginner" | "intermediate" | "advanced"

Events to analyze:
{events}

Return ONLY valid JSON array, no markdown."""

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=30))
    async def extract(self, events: list[dict]) -> list[dict]:
        if not settings.openai_api_key:
            log.warning("OpenAI API key not set, returning raw events")
            return events

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                json={
                    "model": settings.openai_model,
                    "messages": [
                        {"role": "user", "content": self.PROMPT.format(
                            events=json.dumps(events, ensure_ascii=False)
                        )}
                    ],
                    "temperature": 0.1,
                }
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]

            # Clean markdown if present
            if content.startswith("```"):
                content = content.split("\n", 1)[1].rsplit("```", 1)[0]

            return json.loads(content)


# === Notifier ===
class Notifier:
    """Send notifications via email and Telegram."""

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def send_email(self, to: str, subject: str, html: str) -> bool:
        if not settings.resend_api_key:
            log.warning(f"Email skipped (no API key): {to}")
            return False

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {settings.resend_api_key}"},
                json={
                    "from": settings.email_from,
                    "to": to,
                    "subject": subject,
                    "html": html,
                }
            )
            if response.status_code == 200:
                log.info(f"Email sent to {to}")
                return True
            else:
                log.error(f"Email failed: {response.text}")
                return False

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def send_telegram(self, chat_id: str, text: str) -> bool:
        if not settings.telegram_bot_token:
            log.warning(f"Telegram skipped (no token): {chat_id}")
            return False

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": "Markdown",
                }
            )
            return response.status_code == 200


# === Main workflow ===
async def run_scrape_and_notify(session: Session):
    """Main workflow: scrape → extract → save → notify."""
    scraper = Scraper()
    extractor = EventExtractor()
    notifier = Notifier()

    # 1. Scrape
    raw_events = await scraper.scrape()
    if not raw_events:
        log.warning("No events found")
        return

    # 2. Extract with LLM
    enriched = await extractor.extract(raw_events)

    # 3. Save new events
    new_events = []
    for e in enriched:
        event_id = hashlib.md5(e["url"].encode()).hexdigest()[:16]
        existing = session.exec(select(Event).where(Event.external_id == event_id)).first()

        if not existing:
            event = Event(
                external_id=event_id,
                title=e.get("title", ""),
                url=e.get("url", ""),
                location=e.get("location"),
                description=e.get("description"),
                topics=json.dumps(e.get("topics", [])),
                event_type=e.get("type"),
            )
            session.add(event)
            new_events.append(event)

    session.commit()
    log.info(f"Saved {len(new_events)} new events")

    if not new_events:
        log.info("No new events to notify")
        return

    # 4. Notify subscribers
    subscribers = session.exec(
        select(Subscriber).where(Subscriber.status == SubscriberStatus.VERIFIED)
    ).all()

    for sub in subscribers:
        # Format email
        html = format_email(new_events)
        await notifier.send_email(sub.email, "Nové eventy na DataTalk", html)

        # Telegram if available
        if sub.telegram_chat_id:
            text = format_telegram(new_events)
            await notifier.send_telegram(sub.telegram_chat_id, text)

        # Log
        for event in new_events:
            session.add(NotificationLog(
                subscriber_id=sub.id,
                event_id=event.id,
                channel="email"
            ))

    session.commit()
    log.info(f"Notified {len(subscribers)} subscribers")


def format_email(events: list[Event]) -> str:
    """Format events as HTML email."""
    items = "\n".join(
        f'<div style="margin-bottom:20px;padding:15px;border:1px solid #ddd;border-radius:8px;">'
        f'<h3 style="margin:0 0 10px 0;">{e.title}</h3>'
        f'<p style="color:#666;margin:5px 0;">{e.location or "TBD"}</p>'
        f'<a href="{e.url}" style="color:#0066cc;">Více info →</a>'
        f'</div>'
        for e in events
    )
    return f"""
    <div style="font-family:sans-serif;max-width:600px;margin:0 auto;">
        <h1 style="color:#333;">Nové eventy tento týden</h1>
        {items}
        <p style="color:#999;font-size:12px;margin-top:30px;">
            <a href="{{{{unsubscribe_url}}}}">Odhlásit</a>
        </p>
    </div>
    """


def format_telegram(events: list[Event]) -> str:
    """Format events as Telegram message."""
    items = "\n\n".join(
        f"*{e.title}*\n📍 {e.location or 'TBD'}\n[Více info]({e.url})"
        for e in events[:5]  # Limit to 5 for Telegram
    )
    return f"🎉 *Nové eventy*\n\n{items}"
