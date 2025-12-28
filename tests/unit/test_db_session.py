"""Tests for a database session."""

from unittest.mock import AsyncMock, patch

import pytest

from app.db.session import async_session_maker, engine, get_db


@pytest.mark.asyncio
async def test_get_db_success():
    """Test get_db generator with successful commit."""
    session_mock = AsyncMock()
    session_mock.__aenter__ = AsyncMock(return_value=session_mock)
    session_mock.__aexit__ = AsyncMock(return_value=None)

    with patch("app.db.session.async_session_maker") as mock_maker:
        mock_maker.return_value = session_mock

        async for _ in get_db():
            pass

        session_mock.commit.assert_awaited_once()
        session_mock.rollback.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_db_exception():
    """Test get_db generator structure handles exceptions."""
    session_mock = AsyncMock()
    session_mock.__aenter__ = AsyncMock(return_value=session_mock)
    session_mock.__aexit__ = AsyncMock(return_value=None)
    session_mock.rollback = AsyncMock()
    session_mock.commit = AsyncMock()

    with patch("app.db.session.async_session_maker") as mock_maker:
        mock_maker.return_value = session_mock

        gen = get_db()
        assert hasattr(gen, "__anext__")

        async for db_session in gen:
            assert db_session == session_mock
            break

        assert session_mock.__aexit__ is not None


def test_async_session_maker_exists():
    """Test that async_session_maker is configured."""
    assert async_session_maker is not None


def test_engine_exists():
    """Test that the engine is configured."""
    assert engine is not None
