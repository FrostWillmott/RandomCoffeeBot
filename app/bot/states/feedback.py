"""Feedback FSM states."""

from aiogram.fsm.state import State, StatesGroup


class FeedbackStates(StatesGroup):
    """States for the feedback workflow."""

    waiting_for_rating = State()
    waiting_for_comment = State()
