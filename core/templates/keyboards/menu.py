from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from core.db.database_handler import DatabaseHandler
from core.services.texts import get_texts


async def get_main_menu_keyboard(
    language_code: str, db: DatabaseHandler, is_admin: bool = False
) -> InlineKeyboardMarkup:
    """Get main menu keyboard."""

    texts = await get_texts(
        unique_names=[
            "exchange_button",
            "rate_button",
            "about_button",
            "settings_button",
            "admin_button",
        ],
        language_code=language_code,
        db=db,
    )

    keyboard_list = [
        [
            InlineKeyboardButton(
                text=texts.get("exchange_button", "📚 Exchange"),
                callback_data="exchange_button",
            ),
        ],
        [
            InlineKeyboardButton(
                text=texts.get("rate_button", "📊 Get Rate"),
                callback_data="rate_button",
            ),
            InlineKeyboardButton(
                text=texts.get("about_button", "ℹ️ About Us"),
                callback_data="about_button",
            ),
        ],
        [
            InlineKeyboardButton(
                text=texts.get("settings_button", "⚙️ Settings"),
                callback_data="settings_button",
            ),
        ],
    ]
    if is_admin:
        keyboard_list.append(
            [
                InlineKeyboardButton(
                    text=texts.get("admin_button", "🛠️ Admin Panel"),
                    callback_data="admin_button",
                ),
            ],
        )
    return InlineKeyboardMarkup(inline_keyboard=keyboard_list)


async def get_back_to_main_menu_keyboard(
    language_code: str, db: DatabaseHandler
) -> InlineKeyboardMarkup:
    texts = await get_texts(
        unique_names=["back_to_main_menu_button"],
        language_code=language_code,
        db=db,
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=texts.get("back_to_main_menu_button", "🏠 Back to Main Menu"),
                    callback_data="main_menu",
                )
            ]
        ]
    )
    return keyboard


async def get_settings_keyboard(
    language_code: str, db: DatabaseHandler
) -> InlineKeyboardMarkup:
    texts = await get_texts(
        unique_names=["back_to_main_menu_button"],
        language_code=language_code,
        db=db,
    )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
                InlineKeyboardButton(text="🇺🇸 English", callback_data="lang_en"),
            ],
            [
                InlineKeyboardButton(
                    text=texts.get("back_to_main_menu_button", "🏠 Back to Main Menu"),
                    callback_data="main_menu",
                )
            ],
        ]
    )
    return keyboard
