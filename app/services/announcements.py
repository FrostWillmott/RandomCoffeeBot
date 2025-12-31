"""Announcement service for posting to a Telegram group."""

import logging
from typing import Any

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.session import async_session_maker
from app.models.session import Session
from app.repositories.session import SessionRepository
from app.utils.retry import retry_telegram_api

logger = logging.getLogger(__name__)


@retry_telegram_api(max_attempts=3, initial_wait=1.0, max_wait=30.0)
async def _send_announcement_with_retry(bot: Bot, **kwargs: Any) -> Any:
    """Send an announcement message with retry logic.

    Args:
        bot: Bot instance
        **kwargs: Arguments for bot.send_message

    Returns:
        Sent message
    """
    return await bot.send_message(**kwargs)


async def post_session_announcement(
    bot: Bot, session: Session, db_session: AsyncSession | None = None
) -> bool:
    """Post the Random Coffee session announcement to the group.

    Args:
        bot: Bot instance
        session: Session to announce
        db_session: Optional database session

    Returns:
        True if announcement was posted successfully
    """
    settings = get_settings()
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
            "Поставьте 👍 на это сообщение для участия.\n"
            "Чтобы отменить — уберите реакцию.\n\n"
            "⚠️ <b>Важно:</b> у вас должен быть установлен "
            "@username в настройках Telegram.\n\n"
            "💡 <b>Почему стоит участвовать?</b>\n"
            "• Практикуйте объяснение технических концепций\n"
            "• Учитесь у коллег\n"
            "• Расширяйте свою сеть контактов\n"
            "• Готовьтесь к собеседованиям\n\n"
            "Не упустите возможность! 🚀"
        )

        message = await _send_announcement_with_retry(
            bot,
            chat_id=settings.channel_id,
            text=announcement_text,
            parse_mode="HTML",
        )

        if db_session is None:
            async with async_session_maker() as new_session:
                session_repo = SessionRepository(new_session)
                session.announcement_message_id = message.message_id
                await session_repo.update(session)
                await new_session.commit()
        else:
            session_repo = SessionRepository(db_session)
            session.announcement_message_id = message.message_id
            await session_repo.update(session)

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
