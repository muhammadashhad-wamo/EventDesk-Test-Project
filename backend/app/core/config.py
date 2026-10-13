from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    APP_NAME: str
    ASYNC_DB_URL: str
    SYNC_DB_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    JOB_INTERVAL_SECONDS: int
    EVENT_REMINDER_LEAD_TIME_HOURS: int

    model_config = SettingsConfigDict(
        env_file=(
            BASE_DIR / "app" / "db" / ".env.db",
            BASE_DIR / "app" / ".env.app"
        ),
        env_file_encoding="utf-8",
        extra="ignore" # Review this again
    )


settings = Settings()