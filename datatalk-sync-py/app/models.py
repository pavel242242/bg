"""Database models using SQLModel (SQLAlchemy + Pydantic)."""
from sqlmodel import SQLModel, Field, create_engine, Session
from datetime import datetime
from typing import Optional
from enum import Enum


class SubscriberStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    UNSUBSCRIBED = "unsubscribed"


class Subscriber(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    telegram_chat_id: Optional[str] = None
    status: SubscriberStatus = SubscriberStatus.PENDING
    verification_token: Optional[str] = None
    preferences: str = "{}"  # JSON string
    created_at: datetime = Field(default_factory=datetime.utcnow)
    verified_at: Optional[datetime] = None


class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    external_id: str = Field(unique=True, index=True)  # URL or hash
    title: str
    date: Optional[datetime] = None
    location: Optional[str] = None
    description: Optional[str] = None
    url: str
    topics: str = "[]"  # JSON array
    event_type: Optional[str] = None  # workshop, meetup, etc.
    scraped_at: datetime = Field(default_factory=datetime.utcnow)


class NotificationLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    subscriber_id: int = Field(foreign_key="subscriber.id")
    event_id: int = Field(foreign_key="event.id")
    channel: str  # email, telegram
    sent_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "sent"  # sent, failed, bounced


# Database setup
def get_engine(database_url: str):
    return create_engine(database_url, echo=False)


def init_db(engine):
    SQLModel.metadata.create_all(engine)


def get_session(engine):
    return Session(engine)
