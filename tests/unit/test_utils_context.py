"""Tests for context utilities."""

from app.utils.context import (
    correlation_id,
    get_correlation_id,
    set_correlation_id,
)


def test_get_correlation_id_creates_new():
    """Test that get_correlation_id creates a new ID if none exists."""
    try:
        correlation_id.set(None)
    except LookupError:
        pass

    corr_id = get_correlation_id()
    assert corr_id is not None
    assert isinstance(corr_id, str)
    assert len(corr_id) > 0


def test_get_correlation_id_returns_existing():
    """Test that get_correlation_id returns existing ID."""
    test_id = "test-correlation-id-123"
    set_correlation_id(test_id)

    corr_id = get_correlation_id()
    assert corr_id == test_id


def test_set_correlation_id():
    """Test setting correlation ID."""
    test_id = "test-id-456"
    set_correlation_id(test_id)

    current_id = correlation_id.get()
    assert current_id == test_id


def test_correlation_id_persistence():
    """Test that correlation ID persists in the same context."""
    test_id = "persistent-id-789"
    set_correlation_id(test_id)

    assert get_correlation_id() == test_id
    assert get_correlation_id() == test_id
    assert get_correlation_id() == test_id
