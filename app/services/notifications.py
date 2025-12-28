"""Notification service for sending match notifications."""

import logging

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import async_session_maker
from app.models.match import Match
from app.models.user import User

logger = logging.getLogger(__name__)


def _format_user_info(user: User) -> str:
    """Format user information for display."""
    parts = []
    if user.first_name:
        parts.append(user.first_name)
    if user.last_name:
        parts.append(user.last_name)
    if user.username:
        parts.append(f"(@{user.username})")

    return " ".join(parts) if parts else f"User #{user.telegram_id}"


def _create_match_keyboard(match_id: int) -> InlineKeyboardMarkup:
    """Create keyboard for match notification."""
    buttons = [
        [
            InlineKeyboardButton(
                text="✅ Confirm Match",
                callback_data=f"confirm_match:{match_id}",
            )
        ],
        [
            InlineKeyboardButton(
                text="📅 Suggest Time",
                callback_data=f"suggest_time:{match_id}",
            )
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def send_match_notification(bot: Bot, match_id: int) -> bool:
    """Send match notification to both users."""
    async with async_session_maker() as session:
        try:
            # Get match with all related data
            result = await session.execute(
                select(Match)
                .options(
                    selectinload(Match.user1),
                    selectinload(Match.user2),
                    selectinload(Match.topic),
                    selectinload(Match.session),
                )
                .where(Match.id == match_id)
            )
            match = result.scalar_one_or_none()

            if not match:
                logger.error(f"Match {match_id} not found")
                return False

            # Send notification to both users
            success = True
            for user, partner in [
                (match.user1, match.user2),
                (match.user2, match.user1),
            ]:
                try:
                    message_text = _create_match_message(user, partner, match)
                    await bot.send_message(
                        chat_id=user.telegram_id,
                        text=message_text,
                        parse_mode="HTML",
                        reply_markup=_create_match_keyboard(match.id),
                    )
                    logger.info(
                        f"Sent match notification to user {user.telegram_id}"
                    )
                except TelegramAPIError as e:
                    logger.error(
                        f"Failed to send match notification to "
                        f"user {user.telegram_id}: {e}"
                    )
                    success = False

            return success

        except Exception as e:
            logger.error(
                f"Error sending match notification for match {match_id}: {e}"
            )
            return False


def _create_match_message(user: User, partner: User, match: Match) -> str:
    """Create match notification message."""
    partner_info = _format_user_info(partner)
    session_date = match.session.date.strftime("%A, %B %d at %H:%M UTC")

    message = (
        f"🎉 <b>You've been matched for Random Coffee!</b>\n\n"
        f"👤 <b>Your match:</b> {partner_info}\n"
        f"📅 <b>Session date:</b> {session_date}\n\n"
    )

    if match.topic:
        message += (
            f"📚 <b>Discussion Topic:</b> {match.topic.title}\n\n"
            f"<i>{match.topic.description}</i>\n\n"
            f"<b>Discussion Questions:</b>\n"
        )
        for i, question in enumerate(match.topic.questions[:4], 1):
            message += f"{i}. {question}\n"

        if match.topic.resources:
            message += "\n<b>Resources:</b>\n"
            for resource in match.topic.resources[:3]:
                message += f"• {resource}\n"

    message += (
        "\n<b>Next Steps:</b>\n"
        "1️⃣ Reach out to your match via Telegram\n"
        "2️⃣ Coordinate a meeting time (30-60 minutes recommended)\n"
        "3️⃣ Choose a format: Zoom, Google Meet, or Telegram call\n"
        "4️⃣ Discuss the assigned topic together\n"
        "5️⃣ Share feedback after your meeting\n\n"
        "💡 <b>Tip:</b> Start with introductions, then dive into the topic! "
        "Don't worry about knowing everything - it's about learning together.\n\n"
        "Have a great conversation! ☕️"
    )

    return message


async def notify_all_matches_for_session(bot: Bot, session_id: int) -> int:
    """Send notifications for all matches in a session.

    Returns the number of successful notifications sent.
    """
    async with async_session_maker() as session:
        try:
            # Get all matches for this session
            result = await session.execute(
                select(Match).where(Match.session_id == session_id)
            )
            matches = result.scalars().all()

            notifications_sent = 0
            for match in matches:
                success = await send_match_notification(bot, match.id)
                if success:
                    notifications_sent += 1

            logger.info(
                f"Sent {notifications_sent} match notifications "
                f"for session {session_id}"
            )
            return notifications_sent

        except Exception as e:
            logger.error(
                f"Error notifying matches for session {session_id}: {e}"
            )
            return 0
