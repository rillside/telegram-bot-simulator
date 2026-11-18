# Примеры подключения библиотек

В данном руководстве подробно рассмотрены примеры кода для работы с Telegram Simulator.

Все примеры доступны в директории `examples/` репозитория.

---

## 1. pyTelegramBotAPI (telebot)

Для подключения библиотеки `telebot` достаточно настроить свойство `apihelper.API_URL`:

```python
import telebot
from telebot import apihelper

# Переопределяем шаблон URL официального API на локальный эмулятор
apihelper.API_URL = "http://127.0.0.1:8000/bot{0}/{1}"

# Токен берется из интерфейса Telegram Simulator
bot = telebot.TeleBot("1:SIMULATOR_TOKEN")


@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я работаю локально через Telegram Simulator!")


@bot.message_handler(func=lambda msg: True)
def echo(message):
    bot.send_message(message.chat.id, f"Вы сказали: {message.text}")


if __name__ == "__main__":
    bot.infinity_polling()
```

### Инлайн-кнопки в telebot

```python
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

markup = InlineKeyboardMarkup()
btn1 = InlineKeyboardButton("👍 Нравится", callback_data="like")
btn2 = InlineKeyboardButton("👎 Не нравится", callback_data="dislike")
markup.row(btn1, btn2)

bot.send_message(chat_id, "Оцените работу:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def on_callback(call):
    if call.data == "like":
        bot.answer_callback_query(call.id, "Спасибо!")
        bot.edit_message_text("Вы нажали «Нравится»!", call.message.chat.id, call.message.message_id)
```

---

## 2. aiogram 3

В библиотеке `aiogram 3` переопределение API осуществляется через класс `TelegramAPIServer` и кастомную HTTP-сессию `AiohttpSession`:

```python
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.filters import CommandStart
from aiogram.types import Message

# Настройка локального сервера API
API = TelegramAPIServer.from_base("http://127.0.0.1:8000")
session = AiohttpSession(api=API)

bot = Bot(token="1:SIMULATOR_TOKEN", session=session)
dp = Dispatcher()


@dp.message(CommandStart())
async def start_handler(message: Message) -> None:
    await message.answer(
        f"Здравствуйте, {message.from_user.full_name}! "
        "Бот успешно запущен в среде симулятора."
    )


@dp.message()
async def echo_handler(message: Message) -> None:
    await message.answer(f"Эхо: {message.text}")


async def main() -> None:
    try:
        await dp.start_polling(bot)
    finally:
        await session.close()


if __name__ == "__main__":
    asyncio.run(main())
```

### Инлайн-кнопки в aiogram 3

```python
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram import F

kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Кнопка 1", callback_data="btn_1")]
])

await message.answer("Выберите вариант:", reply_markup=kb)

@dp.callback_query(F.data == "btn_1")
async def on_button(callback: CallbackQuery):
    await callback.answer("Уведомление получено!")
    await callback.message.edit_text("Кнопка успешно обработана!")
```

---

## 3. Запуск пользовательского кода

Пользовательский код может быть запущен:
1. **Через интерфейс симулятора**: перейдите в правое меню информации о боте, введите путь к скрипту (например `examples/telebot/echo_bot.py`) и нажмите «Запустить бота».
2. **Внешне из вашей IDE** (VS Code, PyCharm, терминал): просто запустите ваш `.py` скрипт. Он автоматически соединится с локальным сервером `http://127.0.0.1:8000` и начнет обрабатывать сообщения из веб-интерфейса.
