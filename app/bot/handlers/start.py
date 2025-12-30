"""Start a command handler."""

import asyncio

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards import get_main_menu_keyboard
from app.models.user import User

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession) -> None:
    """Handle /start command."""
    if not message.from_user:
        return

    result = await session.execute(
        select(User).where(User.telegram_id == message.from_user.id)
    )
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            level="middle",
        )
        session.add(user)
        await session.commit()

        welcome_text = (
            f"👋 Добро пожаловать, {message.from_user.first_name}!\n\n"
            "🤝 Random Coffee Bot объединяет Python-разработчиков для еженедельных "
            "кофе-чатов, чтобы обсуждать интересные технические темы.\n\n"
            "📋 Как это работает:\n"
            "1️⃣ Зарегистрируйтесь на предстоящие сессии\n"
            "2️⃣ Получите пару с другим разработчиком\n"
            "3️⃣ Обсудите назначенные темы Python Middle\n"
            "4️⃣ Поделитесь отзывом после встречи\n\n"
            "Выберите опцию ниже, чтобы начать:"
        )
    else:
        welcome_text = (
            f"👋 С возвращением, {message.from_user.first_name}!\n\nВыберите опцию:"
        )

    # Remove old ReplyKeyboard buttons (send temporary message)
    temp_msg = await message.answer(
        "🔄 Обновление...",
        reply_markup=ReplyKeyboardRemove(),
    )

    # Small delay and delete temp message
    await asyncio.sleep(0.2)
    try:
        await temp_msg.delete()
    except Exception:
        pass

    # Send welcome message with InlineKeyboard menu
    await message.answer(
        welcome_text,
        reply_markup=get_main_menu_keyboard(),
    )
