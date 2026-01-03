"""Utilities for formatting user information."""

from aiogram.types import User as TelegramUser

from app.models.user import User


def format_user_mention(user: User | TelegramUser) -> str:
    """Format user mention for Telegram messages.

    Args:
        user: User model or Telegram User object

    Returns:
        Formatted mention string (@username or HTML link)
    """
    username = getattr(user, "username", None)
    if username:
        return f"@{username}"

    first_name = getattr(user, "first_name", None)
    user_id = getattr(user, "id", None) or getattr(user, "telegram_id", None)
    name = first_name or "Участник"

    if user_id:
        return f'<a href="tg://user?id={user_id}">{name}</a>'

    return name


def get_username_required_message(user_mention: str) -> str:
    """Get message about username requirement.

    Args:
        user_mention: Formatted user mention

    Returns:
        Message text about username requirement
    """
    return (
        f"{user_mention}, для участия в Random Coffee "
        f"необходимо установить @username в настройках Telegram.\n\n"
        f"После установки поставьте 👍 ещё раз."
    )
