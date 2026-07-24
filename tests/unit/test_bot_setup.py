"""Unit tests for bot/dispatcher setup, keyboards, logging, and message templates."""

import logging
from unittest.mock import MagicMock, patch

import pytest
from aiogram import Bot, Dispatcher

from app.bot import get_bot, get_dispatcher
from app.bot.keyboards import get_main_menu_keyboard
from app.bot.keyboards.inline import get_match_actions_keyboard
from app.resources import messages
from app.utils.logging import setup_logging


class TestBotSetup:
    @pytest.mark.asyncio
    async def test_get_bot(self):
        settings = MagicMock(telegram_bot_token="123456:TEST-token")  # nosec
        with patch("app.bot.get_settings", return_value=settings):
            bot = await get_bot()
        try:
            assert isinstance(bot, Bot)
        finally:
            await bot.session.close()

    def test_get_dispatcher(self):
        dp, throttling_mw = get_dispatcher()

        assert isinstance(dp, Dispatcher)
        assert len(dp.sub_routers) == 6
        assert throttling_mw in dp.message.middleware
        assert throttling_mw in dp.callback_query.middleware


class TestKeyboards:
    def test_main_menu_keyboard(self):
        keyboard = get_main_menu_keyboard()
        callbacks = [
            button.callback_data for row in keyboard.inline_keyboard for button in row
        ]
        assert callbacks == ["register", "status", "help"]

    def test_match_actions_keyboard(self):
        keyboard = get_match_actions_keyboard(42)
        callbacks = [
            button.callback_data for row in keyboard.inline_keyboard for button in row
        ]
        assert callbacks == ["confirm_match:42", "start_feedback:42"]


@pytest.fixture
def restore_root_logger():
    root = logging.getLogger()
    saved_handlers = root.handlers[:]
    saved_level = root.level
    yield
    root.handlers[:] = saved_handlers
    root.setLevel(saved_level)


class TestSetupLogging:
    def test_text_format(self, restore_root_logger):
        setup_logging("DEBUG", "text")

    def test_json_format(self, restore_root_logger):
        setup_logging("INFO", "json")
        root = logging.getLogger()
        assert root.level == logging.INFO
        assert root.handlers

    def test_unknown_level_falls_back_to_info(self, restore_root_logger):
        setup_logging("NOT_A_LEVEL", "json")
        assert logging.getLogger().level == logging.INFO


class TestMessageTemplates:
    def test_templates_format(self):
        assert "Иван" in messages.MATCH_NOTIFICATION_USER.format(partner_info="Иван")
        assert "2026-07-27" in messages.MATCH_NOTIFICATION_DATE.format(
            session_date="2026-07-27"
        )
        assert "тема" in messages.MATCH_NOTIFICATION_TOPIC.format(title="тема")
        assert messages.UNMATCHED_NOTIFICATION
        assert messages.MATCH_NOTIFICATION_FOOTER
