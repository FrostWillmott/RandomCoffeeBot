"""Command handlers."""

from collections.abc import Sequence

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards import get_main_menu_keyboard
from app.models.enums import MatchStatus, SessionStatus
from app.models.match import Match
from app.models.registration import Registration
from app.models.session import Session
from app.models.user import User

router = Router()


@router.message(Command("help"))
@router.callback_query(F.data == "help")
async def cmd_help(event: Message | CallbackQuery) -> None:
    """Handle /help command or help button."""
    help_text = (
        "❓ <b>Справка Random Coffee Bot</b>\n\n"
        "<b>Доступные команды:</b>\n"
        "/start - Запустить бота и увидеть главное меню\n"
        "/help - Показать это сообщение справки\n"
        "/status - Проверить ваш текущий статус\n\n"
        "<b>Как работает Random Coffee:</b>\n\n"
        "1️⃣ <b>Регистрация</b>\n"
        "   • Каждую неделю в канале объявляется новая сессия\n"
        "   • Используйте бота для регистрации на предстоящие сессии\n\n"
        "2️⃣ <b>Подбор пары</b>\n"
        "   • После закрытия регистрации участники случайным образом "
        "объединяются в пары\n"
        "   • Каждая пара получает тему для собеседования Python Middle\n\n"
        "3️⃣ <b>Встреча</b>\n"
        "   • Согласуйте время и формат встречи с вашей парой\n"
        "   • Обсудите назначенную тему вместе\n\n"
        "4️⃣ <b>Отзыв</b>\n"
        "   • Поделитесь своим опытом после встречи\n"
        "   • Помогите улучшить будущие сессии\n\n"
        "<b>Нужна помощь?</b> Свяжитесь с @your_support"
    )

    if isinstance(event, Message):
        await event.answer(help_text, parse_mode="HTML")
    else:
        if event.message:
            await event.message.edit_text(
                help_text,
                parse_mode="HTML",
                reply_markup=get_main_menu_keyboard(),
            )
        await event.answer()


async def _get_user_status_data(session: AsyncSession, user: User):
    """Retrieve active registrations and matches for a user."""
    reg_stmt = (
        select(Registration, Session)
        .join(Session)
        .where(
            and_(
                Registration.user_id == user.id,
                Session.status.in_([SessionStatus.OPEN, SessionStatus.CLOSED]),
            )
        )
        .order_by(Session.date.desc())
    )
    match_stmt = (
        select(Match, Session)
        .join(Session)
        .where(
            and_(
                or_(Match.user1_id == user.id, Match.user2_id == user.id),
                Match.status.in_([MatchStatus.CREATED, MatchStatus.CONFIRMED]),
            )
        )
        .order_by(Session.date.desc())
    )

    registrations = (await session.execute(reg_stmt)).all()
    matches = (await session.execute(match_stmt)).all()
    return registrations, matches


def _format_status_message(user: User, registrations: Sequence, matches: Sequence) -> str:
    """Construct the status text message."""
    text = (
        f"ℹ️ <b>Ваш статус</b>\n\n👤 Имя: {user.first_name or 'Не указано'}\n🎯"
        f" Уровень: {user.level}\n\n"
    )

    if registrations:
        text += f"📝 <b>Активные регистрации:</b> {len(registrations)}\n"
        for _, sess in registrations[:3]:
            text += f"   • {sess.date.strftime('%Y-%m-%d')}\n"

    if matches:
        text += f"\n🤝 <b>Активные пары:</b> {len(matches)}\n"
        for match, sess in matches[:3]:
            status_ru = {
                "CREATED": "Создана",
                "CONFIRMED": "Подтверждена",
                "COMPLETED": "Завершена",
            }.get(match.status.value, match.status.value)
            text += f"   • {sess.date.strftime('%Y-%m-%d')} - {status_ru}\n"

    if not registrations and not matches:
        text += (
            "Нет активных регистраций или пар.\n"
            "Используйте меню для регистрации на следующую сессию!"
        )
    return text


@router.message(Command("status"))
@router.callback_query(F.data == "status")
async def cmd_status(event: Message | CallbackQuery, session: AsyncSession) -> None:
    """Handle /status command or status button."""
    user_id = event.from_user.id if event.from_user else None
    message = event if isinstance(event, Message) else event.message

    if not user_id or not message:
        return

    user = (
        await session.execute(select(User).where(User.telegram_id == user_id))
    ).scalar_one_or_none()

    if not user:
        status_text = "⚠️ Вы не зарегистрированы. Используйте /start для регистрации."
    else:
        registrations, matches = await _get_user_status_data(session, user)
        status_text = _format_status_message(user, registrations, matches)

    if isinstance(event, Message):
        await message.answer(status_text, parse_mode="HTML")
    else:
        if hasattr(message, "edit_text"):
            await message.edit_text(
                status_text, parse_mode="HTML", reply_markup=get_main_menu_keyboard()
            )
        await event.answer()
