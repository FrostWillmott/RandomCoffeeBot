"""Context utilities for request tracking."""

import contextvars
import uuid

correlation_id: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "correlation_id", default=None
)


def get_correlation_id() -> str:
    """Get or create a correlation ID for the current context."""
    corr_id = correlation_id.get()
    if corr_id is None:
        corr_id = str(uuid.uuid4())
        correlation_id.set(corr_id)
    return corr_id


def set_correlation_id(corr_id: str) -> None:
    """Set correlation ID for the current context."""
    correlation_id.set(corr_id)
