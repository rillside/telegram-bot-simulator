"""
Telegram Simulator - aiogram 3 Echo Bot Example
"""
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

TOKEN = "YOUR_BOT_TOKEN_HERE"

API = TelegramAPIServer.from_base("http://127.0.0.1:8000")
session = AiohttpSession(api=API)
bot = Bot(token=TOKEN, session=session)
dp = Dispatcher()

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(
        f"Привет, {message.from_user.full_name}! "
        "Я асинхронный бот на aiogram 3, работающий в локальном симуляторе!"
    )

@dp.message(Command("help"))
async def command_help_handler(message: Message) -> None:
    await message.answer("Просто отправьте мне любое сообщение, и я повторю его.")

@dp.message()
async def echo_handler(message: Message) -> None:
    await message.answer(f"Эхо: {message.text}")

async def main() -> None:
    print("Запуск aiogram 3 Echo Bot...")
    try:
        await dp.start_polling(bot)
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(main())
