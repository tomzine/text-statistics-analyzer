import pytest

from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from fastapi.testclient import TestClient

from fastapi_app.main import app
from fastapi_app.database import Base, get_db
from fastapi_app import models

TEST_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool)


# Create session factory
TestingSessionLocal = sessionmaker(
    bind = test_engine,
    autoflush = False,
    autocommit = False
)

@pytest.fixture
def client():

    try:
        Base.metadata.create_all(test_engine)

        def get_test_db():
            db = TestingSessionLocal()

            try:
                yield db

            finally:
                db.close()

        app.dependency_overrides[get_db] = get_test_db

        yield TestClient(app)

    finally:
        app.dependency_overrides.pop(get_db, None)

        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def jwt_secret(monkeypatch):

    monkeypatch.setenv("SECRET_KEY", "65795d684de6e484479feb58648d05c6a57404dcf520758aaaae8c30e0bcdb2d")

@pytest.fixture
def db_session(client):

    db = TestingSessionLocal()

    try:
        yield db

    finally:
        db.close()
