from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    APP_NAME: str
    ASYNC_DB_URL: str
    SYNC_DB_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JOB_INTERVAL_SECONDS: int = 300
    EVENT_REMINDER_LEAD_TIME_HOURS: int = 24
    RATE_LIMIT_MAX_REQUESTS: int = 30
    RATE_LIMIT_WINDOW_SECONDS: int =60
    WEBSOCKET_SEND_TIMEOUT_SECONDS: float = 5.0

    model_config = SettingsConfigDict(
        env_file=(
            BASE_DIR / "app" / "db" / ".env.db",
            BASE_DIR / "app" / ".env.app"
        ),
        env_file_encoding="utf-8",
        extra="ignore" # Review this again
    )


settings = Settings()