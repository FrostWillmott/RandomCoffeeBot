"""Registration handlers."""

from datetime import datetime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards import (
    get_confirm_registration_keyboard,
    get_main_menu_keyboard,
)
from app.bot.states import RegistrationStates
from app.models.registration import Registration
from app.models.session import Session
from app.models.user import User

router = Router()


@router.callback_query(F.data == "register")
async def start_registration(
    callback: CallbackQuery, session: AsyncSession, state: FSMContext
) -> None:
    """Handle registration button click."""
    if not callback.message or not callback.from_user:
        return

    # Get next active session
    result = await session.execute(
        select(Session)
        .where(
            and_(
                Session.status == "open",
                Session.registration_deadline > datetime.utcnow(),
            )
        )
        .order_by(Session.date)
    )
    next_session = result.scalar_one_or_none()

    if not next_session:
        await callback.message.edit_text(
            "😔 No upcoming sessions available for registration.\n"
            "Check back later!",
            reply_markup=get_main_menu_keyboard(),
        )
        await callback.answer()
        return

    # Check if already registered
    result = await session.execute(
        select(Registration).where(
            and_(
                Registration.session_id == next_session.id,
                Registration.user_id
                == (
                    await session.execute(
                        select(User.id).where(
                            User.telegram_id == callback.from_user.id
                        )
                    )
                ).scalar_one(),
            )
        )
    )
    existing_registration = result.scalar_one_or_none()

    if existing_registration:
        await callback.message.edit_text(
            f"✅ You're already registered for the session on "
            f"{next_session.date.strftime('%Y-%m-%d %H:%M')}",
            reply_markup=get_main_menu_keyboard(),
        )
        await callback.answer()
        return

    # Show confirmation
    deadline_str = next_session.registration_deadline.strftime(
        "%Y-%m-%d %H:%M"
    )
    session_date_str = next_session.date.strftime("%Y-%m-%d %H:%M")

    await state.update_data(session_id=next_session.id)
    await state.set_state(RegistrationStates.waiting_for_confirmation)

    await callback.message.edit_text(
        f"📅 Register for Random Coffee\n\n"
        f"Session date: {session_date_str}\n"
        f"Registration deadline: {deadline_str}\n\n"
        f"Confirm your registration?",
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
        await callback.answer("Error: Session not found")
        await state.clear()
        return

    # Get user
    result = await session.execute(
        select(User).where(User.telegram_id == callback.from_user.id)
    )
    user = result.scalar_one()

    # Create registration
    registration = Registration(
        user_id=user.id,
        session_id=session_id,
        registered_at=datetime.utcnow(),
    )
    session.add(registration)
    await session.commit()

    await callback.message.edit_text(
        "✅ Registration successful!\n\n"
        "You'll receive a notification when matches are formed.",
        reply_markup=get_main_menu_keyboard(),
    )
    await callback.answer("Registered!")
    await state.clear()


@router.callback_query(
    RegistrationStates.waiting_for_confirmation,
    F.data == "cancel_registration",
)
async def cancel_registration(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """Cancel registration."""
    if not callback.message:
        return

    await callback.message.edit_text(
        "❌ Registration cancelled.",
        reply_markup=get_main_menu_keyboard(),
    )
    await callback.answer()
    await state.clear()
