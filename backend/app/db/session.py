from collections.abc import Generator

from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine

from app.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



def check_db_connection() -> None:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))



def get_db_health() -> str:
    try:
        check_db_connection()
        return "ok"
    except Exception:
        return "unavailable"
