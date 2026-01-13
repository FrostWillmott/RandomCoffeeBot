"""Notification service for posting match results to a group."""

import logging
from typing import Any

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError, TelegramForbiddenError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.constants import SEND_PERSONAL_NOTIFICATIONS
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
            except (TelegramAPIError, SQLAlchemyError) as e:
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

        if match.user3:
            user3_mention = _format_user_mention(match.user3)
            pair_line = f"👥 {user1_mention} + {user2_mention} + {user3_mention}"
        else:
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


def _build_personal_notification_message(match: Match, user: User) -> str:
    """Build a personal notification message for a user about their match.

    Args:
        match: Match object with relations loaded
        user: User who will receive the notification

    Returns:
        Formatted message text
    """
    if match.user3_id and match.user3:
        partners = []
        if match.user1.id != user.id:
            partners.append(_format_user_mention(match.user1))
        if match.user2.id != user.id:
            partners.append(_format_user_mention(match.user2))
        if match.user3.id != user.id:
            partners.append(_format_user_mention(match.user3))

        partners_text = " и ".join(partners)
        message = "☕ <b>Random Coffee: Ваша группа сформирована!</b>\n\n"
        message += f"👥 Вы в группе с {partners_text}\n"
    else:
        partner = match.user1 if match.user2.id == user.id else match.user2
        partner_mention = _format_user_mention(partner)
        message = "☕ <b>Random Coffee: Ваша пара сформирована!</b>\n\n"
        message += f"👥 Ваш партнёр: {partner_mention}\n"

    if match.topic:
        message += f'\n📚 Тема для обсуждения: "<i>{match.topic.title}</i>"'
        if match.topic.description:
            message += f"\n\n{match.topic.description}"

    message += "\n\n💬 Свяжитесь с партнёром и договоритесь о встрече!"

    return message


async def _send_personal_notification(bot: Bot, user: User, match: Match) -> bool:
    """Send a personal notification to a user about their match.

    Args:
        bot: Bot instance
        user: User to notify
        match: Match object with relations loaded

    Returns:
        True if notification was sent successfully
    """
    try:
        message_text = _build_personal_notification_message(match, user)
        await _send_message_with_retry(
            bot,
            chat_id=user.telegram_id,
            text=message_text,
            parse_mode="HTML",
        )
        logger.debug(f"Sent personal notification to user {user.id} for match {match.id}")
        return True
    except TelegramForbiddenError as e:
        logger.info(
            f"Could not send personal notification to user {user.id}: {e}. "
            f"User has not started a conversation with the bot."
        )
        return False
    except Exception as e:
        logger.warning(
            f"Failed to send personal notification to user {user.id}: {e}",
            exc_info=e,
        )
        return False


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

            if SEND_PERSONAL_NOTIFICATIONS:
                personal_sent = 0
                personal_failed = 0

                for match in matches:
                    if match.user1:
                        if await _send_personal_notification(bot, match.user1, match):
                            personal_sent += 1
                        else:
                            personal_failed += 1

                    if match.user2:
                        if await _send_personal_notification(bot, match.user2, match):
                            personal_sent += 1
                        else:
                            personal_failed += 1

                    if match.user3:
                        if await _send_personal_notification(bot, match.user3, match):
                            personal_sent += 1
                        else:
                            personal_failed += 1

                logger.info(
                    f"Sent {personal_sent} personal notifications for session {session_id}"
                    f" ({personal_failed} failed)"
                )

            return True

        except TelegramAPIError as e:
            logger.exception(
                f"Failed to post matches for session {session_id}",
                exc_info=e,
            )
            return False
        except Exception as e:
            logger.exception(
                f"Failed to post matches for session {session_id}",
                exc_info=e,
            )
            return False
