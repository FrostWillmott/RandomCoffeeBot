"""Telegram bot package."""

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.bot.handlers import commands, matches, registration, start
from app.bot.middlewares import DatabaseMiddleware
from app.config import get_settings


async def get_bot() -> Bot:
    """Create and return bot instance."""
    settings = get_settings()
    return Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def get_dispatcher() -> Dispatcher:
    """Create and configure dispatcher."""
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Register middleware
    dp.update.middleware(DatabaseMiddleware())

    # Register routers
    dp.include_router(start.router)
    dp.include_router(registration.router)
    dp.include_router(matches.router)
    dp.include_router(commands.router)

    return dp


__all__ = ["get_bot", "get_dispatcher"]
