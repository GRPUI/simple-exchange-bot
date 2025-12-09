import asyncio

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import LEAD_CHAT
from core.db.database_handler import DatabaseHandler
from core.services.delete import safe_delete_messages
from core.services.texts import get_texts
from core.templates.keyboards.payment_orders import (
    get_payment_categories_keyboard,
    get_payment_order_final_keyboard,
)
from core.templates.states.orders import CreatePaymentOrderState

router = Router()


@router.callback_query(F.data == "payment_order_button")
async def payment_order_button_handler(
    callback_query: CallbackQuery, state: FSMContext, db: DatabaseHandler
) -> None:
    await state.set_state(CreatePaymentOrderState.waiting_for_category)
    user = await db.get_user(callback_query.from_user.id)
    texts = await get_texts(
        unique_names=["choose_payment_category"],
        language_code=user.language or "ru",
        db=db,
    )
    await callback_query.message.edit_text(
        texts["choose_payment_category"],
        reply_markup=await get_payment_categories_keyboard(db),
    )


@router.callback_query(StateFilter(CreatePaymentOrderState.waiting_for_category))
async def payment_order_category_handler(
    callback_query: CallbackQuery, state: FSMContext, db: DatabaseHandler
) -> None:
    user = await db.get_user(callback_query.from_user.id)
    texts, category = await asyncio.gather(
        get_texts(
            unique_names=["choose_payment_amount"],
            language_code=user.language or "ru",
            db=db,
        ),
        db.get_payment_category_by_unique_name(
            callback_query.data.split(":")[1], user.language or "ru"
        ),
    )
    await state.update_data(
        category=category.name, order_message=callback_query.message.message_id
    )
    await state.set_state(CreatePaymentOrderState.waiting_for_amount_with_currency)
    await callback_query.message.edit_text(texts["choose_payment_amount"])


@router.message(StateFilter(CreatePaymentOrderState.waiting_for_amount_with_currency))
async def payment_order_amount_with_currency_handler(
    message: Message, state: FSMContext, db: DatabaseHandler
) -> None:
    await safe_delete_messages(message.bot, message.chat.id, [message.message_id])
    data = await state.get_data()
    user = await db.get_user(message.from_user.id)
    texts = await get_texts(
        unique_names=["send_link"],
        language_code=user.language or "ru",
        db=db,
    )
    await state.update_data(amount_with_currency=message.text)
    await state.set_state(CreatePaymentOrderState.waiting_for_link)
    await message.bot.edit_message_text(
        texts["send_link"], chat_id=message.chat.id, message_id=data["order_message"]
    )


@router.message(StateFilter(CreatePaymentOrderState.waiting_for_link))
async def payment_order_link_handler(
    message: Message, state: FSMContext, db: DatabaseHandler
) -> None:
    await safe_delete_messages(message.bot, message.chat.id, [message.message_id])
    data = await state.get_data()
    user = await db.get_user(message.from_user.id)
    texts = await get_texts(
        unique_names=["payment_order_template"],
        language_code=user.language or "ru",
        db=db,
    )
    text = texts["payment_order_template"].format(
        amount_with_currency=data["amount_with_currency"],
        category=data["category"],
        link=message.text,
    )
    await state.update_data(order_text=text)
    await state.set_state(None)
    await message.bot.edit_message_text(
        text,
        chat_id=message.chat.id,
        message_id=data["order_message"],
        reply_markup=await get_payment_order_final_keyboard(
            user.language or "ru", db=db
        ),
    )


@router.callback_query(F.data == "submit_payment_order")
async def submit_payment_order_handler(
    callback_query: CallbackQuery, state: FSMContext, db: DatabaseHandler
) -> None:
    data = await state.get_data()
    user = await db.get_user(callback_query.from_user.id)
    texts = await get_texts(["payment_order_sent"], user.language or "ru", db=db)
    text = (
        f"НОВАЯ ЗАЯВКА от <a href='tg://user?id={callback_query.from_user.id}'>{callback_query.from_user.first_name or 'Клиент'}</a>\n\n"
        + data["order_text"].split("\n\n")[1]
    )
    await callback_query.message.edit_text(texts["payment_order_sent"])
    await callback_query.bot.send_message(
        LEAD_CHAT,
        text=text,
        parse_mode="HTML",
    )


@router.callback_query(F.data == "start_over_payment_order")
async def start_over_payment_order_handler(
    callback_query: CallbackQuery, state: FSMContext, db: DatabaseHandler
) -> None:
    await state.clear()
    await payment_order_button_handler(callback_query, state, db)
