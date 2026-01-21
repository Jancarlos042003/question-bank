from sqlalchemy.orm import sessionmaker, Session
from app.db.engine import engine

SessionLocal = sessionmaker(
    bind=engine, autoflush=False, autocommit=False, class_=Session
)
