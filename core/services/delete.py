import asyncio

from aiogram import Bot


async def _delete_message(
    bot: Bot,
    chat_id: int,
    message_id: int,
) -> None:
    """Helper function to delete a single message safely."""
    for _ in range(3):
        try:
            await bot.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception:
            await asyncio.sleep(0.5)


async def safe_delete_messages(
    bot: Bot,
    chat_id: int,
    message_ids: list[int],
) -> None:
    """Safely delete messages, ignoring errors if messages are already deleted."""
    for message_id in message_ids:
        asyncio.create_task(_delete_message(bot, chat_id, message_id))


async def delayed_delete_messages(
    bot: Bot,
    chat_id: int,
    message_ids: list[int],
    delay: float = 2.0,
) -> None:
    """Delete messages after a specified delay."""
    await asyncio.sleep(delay)
    await safe_delete_messages(bot, chat_id, message_ids)
