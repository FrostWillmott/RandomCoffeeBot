"""Message templates for the bot."""

MATCH_NOTIFICATION_TITLE = "🎉 <b>Вы подобраны для Random Coffee!</b>"
MATCH_NOTIFICATION_USER = "👤 <b>Ваш партнёр:</b> {partner_info}"
MATCH_NOTIFICATION_DATE = "📅 <b>Дата сессии:</b> {session_date}"
MATCH_NOTIFICATION_TOPIC = "📚 <b>Тема для обсуждения:</b> {title}"
MATCH_NOTIFICATION_TOPIC_DESC = "<i>{description}</i>"
MATCH_NOTIFICATION_QUESTIONS = "<b>Вопросы для обсуждения:</b>"
MATCH_NOTIFICATION_RESOURCES = "\n<b>Ресурсы:</b>"
MATCH_NOTIFICATION_FOOTER = (
    "\n<b>Следующие шаги:</b>\n"
    "1️⃣ Свяжитесь с вашим партнёром через Telegram\n"
    "2️⃣ Согласуйте время встречи (рекомендуется 30-60 минут)\n"
    "3️⃣ Выберите формат: Zoom, Google Meet или звонок в Telegram\n"
    "4️⃣ Обсудите назначенную тему вместе\n"
    "5️⃣ Поделитесь отзывом после встречи\n\n"
    "💡 <b>Совет:</b> Начните с знакомства, затем переходите к теме! "
    "Не переживайте, если не знаете всё - это возможность учиться вместе.\n\n"
    "Приятного общения! ☕️"
)

UNMATCHED_NOTIFICATION = (
    "😔 <b>На этот раз пара не найдена</b>\n\n"
    "Мы не смогли найти вам партнёра в этой сессии из-за "
    "нечётного количества участников или ограничений при подборе.\n\n"
    "Не переживайте, в следующей сессии у вас будет <b>приоритет</b>! 🌟\n\n"
    "До встречи в следующий раз! ☕️"
)
