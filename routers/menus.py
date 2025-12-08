import asyncio

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from core.db.database_handler import DatabaseHandler
from core.services.texts import get_texts
from core.templates.keyboards.menu import (
    get_main_menu_keyboard,
    get_back_to_main_menu_keyboard,
    get_settings_keyboard,
)

router = Router()


@router.callback_query(F.data == "main_menu")
async def main_menu_handler(
    callback_query: CallbackQuery, state: FSMContext, db: DatabaseHandler
) -> None:
    await state.clear()

    user = await db.get_user(
        callback_query.from_user.id,
    )

    texts = await get_texts(
        unique_names=["greetings"],
        language_code=user.language or "ru",
        db=db,
    )

    await callback_query.message.edit_text(
        texts["greetings"],
        reply_markup=await get_main_menu_keyboard(
            user.language or "en", db, is_admin=user.is_admin
        ),
    )


@router.callback_query(F.data == "rate_button")
async def exchange_button_handler(
    callback_query: CallbackQuery, state: FSMContext, db: DatabaseHandler
) -> None:
    currencies = await db.get_currencies()
    user = await db.get_user(callback_query.from_user.id)
    texts = await get_texts(
        unique_names=["rate_template"], language_code=user.language or "ru", db=db
    )

    text = texts.get("rate_template", "Current exchange rate:")
    for currency in currencies:
        text += f"\n- {currency.name}: {currency.rate}"

    await callback_query.message.edit_text(
        text=text,
        reply_markup=await get_back_to_main_menu_keyboard(user.language or "en", db),
    )


@router.callback_query(F.data == "about_button")
async def about_button_handler(
    callback_query: CallbackQuery, state: FSMContext, db: DatabaseHandler
) -> None:
    user = await db.get_user(callback_query.from_user.id)
    texts, keyboard = await asyncio.gather(
        get_texts(
            unique_names=["about_us_text"], language_code=user.language or "ru", db=db
        ),
        get_back_to_main_menu_keyboard(user.language or "en", db),
    )
    await callback_query.message.edit_text(
        texts["about_us_text"], reply_markup=keyboard
    )


@router.callback_query(F.data == "settings_button")
async def settings_button_handler(
    callback_query: CallbackQuery, state: FSMContext, db: DatabaseHandler
) -> None:
    user = await db.get_user(callback_query.from_user.id)
    texts = await get_texts(
        unique_names=["settings_text"], language_code=user.language or "ru", db=db
    )
    await callback_query.message.edit_text(
        texts["settings_text"],
        reply_markup=await get_settings_keyboard(user.language or "en", db),
    )


@router.callback_query(F.data.startswith("lang_"))
async def change_language_handler(
    callback_query: CallbackQuery, state: FSMContext, db: DatabaseHandler
) -> None:
    language_code = callback_query.data.split("_")[1]
    user = await db.update_user(callback_query.from_user.id, language=language_code)
    texts = await get_texts(
        unique_names=["settings_text"], language_code=language_code, db=db
    )
    await callback_query.message.edit_text(
        texts["settings_text"],
        reply_markup=await get_settings_keyboard(user.language or "en", db),
    )
