"""API tests."""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel

from app.main import app, get_db
from app.models import Subscriber, SubscriberStatus


# Test database
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})


def override_get_db():
    with Session(engine) as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)


client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "status" in response.json()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_subscribe():
    response = client.post("/subscribe", json={"email": "test@example.com"})
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_subscribe_duplicate():
    client.post("/subscribe", json={"email": "test@example.com"})
    response = client.post("/subscribe", json={"email": "test@example.com"})
    assert response.status_code == 200  # Should handle gracefully


def test_verify_invalid_token():
    response = client.get("/verify?token=invalid")
    assert response.status_code == 400


def test_events_empty():
    response = client.get("/events")
    assert response.status_code == 200
    assert response.json() == []


def test_unsubscribe():
    response = client.post("/unsubscribe", json="test@example.com")
    assert response.status_code == 200
