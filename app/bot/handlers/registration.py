"""Registration handlers."""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy import and_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards import (
    get_confirm_registration_keyboard,
    get_main_menu_keyboard,
)
from app.bot.states import RegistrationStates
from app.models.registration import Registration

router = Router()


from app.services.helpers import get_next_open_session, get_user_by_telegram_id


@router.callback_query(F.data == "register")
async def start_registration(
    callback: CallbackQuery, session: AsyncSession, state: FSMContext
) -> None:
    """Handle registration button click."""
    if not callback.message or not callback.from_user:
        return

    next_session = await get_next_open_session(session)

    if not next_session:
        if callback.message:
            await callback.message.edit_text(
                "😔 Нет доступных сессий для регистрации.\nПроверьте позже!",
                reply_markup=get_main_menu_keyboard(),
            )
        await callback.answer()
        return

    user = await get_user_by_telegram_id(session, callback.from_user.id)
    if not user:
        return

    result = await session.execute(
        select(Registration).where(
            and_(
                Registration.session_id == next_session.id,
                Registration.user_id == user.id,
            )
        )
    )
    existing_registration = result.scalar_one_or_none()

    if existing_registration:
        if callback.message:
            await callback.message.edit_text(
                f"✅ Вы уже зарегистрированы на сессию "
                f"{next_session.date.strftime('%Y-%m-%d %H:%M')}",
                reply_markup=get_main_menu_keyboard(),
            )
        await callback.answer()
        return

    deadline_str = next_session.registration_deadline.strftime("%Y-%m-%d %H:%M")
    session_date_str = next_session.date.strftime("%Y-%m-%d %H:%M")

    await state.update_data(session_id=next_session.id)
    await state.set_state(RegistrationStates.waiting_for_confirmation)

    if callback.message:
        await callback.message.edit_text(
            f"📅 Регистрация на Random Coffee\n\n"
            f"Дата сессии: {session_date_str}\n"
            f"Дедлайн регистрации: {deadline_str}\n\n"
            f"Подтвердить регистрацию?",
            reply_markup=get_confirm_registration_keyboard(),
        )
    await callback.answer()


@router.callback_query(
    RegistrationStates.waiting_for_confirmation,
    F.data == "confirm_registration",
)
async def confirm_registration(
    callback: CallbackQuery, session: AsyncSession, state: FSMContext
) -> None:
    """Confirm registration."""
    if not callback.message or not callback.from_user:
        return

    data = await state.get_data()
    session_id = data.get("session_id")

    if not session_id:
        await callback.answer("Ошибка: Сессия не найдена")
        await state.clear()
        return

    user = await get_user_by_telegram_id(session, callback.from_user.id)
    if not user:
        return

    try:
        registration = Registration(
            user_id=user.id,
            session_id=session_id,
        )
        session.add(registration)
        await session.commit()
    except IntegrityError:
        await session.rollback()
        if callback.message:
            await callback.message.edit_text(
                "⚠️ Вы уже зарегистрированы на эту сессию.",
                reply_markup=get_main_menu_keyboard(),
            )
        await callback.answer("Уже зарегистрированы!")
        await state.clear()
        return

    if callback.message:
        await callback.message.edit_text(
            "✅ Регистрация успешна!\n\n"
            "Вы получите уведомление, когда будут сформированы пары.",
            reply_markup=get_main_menu_keyboard(),
        )
    await callback.answer("Зарегистрированы!")
    await state.clear()


@router.callback_query(
    RegistrationStates.waiting_for_confirmation,
    F.data == "cancel_registration",
)
async def cancel_registration(callback: CallbackQuery, state: FSMContext) -> None:
    """Cancel registration."""
    if not callback.message:
        return

    if callback.message:
        await callback.message.edit_text(
            "❌ Регистрация отменена.",
            reply_markup=get_main_menu_keyboard(),
        )
    await callback.answer()
    await state.clear()
