from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    CONTAINER_NAME: str
    # Solo para desarrollo local
    GOOGLE_APPLICATION_CREDENTIALS: str | None = None
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = "6379"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env", env_file_encoding="utf-8"
    )


settings = Settings()
