"""Notification service for posting match results to a group."""

import logging
from typing import Any

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.session import async_session_maker
from app.models.match import Match
from app.models.user import User
from app.repositories.match import MatchRepository
from app.repositories.user import UserRepository
from app.utils.retry import retry_telegram_api

logger = logging.getLogger(__name__)


async def mark_user_inactive(user_id: int, session: AsyncSession | None = None) -> None:
    """Mark the user as inactive in the database.

    Args:
        user_id: User ID to mark inactive
        session: Optional database session
    """
    if session is None:
        async with async_session_maker() as db_session:
            try:
                success = await _mark_user_inactive_logic(db_session, user_id)
                if success:
                    await db_session.commit()
            except Exception as e:
                logger.exception(f"Error marking user {user_id} inactive", exc_info=e)
                await db_session.rollback()
    else:
        await _mark_user_inactive_logic(session, user_id)


async def _mark_user_inactive_logic(session: AsyncSession, user_id: int) -> bool:
    """Core logic for marking user inactive.

    Returns:
        True if the user was found and marked inactive, False otherwise
    """
    user_repo = UserRepository(session)
    success = await user_repo.mark_inactive(user_id)
    if not success:
        logger.warning(f"User {user_id} not found, cannot mark inactive")
    else:
        logger.info(f"Marked user {user_id} as inactive")
    return success


def _format_user_mention(user: User) -> str:
    """Format user mention for a group message."""
    from app.utils.user_formatting import format_user_mention

    return format_user_mention(user)


@retry_telegram_api(max_attempts=3, initial_wait=1.0, max_wait=30.0)
async def _send_message_with_retry(bot: Bot, **kwargs: Any) -> None:
    """Send a message with retry logic for transient errors.

    Args:
        bot: Bot instance
        **kwargs: Arguments for bot.send_message
    """
    await bot.send_message(**kwargs)


def _build_matches_message(
    matches: list[Match], unmatched_users: list[User] | None = None
) -> str:
    """Build a message with all matches for posting to a group."""
    if not matches:
        return "☕ Нет пар для этой сессии."

    lines = ["☕ <b>Пары Random Coffee сформированы!</b>\n"]

    for match in matches:
        user1_mention = _format_user_mention(match.user1)
        user2_mention = _format_user_mention(match.user2)

        pair_line = f"👥 {user1_mention} + {user2_mention}"
        if match.topic:
            pair_line += f'\n   📚 Тема: "<i>{match.topic.title}</i>"'
        lines.append(pair_line)

    if unmatched_users:
        lines.append("")
        unmatched_mentions = ", ".join(_format_user_mention(u) for u in unmatched_users)
        lines.append(f"😔 Без пары: {unmatched_mentions}")
        lines.append("   (В следующий раз повезёт!)")

    lines.append("")
    lines.append("💬 Свяжитесь с партнёром и договоритесь о встрече!")

    return "\n".join(lines)


async def notify_all_matches_for_session(
    bot: Bot, session_id: int, unmatched_user_ids: list[int] | None = None
) -> bool:
    """Post all matches to the group as a single message.

    Args:
        bot: Bot instance
        session_id: Session ID to notify about
        unmatched_user_ids: List of user IDs who weren't matched

    Returns:
        True if a message was sent successfully
    """
    settings = get_settings()
    async with async_session_maker() as session:
        try:
            match_repo = MatchRepository(session)
            user_repo = UserRepository(session)

            matches = await match_repo.get_by_session_id_with_relations(session_id)

            unmatched_users: list[User] | None = None
            if unmatched_user_ids:
                unmatched_users = []
                for user_id in unmatched_user_ids:
                    user = await user_repo.get_by_id(user_id)
                    if user:
                        unmatched_users.append(user)

            if not matches:
                logger.warning(f"No matches found for session {session_id}")
                return False

            message_text = _build_matches_message(matches, unmatched_users)

            await _send_message_with_retry(
                bot,
                chat_id=settings.channel_id,
                text=message_text,
                parse_mode="HTML",
            )

            logger.info(f"Posted {len(matches)} matches to group for session {session_id}")
            return True

        except TelegramAPIError as e:
            logger.exception(
                f"Failed to post matches for session {session_id}",
                exc_info=e,
            )
            return False
        except Exception as e:
            logger.exception(
                f"Error posting matches for session {session_id}",
                exc_info=e,
            )
            return False
