"""Retry utilities for Telegram API calls."""

import logging
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

from aiogram.exceptions import (
    TelegramAPIError,
    TelegramRetryAfter,
    TelegramServerError,
)
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)

RETRYABLE_ERRORS = (
    TelegramServerError,
    TelegramRetryAfter,
)

T = TypeVar("T")


def retry_telegram_api(
    max_attempts: int = 3,
    initial_wait: float = 1.0,
    max_wait: float = 60.0,
    exponential_base: float = 2.0,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator for retrying Telegram API calls with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts (default: 3)
        initial_wait: Initial wait time in seconds (default: 1.0)
        max_wait: Maximum wait time in seconds (default: 60.0)
        exponential_base: Base for exponential backoff (default: 2.0)

    Returns:
        Decorated function with retry logic
    """
    retry_decorator = retry(
        retry=retry_if_exception_type(RETRYABLE_ERRORS),
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(
            multiplier=initial_wait,
            max=max_wait,
            exp_base=exponential_base,
        ),
        reraise=True,
    )

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        @retry_decorator
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                result = await func(*args, **kwargs)
                return result
            except RETRYABLE_ERRORS as e:
                logger.warning(
                    f"Retryable Telegram API error in {func.__name__}: {e}. "
                    f"Will retry according to retry policy."
                )
                raise
            except TelegramAPIError as e:
                logger.error(f"Non-retryable Telegram API error in {func.__name__}: {e}")
                raise

        return wrapper

    return decorator
