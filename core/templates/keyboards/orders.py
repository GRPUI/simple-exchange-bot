from itertools import zip_longest

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from core.db.database_handler import DatabaseHandler
from core.services.texts import get_texts


async def get_currencies_keyboard(db: DatabaseHandler) -> InlineKeyboardMarkup:
    currencies = await db.get_currencies()
    keyboard_list = []

    buttons = [
        InlineKeyboardButton(
            text=currency.name, callback_data=f"currency_{currency.symbol}"
        )
        for currency in currencies
    ]

    for button1, button2 in zip_longest(buttons[::2], buttons[1::2], fillvalue=None):
        row = [button1]
        if button2:
            row.append(button2)
        keyboard_list.append(row)

    return InlineKeyboardMarkup(inline_keyboard=keyboard_list)


async def get_order_final_keyboard(language: str, db: DatabaseHandler):
    texts = await get_texts(
        unique_names=["submit_button", "start_over_button"],
        language_code=language,
        db=db,
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=texts.get("submit_button"), callback_data="submit_order"
                )
            ],
            [
                InlineKeyboardButton(
                    text=texts.get("start_over_button"), callback_data="start_over"
                )
            ],
        ]
    )
    return keyboard
