"""Unit tests for reactions handler."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.types import ReactionTypeEmoji

from app.bot.handlers.reactions import (
    get_or_create_user,
    handle_reaction,
    handle_registration_add,
    handle_registration_remove,
    has_emoji,
)
from app.models.registration import Registration
from app.models.session import Session
from app.models.user import User


class TestHasEmoji:
    """Tests for has_emoji helper function."""

    def test_has_emoji_present(self):
        """Test detecting emoji in the reactions list."""
        reactions = [ReactionTypeEmoji(emoji="👍")]
        assert has_emoji(reactions, "👍") is True

    def test_has_emoji_absent(self):
        """Test emoji not in reactions list."""
        reactions = [ReactionTypeEmoji(emoji="❤️")]
        assert has_emoji(reactions, "👍") is False

    def test_has_emoji_empty_list(self):
        """Test the empty reactions list."""
        assert has_emoji([], "👍") is False

    def test_has_emoji_multiple_reactions(self):
        """Test with multiple reactions."""
        reactions = [
            ReactionTypeEmoji(emoji="❤️"),
            ReactionTypeEmoji(emoji="👍"),
            ReactionTypeEmoji(emoji="🎉"),
        ]
        assert has_emoji(reactions, "👍") is True
        assert has_emoji(reactions, "😢") is False


class TestGetOrCreateUser:
    """Tests for get_or_create_user function."""

    @pytest.mark.asyncio
    async def test_get_existing_user(self):
        """Test it getting existing user."""
        mock_session = MagicMock()
        existing_user = User(
            id=1,
            telegram_id=12345,
            username="existing",
            first_name="Existing",
            is_active=True,
        )
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing_user
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.flush = AsyncMock()

        user = await get_or_create_user(mock_session, 12345, "existing", "Existing", None)

        assert user == existing_user
        mock_session.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_new_user(self):
        """Test creating new user."""
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()

        user = await get_or_create_user(mock_session, 12345, "newuser", "New", "User")

        assert user.telegram_id == 12345
        assert user.username == "newuser"
        assert user.first_name == "New"
        assert user.last_name == "User"
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_user_info(self):
        """Test updating user info when changed."""
        mock_session = MagicMock()
        existing_user = User(
            id=1,
            telegram_id=12345,
            username="old_username",
            first_name="Old",
            is_active=True,
        )
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing_user
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.flush = AsyncMock()

        user = await get_or_create_user(mock_session, 12345, "new_username", "New", "Last")

        assert user.username == "new_username"
        assert user.first_name == "New"
        assert user.last_name == "Last"


class TestHandleReaction:
    """Tests for the handle_reaction function."""

    @pytest.mark.asyncio
    async def test_skip_reaction_without_user(self):
        """Test skipping reaction without user info."""
        mock_reaction = MagicMock()
        mock_reaction.user = None
        mock_session = MagicMock()
        mock_session.execute = AsyncMock()

        await handle_reaction(mock_reaction, mock_session)

        mock_session.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_skip_reaction_not_on_announcement(self):
        """Test skipping reaction not on an announcement message."""
        mock_reaction = MagicMock()
        mock_reaction.user = MagicMock(id=12345, username="test")
        mock_reaction.message_id = 999

        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        await handle_reaction(mock_reaction, mock_session)


class TestHandleRegistrationAdd:
    """Tests for the handle_registration_add function."""

    @pytest.mark.asyncio
    async def test_reject_user_without_username(self):
        """Test rejecting user without a username."""
        mock_session = MagicMock()
        mock_reaction = MagicMock()
        mock_reaction.chat = MagicMock(id=-100123)
        mock_reaction.bot = AsyncMock()
        mock_coffee_session = MagicMock(spec=Session)
        mock_telegram_user = MagicMock()
        mock_telegram_user.username = None
        mock_telegram_user.id = 12345
        mock_telegram_user.first_name = "Test"
        mock_session.execute = AsyncMock()

        await handle_registration_add(
            mock_session, mock_reaction, mock_coffee_session, mock_telegram_user
        )

        mock_reaction.bot.send_message.assert_called_once()
        call_args = mock_reaction.bot.send_message.call_args
        assert "username" in call_args.kwargs["text"].lower()

    @pytest.mark.asyncio
    async def test_skip_already_registered(self):
        """Test skipping registration for already registered user."""
        mock_session = MagicMock()
        mock_reaction = MagicMock()
        mock_coffee_session = MagicMock(spec=Session)
        mock_coffee_session.id = 1
        mock_telegram_user = MagicMock()
        mock_telegram_user.username = "testuser"
        mock_telegram_user.id = 12345
        mock_telegram_user.first_name = "Test"
        mock_telegram_user.last_name = None

        with patch("app.bot.handlers.reactions.get_or_create_user") as mock_get_or_create:
            mock_user = User(id=1, telegram_id=12345, username="testuser", is_active=True)
            mock_get_or_create.return_value = mock_user

            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = Registration(
                id=1, user_id=1, session_id=1
            )
            mock_session.execute = AsyncMock(return_value=mock_result)
            mock_session.flush = AsyncMock()

            await handle_registration_add(
                mock_session, mock_reaction, mock_coffee_session, mock_telegram_user
            )

            mock_session.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_new_registration(self):
        """Test creating new registration."""
        mock_session = MagicMock()
        mock_reaction = MagicMock()
        mock_coffee_session = MagicMock(spec=Session)
        mock_coffee_session.id = 1
        mock_telegram_user = MagicMock()
        mock_telegram_user.username = "testuser"
        mock_telegram_user.id = 12345
        mock_telegram_user.first_name = "Test"
        mock_telegram_user.last_name = None

        with patch("app.bot.handlers.reactions.get_or_create_user") as mock_get_or_create:
            mock_user = User(id=1, telegram_id=12345, username="testuser", is_active=True)
            mock_get_or_create.return_value = mock_user

            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = None
            mock_session.execute = AsyncMock(return_value=mock_result)
            mock_session.flush = AsyncMock()
            mock_session.refresh = AsyncMock()

            await handle_registration_add(
                mock_session, mock_reaction, mock_coffee_session, mock_telegram_user
            )

            mock_session.add.assert_called_once()
            added_obj = mock_session.add.call_args[0][0]
            assert isinstance(added_obj, Registration)
            assert added_obj.session_id == 1
            assert added_obj.user_id == 1


class TestHandleRegistrationRemove:
    """Tests for the handle_registration_remove function."""

    @pytest.mark.asyncio
    async def test_remove_registration(self):
        """Test removing registration when the user removes reaction."""
        mock_session = MagicMock()
        mock_reaction = MagicMock()
        mock_coffee_session = MagicMock(spec=Session)
        mock_coffee_session.id = 1
        mock_telegram_user = MagicMock()
        mock_telegram_user.id = 12345

        mock_user = User(id=1, telegram_id=12345, username="testuser", is_active=True)
        mock_user_result = MagicMock()
        mock_user_result.scalar_one_or_none.return_value = mock_user

        mock_registration = Registration(id=1, user_id=1, session_id=1)
        mock_reg_result = MagicMock()
        mock_reg_result.scalar_one_or_none.return_value = mock_registration

        mock_session.execute = AsyncMock(side_effect=[mock_user_result, mock_reg_result])
        mock_session.delete = AsyncMock()
        mock_session.flush = AsyncMock()

        await handle_registration_remove(
            mock_session, mock_reaction, mock_coffee_session, mock_telegram_user
        )

        mock_session.delete.assert_called_once_with(mock_registration)

    @pytest.mark.asyncio
    async def test_remove_registration_user_not_found(self):
        """Test removing registration when user not found."""
        mock_session = MagicMock()
        mock_reaction = MagicMock()
        mock_coffee_session = MagicMock(spec=Session)
        mock_telegram_user = MagicMock()
        mock_telegram_user.id = 12345

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.delete = AsyncMock()

        await handle_registration_remove(
            mock_session, mock_reaction, mock_coffee_session, mock_telegram_user
        )

        mock_session.delete.assert_not_called()
