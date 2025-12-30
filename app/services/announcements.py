"""Announcement service for posting to a Telegram channel."""

import logging
from typing import Any

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

from app.config import get_settings
from app.db.session import async_session_maker
from app.models.session import Session
from app.utils.retry import retry_telegram_api

logger = logging.getLogger(__name__)
settings = get_settings()


@retry_telegram_api(max_attempts=3, initial_wait=1.0, max_wait=30.0)
async def _send_announcement_with_retry(bot: Bot, **kwargs) -> Any:
    """Send an announcement message with retry logic."""
    return await bot.send_message(**kwargs)


async def post_session_announcement(bot: Bot, session: Session) -> bool:
    """Post the Random Coffee session announcement to the channel."""
    try:
        session_date_str = session.date.strftime("%A, %B %d at %H:%M UTC")
        deadline_str = session.registration_deadline.strftime("%A, %B %d at %H:%M UTC")

        announcement_text = (
            "☕️ <b>Random Coffee: Доступна новая сессия!</b>\n\n"
            f"📅 <b>Дата сессии:</b> {session_date_str}\n"
            f"⏰ <b>Дедлайн регистрации:</b> {deadline_str}\n\n"
            "🎯 <b>Формат этой недели:</b>\n"
            "• Получите случайную пару с другим Python-разработчиком\n"
            "• Получите тему для обсуждения Python Middle собеседования\n"
            "• Встретьтесь на 30-60 минут для обсуждения темы\n"
            "• Практикуйте навыки технической коммуникации\n\n"
            "📝 <b>Как зарегистрироваться:</b>\n"
            "Начните чат с @Kitty_co_bot и нажмите 'Зарегистрироваться на "
            "Random Coffee'\n\n"
            "💡 <b>Почему стоит участвовать?</b>\n"
            "• Практикуйте объяснение технических концепций\n"
            "• Учитесь у коллег\n"
            "• Расширяйте свою сеть контактов\n"
            "• Готовьтесь к собеседованиям\n\n"
            "Не упустите возможность! Зарегистрируйтесь сейчас! 🚀"
        )

        message = await _send_announcement_with_retry(
            bot,
            chat_id=settings.channel_id,
            text=announcement_text,
            parse_mode="HTML",
        )

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
        logger.exception(
            f"Failed to post announcement for session {session.id}",
            exc_info=e,
        )
        return False
    except Exception as e:
        logger.exception(
            "Unexpected error posting announcement",
            exc_info=e,
        )
        return False
