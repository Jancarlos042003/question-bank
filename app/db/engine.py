from sqlalchemy import create_engine

from app.core.config import settings

USER = settings.DB_USER
PASSWORD = settings.DB_PASSWORD
HOST = settings.DB_HOST
PORT = settings.DB_PORT
DBNAME = settings.DB_NAME

DATABASE_URL = (
    f"postgresql+psycopg://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require"
)

engine = create_engine(
    url=DATABASE_URL,
    echo=True,
    future=True,
    pool_size=5,  # conexiones permanentes abiertas
    max_overflow=10,  # conexiones extra en picos
    pool_pre_ping=True,  # verifica que la conexión sigue viva
    pool_recycle=1800,  # recicla conexiones cada 30 min
)
