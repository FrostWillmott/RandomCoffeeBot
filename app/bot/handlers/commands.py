"""Command handlers."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards import get_main_menu_keyboard
from app.models.match import Match
from app.models.registration import Registration
from app.models.session import Session
from app.models.user import User

router = Router()


@router.message(Command("help"))
@router.callback_query(F.data == "help")
async def cmd_help(event: Message | CallbackQuery) -> None:
    """Handle /help command or help button."""
    help_text = (
        "❓ <b>Random Coffee Bot Help</b>\n\n"
        "<b>Available Commands:</b>\n"
        "/start - Start the bot and see main menu\n"
        "/help - Show this help message\n"
        "/status - Check your current status\n\n"
        "<b>How Random Coffee Works:</b>\n\n"
        "1️⃣ <b>Registration</b>\n"
        "   • Every week a new session is announced in the channel\n"
        "   • Use the bot to register for upcoming sessions\n\n"
        "2️⃣ <b>Matching</b>\n"
        "   • After registration closes, participants are randomly paired\n"
        "   • Each pair receives a Python Middle interview topic\n\n"
        "3️⃣ <b>Meeting</b>\n"
        "   • Coordinate meeting time and format with your match\n"
        "   • Discuss the assigned topic together\n\n"
        "4️⃣ <b>Feedback</b>\n"
        "   • Share your experience after the meeting\n"
        "   • Help improve future sessions\n\n"
        "<b>Need help?</b> Contact @your_support"
    )

    if isinstance(event, Message):
        await event.answer(help_text, parse_mode="HTML")
    else:
        if event.message:
            await event.message.edit_text(
                help_text,
                parse_mode="HTML",
                reply_markup=get_main_menu_keyboard(),
            )
        await event.answer()


@router.message(Command("status"))
@router.callback_query(F.data == "status")
async def cmd_status(
    event: Message | CallbackQuery, session: AsyncSession
) -> None:
    """Handle /status command or status button."""
    if isinstance(event, Message):
        user_id = event.from_user.id if event.from_user else None
        message = event
    else:
        user_id = event.from_user.id if event.from_user else None
        message = event.message

    if not user_id or not message:
        return

    # Get user
    result = await session.execute(
        select(User).where(User.telegram_id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        status_text = "⚠️ You're not registered. Use /start to register."
    else:
        # Get active registrations
        result = await session.execute(
            select(Registration, Session)
            .join(Session)
            .where(
                and_(
                    Registration.user_id == user.id,
                    Session.status.in_(["open", "closed"]),
                )
            )
            .order_by(Session.date.desc())
        )
        registrations = result.all()

        # Get active matches
        result = await session.execute(
            select(Match, Session)
            .join(Session)
            .where(
                and_(
                    (Match.user1_id == user.id) | (Match.user2_id == user.id),
                    Match.status.in_(["created", "confirmed"]),
                )
            )
            .order_by(Session.date.desc())
        )
        matches = result.all()

        status_text = "ℹ️ <b>Your Status</b>\n\n"
        status_text += f"👤 Name: {user.first_name or 'N/A'}\n"
        status_text += f"🎯 Level: {user.level}\n\n"

        if registrations:
            status_text += (
                f"📝 <b>Active Registrations:</b> {len(registrations)}\n"
            )
            for reg, sess in registrations[:3]:
                status_text += f"   • {sess.date.strftime('%Y-%m-%d')}\n"

        if matches:
            status_text += f"\n🤝 <b>Active Matches:</b> {len(matches)}\n"
            for match, sess in matches[:3]:
                status_text += (
                    f"   • {sess.date.strftime('%Y-%m-%d')} - {match.status}\n"
                )

        if not registrations and not matches:
            status_text += "No active registrations or matches.\n"
            status_text += "Use the menu to register for the next session!"

    if isinstance(event, Message):
        await message.answer(status_text, parse_mode="HTML")
    else:
        await message.edit_text(
            status_text,
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard(),
        )
        await event.answer()
