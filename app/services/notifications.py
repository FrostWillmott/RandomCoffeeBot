"""Notification service for sending match notifications."""

import logging
from typing import Any

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError, TelegramForbiddenError
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import async_session_maker
from app.models.match import Match
from app.models.user import User
from app.utils.retry import retry_telegram_api

logger = logging.getLogger(__name__)


async def mark_user_inactive(user_id: int) -> None:
    """Mark the user as inactive in the database."""
    async with async_session_maker() as session:
        try:
            user = await session.get(User, user_id)
            if not user:
                logger.warning(f"User {user_id} not found, cannot mark inactive")
                return
            user.is_active = False
            await session.commit()
            logger.info(f"Marked user {user_id} as inactive")
        except Exception as e:
            logger.exception(
                f"Error marking user {user_id} inactive",
                exc_info=e,
            )
            await session.rollback()


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
    """Create a keyboard for match notification."""
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

            success = True
            for user, partner in [
                (match.user1, match.user2),
                (match.user2, match.user1),
            ]:
                try:
                    message_text = _create_match_message(user, partner, match)
                    await _send_message_with_retry(
                        bot,
                        chat_id=user.telegram_id,
                        text=message_text,
                        parse_mode="HTML",
                        reply_markup=_create_match_keyboard(match.id),
                    )
                    logger.info(f"Sent match notification to user {user.telegram_id}")
                except TelegramForbiddenError:
                    logger.warning(
                        f"User {user.telegram_id} blocked the bot. Marking inactive."
                    )
                    await mark_user_inactive(user.id)
                    success = False
                except TelegramAPIError as e:
                    error_str = str(e).lower()
                    if "chat not found" in error_str or "bad request" in error_str:
                        logger.error(f"Bad request for user {user.telegram_id}: {e}")
                        if "chat not found" in error_str:
                            await mark_user_inactive(user.id)
                        success = False
                    else:
                        logger.error(
                            f"Failed to send match notification to "
                            f"user {user.telegram_id}: {e}"
                        )
                        success = False

            return success

        except Exception as e:
            logger.exception(
                f"Error sending match notification for match {match_id}",
                exc_info=e,
            )
            return False


from app.resources import messages


@retry_telegram_api(max_attempts=3, initial_wait=1.0, max_wait=30.0)
async def _send_message_with_retry(bot: Bot, **kwargs: Any) -> None:
    """Send a message with retry logic for transient errors."""
    await bot.send_message(**kwargs)


def _create_match_message(user: User, partner: User, match: Match) -> str:
    """Create a match notification message."""
    partner_info = _format_user_info(partner)
    session_date = match.session.date.strftime("%A, %B %d at %H:%M UTC")

    message = (
        f"{messages.MATCH_NOTIFICATION_TITLE}\n\n"
        f"{messages.MATCH_NOTIFICATION_USER.format(partner_info=partner_info)}\n"
        f"{messages.MATCH_NOTIFICATION_DATE.format(session_date=session_date)}\n\n"
    )

    if match.topic:
        message += (
            f"{messages.MATCH_NOTIFICATION_TOPIC.format(title=match.topic.title)}\n\n"
            f"{messages.MATCH_NOTIFICATION_TOPIC_DESC.format(description=match.topic.description)}\n\n"
            f"{messages.MATCH_NOTIFICATION_QUESTIONS}\n"
        )
        for i, question in enumerate(match.topic.questions[:4], 1):
            message += f"{i}. {question}\n"

        if match.topic.resources:
            message += f"{messages.MATCH_NOTIFICATION_RESOURCES}\n"
            for resource in match.topic.resources[:3]:
                message += f"• {resource}\n"

    message += messages.MATCH_NOTIFICATION_FOOTER

    return message


async def send_unmatched_notification(bot: Bot, user_id: int) -> bool:
    """Send notification to user who wasn't matched."""
    async with async_session_maker() as session:
        try:
            user = await session.get(User, user_id)
            if not user:
                logger.warning(f"User {user_id} not found for unmatched notification")
                return False

            try:
                await _send_message_with_retry(
                    bot,
                    chat_id=user.telegram_id,
                    text=messages.UNMATCHED_NOTIFICATION,
                    parse_mode="HTML",
                )
                logger.info(f"Sent unmatched notification to user {user.telegram_id}")
                return True
            except TelegramForbiddenError:
                logger.warning(
                    f"User {user.telegram_id} blocked the bot. Marking inactive."
                )
                await mark_user_inactive(user.id)
                return False
            except TelegramAPIError as e:
                error_str = str(e).lower()
                if "chat not found" in error_str or "bad request" in error_str:
                    logger.error(
                        f"Bad request sending unmatched notification to "
                        f"user {user.telegram_id}: {e}"
                    )
                    if "chat not found" in error_str:
                        await mark_user_inactive(user.id)
                    return False
                logger.error(
                    f"Telegram API error sending unmatched notification to "
                    f"user {user.telegram_id}: {e}"
                )
                return False
        except Exception as e:
            logger.exception(
                f"Error sending unmatched notification to {user_id}",
                exc_info=e,
            )
            return False


async def notify_all_matches_for_session(bot: Bot, session_id: int) -> int:
    """Send notifications for all matches in a session.

    Returns the number of successful notifications sent.
    """
    async with async_session_maker() as session:
        try:
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
                f"Sent {notifications_sent} match notifications for session {session_id}"
            )
            return notifications_sent

        except Exception as e:
            logger.exception(
                f"Error notifying matches for session {session_id}",
                exc_info=e,
            )
            return 0
