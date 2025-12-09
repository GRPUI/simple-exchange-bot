from itertools import zip_longest

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from core.db.database_handler import DatabaseHandler
from core.services.texts import get_texts


async def get_payment_categories_keyboard(db: DatabaseHandler) -> InlineKeyboardMarkup:
    categories = await db.get_payment_categories()
    keyboard_list = []

    buttons = [
        InlineKeyboardButton(
            text=category.name, callback_data=f"payment_category:{category.unique_name}"
        )
        for category in categories
    ]

    for button1, button2 in zip_longest(buttons[::2], buttons[1::2], fillvalue=None):
        row = [button1]
        if button2:
            row.append(button2)
        keyboard_list.append(row)

    return InlineKeyboardMarkup(inline_keyboard=keyboard_list)


async def get_payment_order_final_keyboard(language: str, db: DatabaseHandler):
    texts = await get_texts(
        unique_names=["submit_button", "start_over_button"],
        language_code=language,
        db=db,
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=texts.get("submit_button"),
                    callback_data="submit_payment_order",
                )
            ],
            [
                InlineKeyboardButton(
                    text=texts.get("start_over_button"),
                    callback_data="start_over_payment_order",
                )
            ],
        ]
    )
    return keyboard
