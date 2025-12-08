from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core.db.database_handler import DatabaseHandler
from core.services.texts import get_texts
from core.templates.keyboards.menu import (
    get_main_menu_keyboard,
)

router = Router()


def strip_bot_suffix(text: str) -> str:
    """
    Return the command text without a trailing "@BotName" part
    that Telegram adds in groups, e.g. "/u_123@Meeting_Bot" -> "/u_123".
    """
    return text.split("@", 1)[0]


@router.message(Command("start"))
async def start_command_handler(
    message: Message, db: DatabaseHandler, state: FSMContext
) -> None:
    """Handle /start command by initializing user and sending greeting with the main menu."""
    await state.clear()

    user_language = message.from_user.language_code or "en"
    user = await db.create_or_get_user(
        user_tg_id=int(message.from_user.id),
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        username=message.from_user.username,
        language=user_language,
    )

    texts = await get_texts(
        unique_names=["greetings"],
        language_code=user.language or "en",
        db=db,
    )

    await message.answer(
        texts["greetings"],
        reply_markup=await get_main_menu_keyboard(
            user.language or "en", db, is_admin=user.is_admin
        ),
    )


@router.message(Command("admin"))
async def admin_command_handler(
    message: Message, db: DatabaseHandler, state: FSMContext
):
    pass
