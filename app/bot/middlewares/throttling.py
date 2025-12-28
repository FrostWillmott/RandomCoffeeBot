"""Throttling middleware to prevent spam."""

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Message
from redis.asyncio import Redis

from app.config import get_settings


class ThrottlingMiddleware(BaseMiddleware):
    """Middleware for rate limiting."""

    def __init__(self, limit: float = 0.5):
        """Initialize middleware.

        Args:
            limit: Minimum interval between messages in seconds.
        """
        self.limit = limit
        settings = get_settings()
        self.redis = Redis.from_url(settings.redis_url)

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        """Process event."""
        if not isinstance(event, Message):
            return await handler(event, data)

        if not event.from_user:
            return await handler(event, data)

        user_id = event.from_user.id
        key = f"throttle:{user_id}"

        if await self.redis.get(key):
            return None

        await self.redis.set(key, "1", px=int(self.limit * 1000))

        return await handler(event, data)
