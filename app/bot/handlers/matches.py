"""Match interaction handlers."""

import logging
from datetime import UTC, datetime

from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards import get_main_menu_keyboard
from app.models.enums import MatchStatus
from app.models.match import Match
from app.schemas.callbacks import (
    ConfirmMatchCallback,
    SuggestTimeCallback,
    parse_callback_data,
)

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data.startswith("confirm_match:"))
async def confirm_match(callback: CallbackQuery, session: AsyncSession) -> None:
    """Handle match confirmation."""
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

    result = await session.execute(select(Match).where(Match.id == match_id))
    match = result.scalar_one_or_none()

    if not match:
        if callback.message:
            await callback.message.edit_text(
                "❌ Пара не найдена.",
                reply_markup=get_main_menu_keyboard(),
            )
        await callback.answer()
        return

    if match.status == MatchStatus.CREATED:
        match.status = MatchStatus.CONFIRMED
        match.confirmed_at = datetime.now(UTC)
        session.add(match)
        await session.commit()

        if callback.message:
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
        if callback.message:
            status_ru = {
                "CONFIRMED": "подтверждена",
                "COMPLETED": "завершена",
            }.get(match.status, match.status.lower())
            await callback.message.edit_text(
                f"ℹ️ Эта пара уже {status_ru}.",
                reply_markup=get_main_menu_keyboard(),
            )
        await callback.answer()


@router.callback_query(F.data.startswith("suggest_time:"))
async def suggest_time(callback: CallbackQuery) -> None:
    """Handle time suggestion (placeholder for now)."""
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
