"""Telegram bot package."""

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage

from app.bot.handlers import (
    commands,
    feedback,
    matches,
    reactions,
    registration,
    start,
)
from app.bot.middlewares import DatabaseMiddleware, ThrottlingMiddleware
from app.config import get_settings


async def get_bot() -> Bot:
    """Create and return a bot instance."""
    settings = get_settings()
    return Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def get_dispatcher() -> tuple[Dispatcher, ThrottlingMiddleware]:
    """Create and configure dispatcher with middlewares.

    Returns:
        Tuple of (dispatcher, throttling_middleware) so the caller
        can manage the middleware lifecycle.
    """
    settings = get_settings()
    storage = RedisStorage.from_url(
        settings.redis_url,
        key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
    )
    dp = Dispatcher(storage=storage)

    throttling_mw = ThrottlingMiddleware()
    dp.message.middleware(throttling_mw)
    dp.update.middleware(DatabaseMiddleware())

    dp.include_router(start.router)
    dp.include_router(reactions.router)
    dp.include_router(registration.router)
    dp.include_router(matches.router)
    dp.include_router(feedback.router)
    dp.include_router(commands.router)

    return dp, throttling_mw


__all__ = ["get_bot", "get_dispatcher"]
