import logging
from sqlalchemy import create_engine, event
from app.core.config import settings

def _normalize_db_url(url: str):
    if url.startswith("postgres"): return url.replace("postgres", "postgresql+psycopg", 1)
    return url

db_url = _normalize_db_url(settings.database_url)
engine = create_engine(db_url, pool_pre_ping=True)

if db_url.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_conn, _):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
