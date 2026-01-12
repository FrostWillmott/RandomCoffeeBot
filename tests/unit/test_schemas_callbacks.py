"""Tests for callback schemas."""

import pytest

from app.schemas.callbacks import (
    ConfirmMatchCallback,
    RatingCallback,
    StartFeedbackCallback,
    SuggestTimeCallback,
    parse_callback_data,
)


class TestConfirmMatchCallback:
    """Tests for ConfirmMatchCallback schema."""

    def test_from_callback_data_valid(self):
        """Test parsing valid confirm_match callback."""
        callback = ConfirmMatchCallback.from_callback_data("confirm_match:123")
        assert callback.match_id == 123

    def test_from_callback_data_invalid_format(self):
        """Test parsing invalid format."""
        with pytest.raises(ValueError, match="Invalid confirm_match callback"):
            ConfirmMatchCallback.from_callback_data("invalid:123")

    def test_from_callback_data_missing_id(self):
        """Test parsing callback without ID."""
        with pytest.raises(ValueError):
            ConfirmMatchCallback.from_callback_data("confirm_match:")

    def test_match_id_validation(self):
        """Test that match_id must be positive."""
        with pytest.raises(ValueError):
            ConfirmMatchCallback(match_id=-1)


class TestSuggestTimeCallback:
    """Tests for SuggestTimeCallback schema."""

    def test_from_callback_data_valid(self):
        """Test parsing valid suggest_time callback."""
        callback = SuggestTimeCallback.from_callback_data("suggest_time:456")
        assert callback.match_id == 456

    def test_from_callback_data_invalid_format(self):
        """Test parsing invalid format."""
        with pytest.raises(ValueError, match="Invalid suggest_time callback"):
            SuggestTimeCallback.from_callback_data("invalid:456")


class TestStartFeedbackCallback:
    """Tests for StartFeedbackCallback schema."""

    def test_from_callback_data_valid(self):
        """Test parsing valid start_feedback callback."""
        callback = StartFeedbackCallback.from_callback_data("start_feedback:789")
        assert callback.match_id == 789

    def test_from_callback_data_invalid_format(self):
        """Test parsing invalid format."""
        with pytest.raises(ValueError, match="Invalid start_feedback callback"):
            StartFeedbackCallback.from_callback_data("invalid:789")


class TestRatingCallback:
    """Tests for RatingCallback schema."""

    def test_from_callback_data_valid(self):
        """Test parsing valid rating callback."""
        for rating in range(1, 6):
            callback = RatingCallback.from_callback_data(f"rating:{rating}")
            assert callback.rating == rating

    def test_from_callback_data_invalid_rating_too_low(self):
        """Test parsing rating below 1."""
        with pytest.raises(ValueError, match="Rating must be between 1 and 5"):
            RatingCallback.from_callback_data("rating:0")

    def test_from_callback_data_invalid_rating_too_high(self):
        """Test parsing rating above 5."""
        with pytest.raises(ValueError, match="Rating must be between 1 and 5"):
            RatingCallback.from_callback_data("rating:6")

    def test_from_callback_data_invalid_format(self):
        """Test parsing invalid format."""
        with pytest.raises(ValueError, match="Invalid rating callback"):
            RatingCallback.from_callback_data("invalid:3")


class TestParseCallbackData:
    """Tests for parse_callback_data function."""

    def test_parse_confirm_match(self):
        """Test parsing confirm_match callback."""
        result = parse_callback_data("confirm_match:123")
        assert isinstance(result, ConfirmMatchCallback)
        assert result.match_id == 123

    def test_parse_suggest_time(self):
        """Test parsing suggest_time callback."""
        result = parse_callback_data("suggest_time:456")
        assert isinstance(result, SuggestTimeCallback)
        assert result.match_id == 456

    def test_parse_start_feedback(self):
        """Test parsing start_feedback callback."""
        result = parse_callback_data("start_feedback:789")
        assert isinstance(result, StartFeedbackCallback)
        assert result.match_id == 789

    def test_parse_rating(self):
        """Test parsing rating callback."""
        result = parse_callback_data("rating:5")
        assert isinstance(result, RatingCallback)
        assert result.rating == 5

    def test_parse_invalid_format_no_colon(self):
        """Test parsing callback without a colon."""
        with pytest.raises(ValueError, match="Invalid callback data format"):
            parse_callback_data("invalid")

    def test_parse_invalid_format_empty(self):
        """Test parsing empty callback."""
        with pytest.raises(ValueError, match="Invalid callback data format"):
            parse_callback_data("")

    def test_parse_unknown_action(self):
        """Test parsing unknown action."""
        with pytest.raises(ValueError, match="Unknown callback action"):
            parse_callback_data("unknown_action:123")
