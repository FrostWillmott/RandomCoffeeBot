"""Throttling middleware to prevent spam."""

import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject
from redis.asyncio import Redis

from app.config import get_settings


class ThrottlingMiddleware(BaseMiddleware):
    """Middleware for per-user rate limiting on messages and callbacks.

    Uses Redis SET NX with TTL to enforce a minimum interval between
    consecutive events from the same user. Separate keys are used for
    different event types so a user can still tap a button immediately
    after sending a text message.
    """

    def __init__(
        self,
        message_limit: float = 0.5,
        callback_limit: float = 0.3,
    ):
        """Initialize middleware.

        Args:
            message_limit: Minimum interval between messages in seconds.
            callback_limit: Minimum interval between callback queries in seconds.
        """
        self.message_limit = message_limit
        self.callback_limit = callback_limit
        settings = get_settings()
        self.redis = Redis.from_url(settings.redis_url)
        self._closed = False

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """Process event with throttling for messages and callback queries."""
        if isinstance(event, Message):
            user = event.from_user
            kind, limit = "msg", self.message_limit
        elif isinstance(event, CallbackQuery):
            user = event.from_user
            kind, limit = "cb", self.callback_limit
        else:
            return await handler(event, data)

        if not user:
            return await handler(event, data)

        key = f"throttle:{kind}:{user.id}"
        try:
            acquired = await self.redis.set(
                key,
                "1",
                px=int(limit * 1000),
                nx=True,
            )
        except Exception:
            # Redis is unavailable — fail open and let the event through.
            logging.getLogger(__name__).warning(
                "Throttling Redis unavailable, failing open for %s:%s",
                kind,
                user.id,
            )
            return await handler(event, data)

        if not acquired:
            # Drop the message silently; for callbacks, still answer() so
            # the spinner is dismissed without surprising the user.
            if isinstance(event, CallbackQuery):
                try:
                    await event.answer()
                except Exception:
                    pass
            return None

        return await handler(event, data)

    async def close(self) -> None:
        """Close the Redis connection."""
        if self._closed:
            return
        try:
            close = getattr(self.redis, "aclose", None)
            if close is not None:
                await close()
            else:
                await self.redis.close()
        finally:
            self._closed = True
