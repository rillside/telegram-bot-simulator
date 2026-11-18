"""
Telegram Simulator - aiogram 3 Reply Keyboard Bot Example
"""
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

TOKEN = "1:dK-NpGYa1RmUKZcI_5GKbzOfFdfHWX1fpwA"

API = TelegramAPIServer.from_base("http://127.0.0.1:8000")
session = AiohttpSession(api=API)
bot = Bot(token=TOKEN, session=session)
dp = Dispatcher()

def get_reply_keyboard() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="⚙️ Настройки")],
        [KeyboardButton(text="🚪 Закрыть меню")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(
        "Главное меню открыто. Выберите нужный раздел:",
        reply_markup=get_reply_keyboard()
    )

@dp.message(F.text == "📊 Статистика")
async def stats_handler(message: Message) -> None:
    await message.answer("Все системы работают в штатном режиме: 100% uptime.")

@dp.message(F.text == "⚙️ Настройки")
async def settings_handler(message: Message) -> None:
    await message.answer("Настройки бота сохранены по умолчанию.")

@dp.message(F.text == "🚪 Закрыть меню")
async def close_handler(message: Message) -> None:
    await message.answer("Меню скрыто.", reply_markup=ReplyKeyboardRemove())

async def main() -> None:
    print("Запуск aiogram 3 Reply Keyboard Bot...")
    try:
        await dp.start_polling(bot)
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(main())
