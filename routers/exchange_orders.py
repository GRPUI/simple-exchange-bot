import asyncio
import re

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import LEAD_CHAT
from core.db.database_handler import DatabaseHandler
from core.services.delete import safe_delete_messages
from core.services.texts import get_texts
from core.templates.keyboards.orders import (
    get_currencies_keyboard,
    get_order_final_keyboard,
)
from core.templates.states.orders import CreateOrderState

router = Router()


@router.callback_query(F.data == "exchange_button")
async def exchange_button_handler(
    callback_query: CallbackQuery, state: FSMContext, db: DatabaseHandler
) -> None:

    await state.set_state(CreateOrderState.waiting_for_amount)
    user = await db.get_user(callback_query.from_user.id)
    texts = await get_texts(
        unique_names=["enter_amount_text"],
        language_code=user.language or "ru",
        db=db,
    )
    await state.update_data(order_message=callback_query.message.message_id)
    await callback_query.message.edit_text(texts["enter_amount_text"])


@router.message(StateFilter(CreateOrderState.waiting_for_amount))
async def exchange_order_handler(
    message: Message, state: FSMContext, db: DatabaseHandler
) -> None:
    data = await state.get_data()
    amount = message.text.replace(",", ".")
    user, keyboard = await asyncio.gather(
        db.get_user(message.from_user.id), get_currencies_keyboard(db)
    )
    texts = await get_texts(
        unique_names=["incorrect_amount", "choose_currency_to_exchange"],
        language_code=user.language or "ru",
        db=db,
    )
    await safe_delete_messages(message.bot, message.chat.id, [message.message_id])
    try:
        amount = float(amount)
        await state.update_data(amount=amount)
    except ValueError:
        await message.bot.edit_message_text(
            texts["incorrect_amount"],
            chat_id=message.chat.id,
            message_id=data["order_message"],
        )
        return
    await state.set_state(CreateOrderState.waiting_for_currency)
    await message.bot.edit_message_text(
        texts["choose_currency_to_exchange"],
        chat_id=message.chat.id,
        message_id=data["order_message"],
        reply_markup=await get_currencies_keyboard(db),
    )


@router.callback_query(StateFilter(CreateOrderState.waiting_for_currency))
async def exchange_currency_handler(
    callback_query: CallbackQuery, state: FSMContext, db: DatabaseHandler
) -> None:
    currency_symbol = callback_query.data.split("_")[1]
    await state.update_data(currency_symbol=currency_symbol)
    await state.set_state(CreateOrderState.waiting_for_account_number)
    user = await db.get_user(callback_query.from_user.id)
    texts = await get_texts(
        unique_names=["enter_account_number"],
        language_code=user.language or "ru",
        db=db,
    )
    await state.update_data(currency_symbol=currency_symbol)
    await callback_query.message.edit_text(texts["enter_account_number"])


@router.message(StateFilter(CreateOrderState.waiting_for_account_number))
async def exchange_account_number_handler(
    message: Message, state: FSMContext, db: DatabaseHandler
) -> None:
    """Обработчик ввода номера счета (телефон или карта)"""

    ACCOUNT_NUMBER_PATTERN = re.compile(
        r"^(?:" r"(?:\+?[\d\s\-()]{10,})|" r"(?:\d[\d\s\-]{13,})" r")$"
    )

    account_number = message.text.strip()
    user = await db.get_user(message.from_user.id)
    data = await state.get_data()

    texts = await get_texts(
        ["invalid_account_number", "enter_bank"], user.language or "ru", db=db
    )

    await safe_delete_messages(message.bot, message.chat.id, [message.message_id])

    if not ACCOUNT_NUMBER_PATTERN.match(account_number):
        await message.bot.edit_message_text(
            texts.get("invalid_account_number"),
            chat_id=message.chat.id,
            message_id=data["order_message"],
        )
        return

    cleaned_account = re.sub(r"[\s\-()]+", "", account_number)

    if len(cleaned_account) < 10:
        await message.bot.edit_message_text(
            texts.get("invalid_account_number"),
            chat_id=message.chat.id,
            message_id=data["order_message"],
        )
        return

    await state.update_data(account_number=cleaned_account)

    await state.set_state(CreateOrderState.waiting_for_bank)

    await message.bot.edit_message_text(
        texts.get("enter_bank"),
        chat_id=message.chat.id,
        message_id=data["order_message"],
    )


@router.message(StateFilter(CreateOrderState.waiting_for_bank))
async def exchange_bank_handler(
    message: Message, state: FSMContext, db: DatabaseHandler
) -> None:
    await state.set_state(CreateOrderState.waiting_for_receiver)
    user = await db.get_user(message.from_user.id)
    texts = await get_texts(["enter_receiver"], user.language or "ru", db=db)
    data = await state.get_data()
    await state.update_data(bank=message.text)
    await message.bot.edit_message_text(
        texts.get("enter_receiver"),
        chat_id=message.chat.id,
        message_id=data["order_message"],
    )

    await safe_delete_messages(message.bot, message.chat.id, [message.message_id])


@router.message(StateFilter(CreateOrderState.waiting_for_receiver))
async def exchange_receiver_handler(
    message: Message, state: FSMContext, db: DatabaseHandler
) -> None:
    await safe_delete_messages(message.bot, message.chat.id, [message.message_id])
    data = await state.get_data()
    user, currency = await asyncio.gather(
        db.get_user(message.from_user.id),
        db.get_currency_by_symbol(data["currency_symbol"]),
    )
    texts = await get_texts(
        ["order_application_template"], user.language or "ru", db=db
    )
    await state.update_data(receiver=message.text)
    text = texts["order_application_template"].format(
        amount=data["amount"],
        currency_name=currency.name,
        account_number=data["account_number"],
        bank=data["bank"],
        receiver=message.text,
    )
    await state.update_data(order_text=text)
    await state.set_state(None)
    await message.bot.edit_message_text(
        text,
        chat_id=message.chat.id,
        message_id=data["order_message"],
        reply_markup=await get_order_final_keyboard(user.language or "ru", db=db),
    )


@router.callback_query(F.data == "submit_order")
async def submit_order_handler(
    callback_query: CallbackQuery, state: FSMContext, db: DatabaseHandler
) -> None:
    data = await state.get_data()
    user = await db.get_user(callback_query.from_user.id)
    texts = await get_texts(["order_sent"], user.language or "ru", db=db)

    text = (
        f"НОВАЯ ЗАЯВКА от <a href='tg://user?id={callback_query.from_user.id}'>{callback_query.from_user.first_name or 'Клиент'}</a>\n\n"
        + data["order_text"].split("\n\n")[1]
    )

    await callback_query.message.edit_text(texts["order_sent"])
    await callback_query.bot.send_message(
        LEAD_CHAT,
        text=text,
        parse_mode="HTML",
    )


@router.callback_query(F.data == "start_over")
async def start_over_handler(
    callback_query: CallbackQuery, state: FSMContext, db: DatabaseHandler
) -> None:
    await state.clear()
    await exchange_button_handler(callback_query, state, db)
