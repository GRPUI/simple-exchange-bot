import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from loguru import logger

from config import BOT_TOKEN, DB_URL
from core.db.database_handler import DatabaseHandler
from core.middlewares.throttling import ThrottlingMiddleware
from routers import commands, admin, orders, menus


async def main() -> None:
    logger.info("Starting bot")

    dp = Dispatcher()
    bot = Bot(token=BOT_TOKEN)

    db = DatabaseHandler(DB_URL)

    await db.init()

    dp["db"] = db
    dp.include_routers(commands.router, admin.router, orders.router, menus.router)
    dp.message.middleware(ThrottlingMiddleware())

    bot_commands = [
        BotCommand(command="/start", description="Запуск / перезапуск бота 🚀"),
    ]
    await bot.set_my_commands(bot_commands)

    logger.info("Bot commands set")
    await logger.complete()
    await dp.start_polling(bot)


if __name__ == "__main__":
    logger.add("logs.log", level="INFO", rotation="1 week")
    asyncio.run(main())
