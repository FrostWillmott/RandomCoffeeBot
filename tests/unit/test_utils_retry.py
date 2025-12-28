"""Tests for retry utilities."""

from unittest.mock import patch

import pytest
from aiogram.exceptions import (
    TelegramRetryAfter,
    TelegramServerError,
)

from app.utils.retry import retry_telegram_api


@pytest.mark.asyncio
async def test_retry_telegram_api_success():
    """Test successful call without retries."""
    call_count = 0

    @retry_telegram_api(max_attempts=3)
    async def successful_call():
        nonlocal call_count
        call_count += 1
        return "success"

    result = await successful_call()
    assert result == "success"
    assert call_count == 1


@pytest.mark.asyncio
async def test_retry_telegram_api_retryable_error_succeeds():
    """Test retry on retryable error that eventually succeeds."""
    call_count = 0

    @retry_telegram_api(max_attempts=3, initial_wait=0.05, max_wait=0.2)
    async def retryable_call():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise TelegramServerError(method="test", message="Temporary error")
        return "success"

    result = await retryable_call()
    assert result == "success"
    assert call_count == 2


@pytest.mark.asyncio
async def test_retry_telegram_api_retryable_error_exhausted():
    """Test retry exhausted for retryable errors."""
    call_count = 0

    @retry_telegram_api(max_attempts=2, initial_wait=0.05, max_wait=0.2)
    async def always_fails():
        nonlocal call_count
        call_count += 1
        raise TelegramServerError(method="test", message="Always fails")

    with pytest.raises(TelegramServerError):
        await always_fails()

    assert call_count == 2


@pytest.mark.asyncio
async def test_retry_telegram_api_retry_after():
    """Test retry on TelegramRetryAfter error."""
    call_count = 0

    @retry_telegram_api(max_attempts=3, initial_wait=0.05, max_wait=0.2)
    async def retry_after_call():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise TelegramRetryAfter(method="test", message="Rate limited", retry_after=1)
        return "success"

    result = await retry_after_call()
    assert result == "success"
    assert call_count == 2


@pytest.mark.asyncio
async def test_retry_telegram_api_non_retryable_error():
    """Test that non-retryable errors are not retried."""
    call_count = 0

    from aiogram.exceptions import TelegramBadRequest

    @retry_telegram_api(max_attempts=3)
    async def non_retryable_call():
        nonlocal call_count
        call_count += 1
        raise TelegramBadRequest(method="test", message="Non-retryable error")

    with pytest.raises(TelegramBadRequest):
        await non_retryable_call()

    assert call_count == 1


@pytest.mark.asyncio
async def test_retry_telegram_api_logs_warning():
    """Test that retryable errors log warnings."""

    call_count = 0

    @retry_telegram_api(max_attempts=2, initial_wait=0.01, max_wait=0.1)
    async def retryable_call():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise TelegramServerError(method="test", message="Temporary error")
        return "success"

    with patch("app.utils.retry.logger") as mock_logger:
        result = await retryable_call()
        assert result == "success"
        assert mock_logger.warning.called
