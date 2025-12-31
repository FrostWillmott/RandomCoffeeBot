"""Start a command handler."""

import asyncio
from datetime import UTC, datetime, timedelta

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards import get_main_menu_keyboard
from app.services.users import get_or_create_user

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession) -> None:
    """Handle /start command."""
    if not message.from_user:
        return

    # Get or create user via service
    user = await get_or_create_user(
        session=session,
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )

    # Check if this is a new user (created within last 5 seconds)
    now = datetime.now(UTC)
    is_new_user = user.created_at and (now - user.created_at) < timedelta(seconds=5)

    if is_new_user:
        welcome_text = (
            f"👋 Добро пожаловать, {message.from_user.first_name}!\n\n"
            "🤝 Random Coffee Bot объединяет Python-разработчиков для "
            "еженедельных кофе-чатов.\n\n"
            "📋 <b>Как это работает:</b>\n"
            "1️⃣ Поставьте 👍 на анонс сессии в группе\n"
            "2️⃣ Получите пару с другим разработчиком\n"
            "3️⃣ Обсудите назначенную тему\n"
            "4️⃣ Поделитесь отзывом после встречи\n\n"
            "⚠️ <b>Важно:</b> установите @username в настройках Telegram "
            "для участия."
        )
    else:
        welcome_text = (
            f"👋 С возвращением, {message.from_user.first_name}!\n\nВыберите опцию:"
        )

    temp_msg = await message.answer(
        "🔄 Обновление...",
        reply_markup=ReplyKeyboardRemove(),
    )

    await asyncio.sleep(0.2)
    try:
        await temp_msg.delete()
    except Exception:
        pass  # Message may already be deleted or bot lacks permissions

    await message.answer(
        welcome_text,
        reply_markup=get_main_menu_keyboard(),
    )
