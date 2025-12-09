from aiogram.types import InlineKeyboardButton, WebAppInfo, InlineKeyboardMarkup

from config import ADMIN_URL
from core.db.database_handler import DatabaseHandler
from core.services.texts import get_texts


async def get_admin_panel_keyboard(
    language_code: str, db: DatabaseHandler
) -> InlineKeyboardMarkup:
    """Get main menu keyboard."""

    texts = await get_texts(
        unique_names=[
            "admin_button",
        ],
        language_code=language_code,
        db=db,
    )

    keyboard_list = [
        [
            InlineKeyboardButton(
                text=texts.get("admin_button", "🛠️ Admin Panel"),
                web_app=WebAppInfo(url=ADMIN_URL),
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard_list)
