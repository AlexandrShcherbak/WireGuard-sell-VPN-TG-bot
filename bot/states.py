from aiogram.fsm.state import State, StatesGroup


class SupportState(StatesGroup):
    waiting_for_message = State()


class PaymentState(StatesGroup):
    waiting_for_method = State()
    waiting_for_confirmation = State()


class AdminState(StatesGroup):
    waiting_for_broadcast_text = State()
    waiting_for_user_id = State()
