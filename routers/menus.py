import asyncio
from decimal import Decimal

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
    user = await db.get_user(callback_query.from_user.id)
    texts = await get_texts(
        unique_names=["rate_template", "no_currency_pairs"],
        language_code=user.language or "ru",
        db=db,
    )

    currency_pairs = await db.get_currency_pairs()

    if not currency_pairs:
        text = texts["no_currency_pairs"]
    else:
        text = texts.get("rate_template", "Current exchange rates:")
        for pair in currency_pairs:
            from_name = pair.from_currency.name
            to_name = pair.to_currency.name
            rate = pair.rate.quantize(Decimal("0.001"))
            text += f"\n- {from_name} → {to_name}: {rate}"

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


@router.callback_query(F.data == "agree_button")
async def agree_terms_handler(
    callback_query: CallbackQuery, state: FSMContext, db: DatabaseHandler
) -> None:
    await db.update_user(callback_query.from_user.id, is_agreed_with_terms=True)
    await main_menu_handler(callback_query, state, db)
