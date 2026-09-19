from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings


_database_url = settings.database_url.get_secret_value()
if _database_url.startswith("postgresql://"):

    _database_url = _database_url.replace("postgresql://", "postgresql+psycopg://", 1)

elif _database_url.startswith("postgres://"):
    _database_url = _database_url.replace("postgres://", "postgresql+psycopg://", 1)
    
connect_args = {"check_same_thread": False} if _database_url.startswith("sqlite") else {}
engine = create_engine(
    _database_url,
    echo=False,
    future=True,
    pool_pre_ping=True,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)

Base = declarative_base()


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
