"""Registration handlers (legacy - now via reactions)."""

from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.bot.keyboards import get_main_menu_keyboard

router = Router()


@router.callback_query(F.data == "register")
async def start_registration(callback: CallbackQuery) -> None:
    """Handle registration button click - redirect to a new flow."""
    if not callback.message:
        return

    await callback.message.edit_text(
        "📝 <b>Регистрация на Random Coffee</b>\n\n"
        "Теперь регистрация происходит через реакции!\n\n"
        "1️⃣ Найдите анонс сессии в группе\n"
        "2️⃣ Поставьте 👍 на сообщение с анонсом\n"
        "3️⃣ Чтобы отменить — уберите реакцию\n\n"
        "⚠️ Важно: у вас должен быть установлен "
        "@username в настройках Telegram.",
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()
