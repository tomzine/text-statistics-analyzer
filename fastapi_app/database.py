from sqlalchemy import create_engine, event
from sqlalchemy.orm import (
    DeclarativeBase,
    sessionmaker,
    Session
)

# Database URL
DATABASE_URL = "sqlite:///./students.db"

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

@event.listens_for(engine, "connect")
def enable_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# Create session factory
SessionLocal = sessionmaker(
    bind = engine,
    autoflush = False,
    autocommit = False
)

# Base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass


# Database dependency
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()