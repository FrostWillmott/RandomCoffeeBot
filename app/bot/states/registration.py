"""Registration FSM states."""

from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    """States for user registration flow."""

    waiting_for_confirmation = State()
