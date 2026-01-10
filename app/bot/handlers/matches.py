"""Match interaction handlers."""

import logging
from datetime import UTC, datetime

from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards import get_main_menu_keyboard
from app.models.enums import MatchStatus
from app.models.match import Match
from app.repositories.match import MatchRepository
from app.repositories.user import UserRepository
from app.schemas.callbacks import (
    ConfirmMatchCallback,
    SuggestTimeCallback,
    parse_callback_data,
)

router = Router()
logger = logging.getLogger(__name__)


async def verify_match_participant(
    session: AsyncSession, telegram_id: int, match: Match
) -> bool:
    """Verify that the user is a participant of the match.

    Args:
        session: Database session
        telegram_id: Telegram user ID
        match: Match to check

    Returns:
        True if the user is a participant, False otherwise
    """
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(telegram_id)
    return user is not None and user.id in (
        match.user1_id,
        match.user2_id,
        match.user3_id if match.user3_id else None,
    )


@router.callback_query(F.data.startswith("confirm_match:"))
async def confirm_match(callback: CallbackQuery, session: AsyncSession) -> None:
    """Handle match confirmation.

    Args:
        callback: Callback query
        session: Database session
    """
    if not callback.message or not callback.from_user:
        return

    if not callback.data:
        await callback.answer("Неверный ID пары")
        return

    try:
        callback_data = parse_callback_data(callback.data)
        if not isinstance(callback_data, ConfirmMatchCallback):
            raise ValueError("Invalid callback type")
        match_id = callback_data.match_id
    except (ValueError, TypeError) as e:
        logger.warning(f"Invalid confirm_match callback data: {callback.data}, error: {e}")
        await callback.answer("Неверный ID пары")
        return

    match_repo = MatchRepository(session)
    match = await match_repo.get_by_id(match_id)

    if not match:
        await callback.message.edit_text(
            "❌ Пара не найдена.",
            reply_markup=get_main_menu_keyboard(),
        )
        await callback.answer()
        return

    # Authorization check
    if not await verify_match_participant(session, callback.from_user.id, match):
        await callback.answer("⛔ У вас нет доступа к этой паре", show_alert=True)
        return

    if match.status == MatchStatus.CREATED:
        match.status = MatchStatus.CONFIRMED
        match.confirmed_at = datetime.now(UTC)
        await match_repo.update(match)

        await callback.message.edit_text(
            "✅ <b>Пара подтверждена!</b>\n\n"
            "Отлично! Вы подтвердили пару. "
            "Теперь свяжитесь с вашим партнёром, чтобы согласовать детали "
            "встречи.\n\n"
            "💡 <b>Рекомендуемая длительность встречи:</b> 30-60 минут\n"
            "📞 <b>Варианты формата:</b> Zoom, Google Meet или звонок в "
            "Telegram\n\n"
            "Приятного общения!",
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard(),
        )
        await callback.answer("Пара подтверждена!")
    else:
        status_ru = {
            "confirmed": "подтверждена",
            "completed": "завершена",
        }.get(match.status, match.status.lower())
        await callback.message.edit_text(
            f"ℹ️ Эта пара уже {status_ru}.",
            reply_markup=get_main_menu_keyboard(),
        )
        await callback.answer()


@router.callback_query(F.data.startswith("suggest_time:"))
async def suggest_time(callback: CallbackQuery) -> None:
    """Handle time suggestion (placeholder for now).

    Args:
        callback: Callback query
    """
    if not callback.message:
        return

    if not callback.data:
        await callback.answer("Неверный запрос")
        return

    try:
        callback_data = parse_callback_data(callback.data)
        if not isinstance(callback_data, SuggestTimeCallback):
            raise ValueError("Invalid callback type")
    except (ValueError, TypeError) as e:
        logger.warning(f"Invalid suggest_time callback data: {callback.data}, error: {e}")
        await callback.answer("Неверный запрос")
        return

    if callback.message:
        await callback.message.edit_text(
            "📅 <b>Согласование времени встречи</b>\n\n"
            "Чтобы согласовать встречу:\n\n"
            "1️⃣ Свяжитесь с вашей парой напрямую через Telegram\n"
            "2️⃣ Обсудите вашу доступность\n"
            "3️⃣ Выберите время, которое подходит вам обоим\n"
            "4️⃣ Решите формат встречи (Zoom, Meet, Telegram)\n\n"
            "💡 <b>Совет:</b> Поделитесь своим календарём или предложите 2-3 "
            "варианта времени!",
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard(),
        )
    await callback.answer()
