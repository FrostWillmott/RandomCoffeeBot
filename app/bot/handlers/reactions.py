"""Reaction handlers for registration via emoji reactions."""

import logging

from aiogram import Router
from aiogram.types import MessageReactionUpdated, ReactionTypeEmoji
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.registration import Registration
from app.repositories.registration import RegistrationRepository
from app.repositories.session import SessionRepository
from app.repositories.user import UserRepository
from app.services.users import get_or_create_user

router = Router()
logger = logging.getLogger(__name__)

REGISTRATION_EMOJI = "👍"


def has_emoji(reactions: list, emoji: str) -> bool:
    """Check if the reactions list contains specific emoji.

    Args:
        reactions: List of reactions
        emoji: Emoji to check for

    Returns:
        True if emoji is in reactions
    """
    return any(isinstance(r, ReactionTypeEmoji) and r.emoji == emoji for r in reactions)


@router.message_reaction()
async def handle_reaction(reaction: MessageReactionUpdated, session: AsyncSession) -> None:
    """Handle emoji reactions on announcement messages for registration.

    Args:
        reaction: Reaction update event
        session: Database session
    """
    if not reaction.user:
        logger.debug("Skipping reaction without user info")
        return

    session_repo = SessionRepository(session)
    coffee_session = await session_repo.get_open_session_by_announcement(
        reaction.message_id
    )

    if not coffee_session:
        return

    old_reactions = reaction.old_reaction or []
    new_reactions = reaction.new_reaction or []

    had_thumbs_up = has_emoji(old_reactions, REGISTRATION_EMOJI)
    has_thumbs_up = has_emoji(new_reactions, REGISTRATION_EMOJI)

    if had_thumbs_up == has_thumbs_up:
        return

    telegram_user = reaction.user

    if has_thumbs_up and not had_thumbs_up:
        await handle_registration_add(session, reaction, coffee_session, telegram_user)
    elif had_thumbs_up and not has_thumbs_up:
        await handle_registration_remove(session, reaction, coffee_session, telegram_user)


async def handle_registration_add(
    session: AsyncSession,
    reaction: MessageReactionUpdated,
    coffee_session,
    telegram_user,
) -> None:
    """Handle adding registration when a user adds thumbs up.

    Args:
        session: Database session
        reaction: Reaction update event
        coffee_session: Coffee session
        telegram_user: Telegram user who reacted
    """
    from aiogram import Bot

    from app.bot import get_bot

    if not telegram_user.username:
        bot: Bot = await get_bot()
        user_mention = (
            f'<a href="tg://user?id={telegram_user.id}">'
            f"{telegram_user.first_name or 'Участник'}</a>"
        )
        await bot.send_message(
            chat_id=reaction.chat.id,
            text=(
                f"{user_mention}, для участия в Random Coffee "
                f"необходимо установить @username в настройках Telegram.\n\n"
                f"После установки поставьте 👍 ещё раз."
            ),
            parse_mode="HTML",
        )
        logger.info(f"User {telegram_user.id} tried to register without username")
        return

    user = await get_or_create_user(
        session=session,
        telegram_id=telegram_user.id,
        username=telegram_user.username,
        first_name=telegram_user.first_name,
        last_name=telegram_user.last_name,
    )

    registration_repo = RegistrationRepository(session)
    existing = await registration_repo.get_by_session_and_user(coffee_session.id, user.id)

    if existing:
        logger.debug(
            f"User {telegram_user.id} already registered for session {coffee_session.id}"
        )
        return

    registration = Registration(
        session_id=coffee_session.id,
        user_id=user.id,
    )
    try:
        await registration_repo.create(registration)
    except IntegrityError:
        # Race condition: another request already created the registration
        logger.debug(
            f"User {telegram_user.id} registration for session {coffee_session.id} "
            "already exists (race condition handled)"
        )
        return

    logger.info(
        f"User {telegram_user.id} (@{telegram_user.username}) "
        f"registered for session {coffee_session.id} via reaction"
    )


async def handle_registration_remove(
    session: AsyncSession,
    reaction: MessageReactionUpdated,
    coffee_session,
    telegram_user,
) -> None:
    """Handle removing registration when the user removes thumbs up.

    Args:
        session: Database session
        reaction: Reaction update event
        coffee_session: Coffee session
        telegram_user: Telegram user who removed reaction
    """
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(telegram_user.id)

    if not user:
        return

    registration_repo = RegistrationRepository(session)
    registration = await registration_repo.get_by_session_and_user(
        coffee_session.id, user.id
    )

    if registration:
        await registration_repo.delete(registration)
        logger.info(
            f"User {telegram_user.id} unregistered from "
            f"session {coffee_session.id} via reaction"
        )
