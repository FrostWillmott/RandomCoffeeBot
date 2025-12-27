"""Bot initialization module."""

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import get_settings

settings = get_settings()

async def get_bot() -> Bot:
    """Initialize and return the Bot instance."""
    return Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

def get_dispatcher() -> Dispatcher:
    """Initialize and return the Dispatcher instance."""
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # You can register routers here later
    # dp.include_router(some_router)

    return dp
