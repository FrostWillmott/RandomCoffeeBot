"""Start command handler."""

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
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

    # Check if user exists
    result = await session.execute(
        select(User).where(User.telegram_id == message.from_user.id)
    )
    user = result.scalar_one_or_none()

    # Create user if doesn't exist
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
            f"👋 Welcome, {message.from_user.first_name}!\n\n"
            "🤝 Random Coffee Bot connects Python developers for weekly coffee chats "
            "to discuss interesting technical topics.\n\n"
            "📋 How it works:\n"
            "1️⃣ Register for upcoming sessions\n"
            "2️⃣ Get matched with another developer\n"
            "3️⃣ Discuss assigned Python Middle topics\n"
            "4️⃣ Share feedback after the meeting\n\n"
            "Choose an option below to get started:"
        )
    else:
        welcome_text = (
            f"👋 Welcome back, {message.from_user.first_name}!\n\n"
            "Choose an option:"
        )

    await message.answer(
        welcome_text,
        reply_markup=get_main_menu_keyboard(),
    )
