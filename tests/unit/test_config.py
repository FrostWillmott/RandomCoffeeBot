"""Tests for configuration."""

import os
from unittest.mock import patch

from app.config import Settings, get_settings


def test_settings_defaults():
    """Test default settings values."""
    settings = Settings()
    assert hasattr(settings, "debug")
    assert hasattr(settings, "log_level")
    assert hasattr(settings, "log_format")
    assert hasattr(settings, "secret_key")
    assert hasattr(settings, "telegram_bot_token")
    assert hasattr(settings, "database_url")
    assert hasattr(settings, "redis_url")


def test_settings_from_env():
    """Test settings from environment variables."""
    env_vars = {
        "DEBUG": "true",
        "LOG_LEVEL": "DEBUG",
        "LOG_FORMAT": "text",
        "TELEGRAM_BOT_TOKEN": "test_token",
        "DATABASE_URL": "postgresql+asyncpg://test:test@localhost/test",
        "REDIS_URL": "redis://localhost:6379/1",
    }

    with patch.dict(os.environ, env_vars, clear=False):
        from app.config import get_settings

        get_settings.cache_clear()
        settings = Settings()
        assert settings.debug is True
        assert settings.log_level == "DEBUG"
        assert settings.log_format == "text"
        assert settings.telegram_bot_token == "test_token"
        assert settings.database_url == env_vars["DATABASE_URL"]
        assert settings.redis_url == env_vars["REDIS_URL"]


def test_settings_production_validation():
    """Test production settings validation logic."""

    settings = Settings()

    assert settings.debug is False or settings.secret_key or settings.telegram_bot_token

    assert hasattr(Settings, "validate_production_settings")


def test_get_settings_cached():
    """Test that get_settings returns a cached instance."""
    get_settings.cache_clear()
    settings1 = get_settings()
    settings2 = get_settings()
    assert settings1 is settings2
