from aiogram.fsm.state import StatesGroup, State


class CreateOrderState(StatesGroup):
    """State for editing a product."""

    waiting_for_amount = State()
    waiting_for_currency = State()
    waiting_for_account_number = State()
    waiting_for_bank = State()
    waiting_for_receiver = State()

    @staticmethod
    def return_state(field: str) -> State:
        """Return the state corresponding to the given field."""
        state_mapping = {
            "amount": CreateOrderState.waiting_for_amount,
            "currency": CreateOrderState.waiting_for_currency,
            "account_number": CreateOrderState.waiting_for_account_number,
            "bank": CreateOrderState.waiting_for_bank,
            "receiver": CreateOrderState.waiting_for_receiver,
        }
        return state_mapping.get(field)


class CreatePaymentOrderState(StatesGroup):
    waiting_for_category = State()
    waiting_for_amount_with_currency = State()
    waiting_for_link = State()
