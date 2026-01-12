"""Pydantic schemas for callback data validation."""

from pydantic import BaseModel, Field


class ConfirmMatchCallback(BaseModel):
    """Schema for confirm_match callback."""

    match_id: int = Field(..., gt=0, description="Match ID to confirm")

    @classmethod
    def from_callback_data(cls, data: str) -> "ConfirmMatchCallback":
        """Parse callback data string into schema."""
        parts = data.split(":", 1)
        if len(parts) != 2 or parts[0] != "confirm_match":
            raise ValueError(f"Invalid confirm_match callback data: {data}")
        return cls(match_id=int(parts[1]))


class SuggestTimeCallback(BaseModel):
    """Schema for suggest_time callback."""

    match_id: int = Field(..., gt=0, description="Match ID for time suggestion")

    @classmethod
    def from_callback_data(cls, data: str) -> "SuggestTimeCallback":
        """Parse callback data string into schema."""
        parts = data.split(":", 1)
        if len(parts) != 2 or parts[0] != "suggest_time":
            raise ValueError(f"Invalid suggest_time callback data: {data}")
        return cls(match_id=int(parts[1]))


class StartFeedbackCallback(BaseModel):
    """Schema for start_feedback callback."""

    match_id: int = Field(..., gt=0, description="Match ID for feedback")

    @classmethod
    def from_callback_data(cls, data: str) -> "StartFeedbackCallback":
        """Parse callback data string into schema."""
        parts = data.split(":", 1)
        if len(parts) != 2 or parts[0] != "start_feedback":
            raise ValueError(f"Invalid start_feedback callback data: {data}")
        return cls(match_id=int(parts[1]))


class RatingCallback(BaseModel):
    """Schema for rating callback."""

    rating: int = Field(..., ge=1, le=5, description="Rating value (1-5)")

    @classmethod
    def from_callback_data(cls, data: str) -> "RatingCallback":
        """Parse callback data string into schema."""
        parts = data.split(":", 1)
        if len(parts) != 2 or parts[0] != "rating":
            raise ValueError(f"Invalid rating callback data: {data}")
        rating_value = int(parts[1])
        if not (1 <= rating_value <= 5):
            raise ValueError(f"Rating must be between 1 and 5, got {rating_value}")
        return cls(rating=rating_value)


def parse_callback_data(data: str) -> BaseModel:
    """Parse callback data and return appropriate schema.

    Args:
        data: Callback data string (e.g., "confirm_match:123")

    Returns:
        Parsed callback schema

    Raises:
        ValueError: If callback data format is invalid
    """
    if not data or ":" not in data:
        raise ValueError(f"Invalid callback data format: {data}")

    action = data.split(":", 1)[0]

    if action == "confirm_match":
        return ConfirmMatchCallback.from_callback_data(data)
    elif action == "suggest_time":
        return SuggestTimeCallback.from_callback_data(data)
    elif action == "start_feedback":
        return StartFeedbackCallback.from_callback_data(data)
    elif action == "rating":
        return RatingCallback.from_callback_data(data)
    else:
        raise ValueError(f"Unknown callback action: {action}")
