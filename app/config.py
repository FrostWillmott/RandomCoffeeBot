"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    debug: bool = False
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    secret_key: str = Field(default="dev-secret-key-change-in-production")

    # Telegram
    telegram_bot_token: str = ""
    channel_id: str = ""

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/randomcoffee"
    )

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Celery
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # Mail
    mail_server: str = "localhost"
    mail_port: int = 1025
    mail_username: str = ""
    mail_password: str = ""
    mail_from: str = "noreply@randomcoffee.local"
    mail_tls: bool = False

    @computed_field  # type: ignore[misc]
    @property
    def async_database_url(self) -> str:
        """Return async database URL."""
        return self.database_url


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
