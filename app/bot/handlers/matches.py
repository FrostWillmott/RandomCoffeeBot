"""Match interaction handlers."""

from datetime import datetime

from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards import get_main_menu_keyboard
from app.models.match import Match

router = Router()


@router.callback_query(F.data.startswith("confirm_match:"))
async def confirm_match(
    callback: CallbackQuery, session: AsyncSession
) -> None:
    """Handle match confirmation."""
    if not callback.message or not callback.from_user:
        return

    try:
        match_id = int(callback.data.split(":")[1])
    except (IndexError, ValueError):
        await callback.answer("Invalid match ID")
        return

    # Get the match
    result = await session.execute(select(Match).where(Match.id == match_id))
    match = result.scalar_one_or_none()

    if not match:
        await callback.message.edit_text(
            "❌ Match not found.",
            reply_markup=get_main_menu_keyboard(),
        )
        await callback.answer()
        return

    # Update match status
    if match.status == "created":
        match.status = "confirmed"
        match.confirmed_at = datetime.utcnow()
        session.add(match)
        await session.commit()

        await callback.message.edit_text(
            "✅ <b>Match Confirmed!</b>\n\n"
            "Great! You've confirmed the match. "
            "Now reach out to your partner to coordinate the meeting details.\n\n"
            "💡 <b>Suggested meeting length:</b> 30-60 minutes\n"
            "📞 <b>Format options:</b> Zoom, Google Meet, or Telegram call\n\n"
            "Have a productive conversation!",
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard(),
        )
        await callback.answer("Match confirmed!")
    else:
        await callback.message.edit_text(
            f"ℹ️ This match has already been {match.status}.",
            reply_markup=get_main_menu_keyboard(),
        )
        await callback.answer()


@router.callback_query(F.data.startswith("suggest_time:"))
async def suggest_time(callback: CallbackQuery) -> None:
    """Handle time suggestion (placeholder for now)."""
    if not callback.message:
        return

    await callback.message.edit_text(
        "📅 <b>Coordinate Meeting Time</b>\n\n"
        "To coordinate your meeting:\n\n"
        "1️⃣ Contact your match directly via Telegram\n"
        "2️⃣ Discuss your availability\n"
        "3️⃣ Choose a time that works for both of you\n"
        "4️⃣ Decide on the meeting format (Zoom, Meet, Telegram)\n\n"
        "💡 <b>Tip:</b> Share your calendar or suggest 2-3 time slots!",
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard(),
    )
    await callback.answer()
