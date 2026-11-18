"""
Telegram Simulator - aiogram 3 Inline Keyboard Bot Example
"""
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "YOUR_BOT_TOKEN_HERE"

API = TelegramAPIServer.from_base("http://127.0.0.1:8000")
session = AiohttpSession(api=API)
bot = Bot(token=TOKEN, session=session)
dp = Dispatcher()

def get_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="⭐ Оценить 5/5", callback_data="rate_5"),
            InlineKeyboardButton(text="👍 Оценить 4/5", callback_data="rate_4")
        ],
        [
            InlineKeyboardButton(text="ℹ️ Справка", callback_data="info")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(
        "Выберите действие из списка:",
        reply_markup=get_keyboard()
    )

@dp.callback_query(F.data.startswith("rate_"))
async def rate_handler(callback: CallbackQuery) -> None:
    rating = callback.data.split("_")[1]
    await callback.answer(f"Спасибо за оценку {rating}/5!", show_alert=False)
    await callback.message.edit_text(f"Вы поставили боту оценку: {rating}/5! 🌟")

@dp.callback_query(F.data == "info")
async def info_handler(callback: CallbackQuery) -> None:
    await callback.answer("Это локальный симулятор Telegram Bot API", show_alert=True)

async def main() -> None:
    print("Запуск aiogram 3 Inline Keyboard Bot...")
    try:
        await dp.start_polling(bot)
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(main())
