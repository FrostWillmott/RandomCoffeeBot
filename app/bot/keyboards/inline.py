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


def get_confirm_registration_keyboard() -> InlineKeyboardMarkup:
    """Get a confirmation keyboard for registration."""
    buttons = [
        [
            InlineKeyboardButton(
                text="✅ Подтвердить", callback_data="confirm_registration"
            ),
            InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_registration"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
