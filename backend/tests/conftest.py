import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import app.task_cache as cache_module
from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture(autouse=True)
def reset_cache():
    cache_module._cache.clear()
    cache_module._user_generation.clear()
    yield
    cache_module._cache.clear()
    cache_module._user_generation.clear()


@pytest.fixture()
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers(client):
    client.post("/api/auth/register", json={"username": "testuser", "password": "pass1234"})
    r = client.post("/api/auth/token", data={"username": "testuser", "password": "pass1234"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture()
def auth_headers2(client):
    client.post("/api/auth/register", json={"username": "otheruser", "password": "pass5678"})
    r = client.post("/api/auth/token", data={"username": "otheruser", "password": "pass5678"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}
