from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    APP_NAME: str
    ASYNC_DB_URL: str
    SYNC_DB_URL: str

    model_config = SettingsConfigDict(
        env_file=(
            BASE_DIR / "app" / "db" / ".env.db",
            BASE_DIR / "app" / ".env.app"
        ),
        env_file_encoding="utf-8",
        extra="ignore" # Review this again
    )


settings = Settings()