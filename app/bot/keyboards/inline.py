"""Inline keyboards for the bot."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Get the main menu keyboard."""
    buttons = [
        [
            InlineKeyboardButton(
                text="📝 Зарегистрироваться на Random Coffee", callback_data="register"
            )
        ],
        [InlineKeyboardButton(text="ℹ️ Мой статус", callback_data="status")],
        [InlineKeyboardButton(text="❓ Справка", callback_data="help")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_match_actions_keyboard(match_id: int) -> InlineKeyboardMarkup:
    """Get keyboard with actions for a matched user's personal notification."""
    buttons = [
        [
            InlineKeyboardButton(
                text="✅ Подтвердить встречу", callback_data=f"confirm_match:{match_id}"
            ),
        ],
        [
            InlineKeyboardButton(
                text="⭐ Оставить отзыв", callback_data=f"start_feedback:{match_id}"
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
