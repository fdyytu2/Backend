from sqlalchemy.orm import sessionmaker
from app.core.db_engine import engine

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_db():
    db = SessionLocal()
    try: yield db
    except: db.rollback(); raise
    finally: db.close()
