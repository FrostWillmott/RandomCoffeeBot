"""Inline keyboards for the bot."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Get main menu keyboard."""
    buttons = [
        [
            InlineKeyboardButton(
                text="📝 Register for Random Coffee", callback_data="register"
            )
        ],
        [InlineKeyboardButton(text="ℹ️ My Status", callback_data="status")],
        [InlineKeyboardButton(text="❓ Help", callback_data="help")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_confirm_registration_keyboard() -> InlineKeyboardMarkup:
    """Get confirmation keyboard for registration."""
    buttons = [
        [
            InlineKeyboardButton(
                text="✅ Confirm", callback_data="confirm_registration"
            ),
            InlineKeyboardButton(
                text="❌ Cancel", callback_data="cancel_registration"
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
