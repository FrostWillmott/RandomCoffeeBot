"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator
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

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        """Ensure required settings are configured in production."""
        if not self.debug:
            if (
                not self.secret_key
                or self.secret_key == "dev-secret-key-change-in-production"
            ):
                raise ValueError(
                    "SECRET_KEY must be set in production (DEBUG=false)"
                )
            if not self.telegram_bot_token or not self.telegram_bot_token.strip():
                raise ValueError(
                    "TELEGRAM_BOT_TOKEN must be set in production"
                )
        return self

    # Telegram
    telegram_bot_token: str = ""
    channel_id: str = ""

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/randomcoffee"
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
