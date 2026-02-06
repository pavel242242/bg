"""FastAPI application with scheduler."""
import secrets
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr
from sqlmodel import Session, select
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from .config import get_settings
from .models import (
    Subscriber, Event, SubscriberStatus,
    get_engine, init_db, get_session
)
from .services import run_scrape_and_notify, Notifier

# Setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
log = logging.getLogger(__name__)
settings = get_settings()
engine = get_engine(settings.database_url)
scheduler = AsyncIOScheduler()


# === Lifespan ===
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db(engine)
    log.info("Database initialized")

    # Schedule scraper
    cron_parts = settings.scrape_schedule.split()
    scheduler.add_job(
        scheduled_scrape,
        CronTrigger(
            minute=cron_parts[0],
            hour=cron_parts[1],
            day=cron_parts[2],
            month=cron_parts[3],
            day_of_week=cron_parts[4],
        ),
        id="scraper",
        replace_existing=True,
    )
    scheduler.start()
    log.info(f"Scheduler started: {settings.scrape_schedule}")

    yield

    # Shutdown
    scheduler.shutdown()


app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
)


# === Dependencies ===
def get_db():
    with Session(engine) as session:
        yield session


# === Schemas ===
class SubscribeRequest(BaseModel):
    email: EmailStr
    telegram: str | None = None


class SubscribeResponse(BaseModel):
    success: bool
    message: str


# === Endpoints ===
@app.get("/")
async def root():
    return {"app": settings.app_name, "status": "running"}


@app.get("/health")
async def health(db: Session = Depends(get_db)):
    """Health check for monitoring."""
    try:
        db.exec(select(Subscriber).limit(1))
        return {"status": "healthy", "db": "connected"}
    except Exception as e:
        raise HTTPException(500, f"Unhealthy: {e}")


@app.post("/subscribe", response_model=SubscribeResponse)
async def subscribe(
    req: SubscribeRequest,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Subscribe to event notifications."""
    # Check existing
    existing = db.exec(
        select(Subscriber).where(Subscriber.email == req.email)
    ).first()

    if existing:
        if existing.status == SubscriberStatus.VERIFIED:
            return SubscribeResponse(success=True, message="Already subscribed")
        # Resend verification
        token = existing.verification_token
    else:
        # Create new
        token = secrets.token_urlsafe(32)
        subscriber = Subscriber(
            email=req.email,
            telegram_chat_id=req.telegram,
            verification_token=token,
        )
        db.add(subscriber)
        db.commit()

    # Send verification email
    background.add_task(send_verification_email, req.email, token)

    return SubscribeResponse(
        success=True,
        message="Verification email sent"
    )


@app.get("/verify")
async def verify_email(token: str, db: Session = Depends(get_db)):
    """Verify email address."""
    subscriber = db.exec(
        select(Subscriber).where(Subscriber.verification_token == token)
    ).first()

    if not subscriber:
        raise HTTPException(400, "Invalid or expired token")

    subscriber.status = SubscriberStatus.VERIFIED
    subscriber.verified_at = datetime.utcnow()
    subscriber.verification_token = None
    db.commit()

    # Redirect to success page or return JSON
    return {"success": True, "message": "Email verified!"}


@app.post("/unsubscribe")
async def unsubscribe(email: EmailStr, db: Session = Depends(get_db)):
    """Unsubscribe from notifications."""
    subscriber = db.exec(
        select(Subscriber).where(Subscriber.email == email)
    ).first()

    if subscriber:
        subscriber.status = SubscriberStatus.UNSUBSCRIBED
        db.commit()

    return {"success": True}


@app.get("/events")
async def list_events(
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """List recent events."""
    events = db.exec(
        select(Event).order_by(Event.scraped_at.desc()).limit(limit)
    ).all()
    return events


@app.post("/scrape")
async def trigger_scrape(
    background: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Manually trigger scraping (for testing)."""
    background.add_task(run_scrape_and_notify, db)
    return {"success": True, "message": "Scraping started"}


# === Background tasks ===
async def send_verification_email(email: str, token: str):
    """Send verification email."""
    notifier = Notifier()
    verify_url = f"{settings.scrape_url.replace('/events', '')}/verify?token={token}"

    html = f"""
    <div style="font-family:sans-serif;max-width:600px;margin:0 auto;">
        <h1>Potvrďte odběr</h1>
        <p>Klikněte pro potvrzení emailu:</p>
        <a href="{verify_url}"
           style="display:inline-block;padding:12px 24px;background:#0066cc;color:white;text-decoration:none;border-radius:6px;">
            Potvrdit email
        </a>
        <p style="color:#999;font-size:12px;margin-top:30px;">
            Pokud jste se neregistrovali, ignorujte tento email.
        </p>
    </div>
    """

    await notifier.send_email(email, "Potvrďte odběr eventů", html)


async def scheduled_scrape():
    """Scheduled scrape task."""
    log.info("Running scheduled scrape")
    with Session(engine) as session:
        await run_scrape_and_notify(session)


# === Run ===
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
