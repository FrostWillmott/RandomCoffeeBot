"""Announcement service for posting to Telegram channel."""

import logging

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

from app.config import get_settings
from app.db.session import async_session_maker
from app.models.session import Session

logger = logging.getLogger(__name__)
settings = get_settings()


async def post_session_announcement(bot: Bot, session: Session) -> bool:
    """Post Random Coffee session announcement to the channel."""
    try:
        session_date_str = session.date.strftime("%A, %B %d at %H:%M UTC")
        deadline_str = session.registration_deadline.strftime(
            "%A, %B %d at %H:%M UTC"
        )

        announcement_text = (
            "☕️ <b>Random Coffee: New Session Available!</b>\n\n"
            f"📅 <b>Session Date:</b> {session_date_str}\n"
            f"⏰ <b>Registration Deadline:</b> {deadline_str}\n\n"
            "🎯 <b>This Week's Format:</b>\n"
            "• Get randomly matched with another Python developer\n"
            "• Receive a Python Middle interview discussion topic\n"
            "• Meet for 30-60 minutes to discuss the topic\n"
            "• Practice technical communication skills\n\n"
            "📝 <b>How to Register:</b>\n"
            "Start a chat with @Kitty_co_bot and click 'Register for Random Coffee'\n\n"
            "💡 <b>Why participate?</b>\n"
            "• Practice explaining technical concepts\n"
            "• Learn from peers\n"
            "• Expand your network\n"
            "• Prepare for interviews\n\n"
            "Don't miss out! Register now! 🚀"
        )

        message = await bot.send_message(
            chat_id=settings.channel_id,
            text=announcement_text,
            parse_mode="HTML",
        )

        # Update session with message ID
        async with async_session_maker() as db_session:
            session.announcement_message_id = message.message_id
            db_session.add(session)
            await db_session.commit()

        logger.info(
            f"Posted announcement for session {session.id} "
            f"(message_id: {message.message_id})"
        )
        return True

    except TelegramAPIError as e:
        logger.error(
            f"Failed to post announcement for session {session.id}: {e}"
        )
        return False
    except Exception as e:
        logger.error(f"Unexpected error posting announcement: {e}")
        return False
