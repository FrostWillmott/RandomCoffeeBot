"""Feedback handlers."""

import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards import get_main_menu_keyboard
from app.bot.states.feedback import FeedbackStates
from app.models.feedback import Feedback
from app.repositories.feedback import FeedbackRepository
from app.repositories.match import MatchRepository
from app.repositories.user import UserRepository
from app.schemas.callbacks import (
    RatingCallback,
    StartFeedbackCallback,
    parse_callback_data,
)

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(
    F.data.startswith("feedback:") | F.data.startswith("start_feedback:")
)
async def start_feedback(
    callback: CallbackQuery, session: AsyncSession, state: FSMContext
) -> None:
    """Start a feedback process.

    Args:
        callback: Callback query
        session: Database session
        state: FSM context
    """
    if not callback.message:
        return

    if not callback.data:
        await callback.answer("Неверный ID пары")
        return

    try:
        if callback.data.startswith("feedback:"):
            callback_data_str = "start_feedback:" + callback.data[9:]
        else:
            callback_data_str = callback.data
        callback_data = parse_callback_data(callback_data_str)
        if not isinstance(callback_data, StartFeedbackCallback):
            raise ValueError("Invalid callback type")
        match_id = callback_data.match_id
    except (ValueError, TypeError) as e:
        logger.warning(f"Invalid feedback callback data: {callback.data}, error: {e}")
        await callback.answer("Неверный ID пары")
        return

    match_repo = MatchRepository(session)
    match = await match_repo.get_by_id(match_id)
    if not match:
        await callback.answer("Пара не найдена")
        return

    if not callback.from_user:
        return

    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    if not user or user.id not in (
        match.user1_id,
        match.user2_id,
        match.user3_id if match.user3_id else None,
    ):
        await callback.answer("⛔ У вас нет доступа к этой паре", show_alert=True)
        return

    await state.update_data(match_id=match_id)
    await state.set_state(FeedbackStates.waiting_for_rating)

    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="1 ⭐️", callback_data="rating:1"),
                InlineKeyboardButton(text="2 ⭐️", callback_data="rating:2"),
                InlineKeyboardButton(text="3 ⭐️", callback_data="rating:3"),
            ],
            [
                InlineKeyboardButton(text="4 ⭐️", callback_data="rating:4"),
                InlineKeyboardButton(text="5 ⭐️", callback_data="rating:5"),
            ],
        ]
    )

    await callback.message.answer(
        "Как прошла ваша встреча? Оцените её от 1 до 5:",
        reply_markup=keyboard,
    )
    await callback.answer()


@router.callback_query(FeedbackStates.waiting_for_rating, F.data.startswith("rating:"))
async def process_rating(callback: CallbackQuery, state: FSMContext) -> None:
    """Process rating.

    Args:
        callback: Callback query
        state: FSM context
    """
    if not callback.message:
        return

    if not callback.data:
        await callback.answer("Неверная оценка")
        return

    try:
        callback_data = parse_callback_data(callback.data)
        if not isinstance(callback_data, RatingCallback):
            raise ValueError("Invalid callback type")
        rating = callback_data.rating
    except (ValueError, TypeError) as e:
        logger.warning(f"Invalid rating callback data: {callback.data}, error: {e}")
        await callback.answer("Неверная оценка")
        return

    await state.update_data(rating=rating)
    await state.set_state(FeedbackStates.waiting_for_comment)

    if callback.message and hasattr(callback.message, "edit_text"):
        await callback.message.edit_text(
            f"Вы оценили встречу на {rating} звёзд! ⭐️\n\n"
            "Есть ли у вас комментарии или предложения? "
            "(Отправьте сообщение или введите /skip)"
        )
    await callback.answer()


@router.message(FeedbackStates.waiting_for_comment)
async def process_comment(
    message: Message, session: AsyncSession, state: FSMContext
) -> None:
    """Process comment.

    Args:
        message: User message
        session: Database session
        state: FSM context
    """
    data = await state.get_data()
    match_id = data.get("match_id")
    rating = data.get("rating")

    if not match_id or not rating:
        await message.answer("Что-то пошло не так. Пожалуйста, попробуйте снова.")
        await state.clear()
        return

    comment = message.text
    if comment == "/skip" or not comment or not comment.strip():
        comment = None
    else:
        comment = comment.strip()[:1000]

    if not message.from_user:
        await message.answer("Информация о пользователе недоступна.")
        await state.clear()
        return

    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer("Пользователь не найден. Пожалуйста, начните с /start.")
        await state.clear()
        return

    feedback_repo = FeedbackRepository(session)
    if await feedback_repo.exists(match_id, user.id):
        await message.answer(
            "Вы уже оставили отзыв для этой встречи. Спасибо! 🙏",
            reply_markup=get_main_menu_keyboard(),
        )
        await state.clear()
        return

    feedback = Feedback(
        match_id=match_id,
        user_id=user.id,
        rating=rating,
        comment=comment,
    )
    await feedback_repo.create(feedback)

    await message.answer(
        "Спасибо за ваш отзыв! 🙏\nДо встречи на следующей сессии!",
        reply_markup=get_main_menu_keyboard(),
    )
    await state.clear()
