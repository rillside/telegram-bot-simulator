"""
Telegram Simulator - pyTelegramBotAPI (telebot) Echo Bot Example
=================================================================
Пример эхо-бота на библиотеке pyTelegramBotAPI (telebot),
работающего с локальным эмулятором Telegram Bot API.
"""

import telebot

# =====================================================================
# [ПОДМЕНА API ДЛЯ ЛОКАЛЬНОГО СИМУЛЯТОРА]
# =====================================================================
# 1. Импортируем служебный модуль сетевых настроек telebot:
from telebot import apihelper

# 2. Перенаправляем базовый шаблон URL на локальный симулятор:
#    {0} — токен бота, {1} — имя метода API (getMe, sendMessage и др.)
apihelper.API_URL = "http://127.0.0.1:8000/bot{0}/{1}"
# =====================================================================

TOKEN = "YOUR_TOKEN"

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=["start"])
def send_welcome(message):
    """Приветственное сообщение по команде /start."""
    user_name = message.from_user.first_name or "Пользователь"
    bot.reply_to(
        message,
        f"👋 Привет, {user_name}!\n\n"
        f"Я тестовый эхо-бот на **pyTelegramBotAPI** (`telebot`).\n"
        f"Я работаю локально через **Telegram Simulator** без интернета!\n\n"
        f"Отправь мне любое текстовое сообщение, и я повторю его в ответ.\n"
        f"Доступные команды: /start, /help, /info",
        parse_mode="Markdown"
    )


@bot.message_handler(commands=["help"])
def send_help(message):
    """Справка по доступным командам."""
    bot.send_message(
        message.chat.id,
        "ℹ️ **Справка по боту:**\n\n"
        "• Напиши любой текст — бот ответит эхом.\n"
        "• /start — перезапустить приветствие.\n"
        "• /info — посмотреть информацию о текущем чате и пользователе.\n"
        "• /help — показать это сообщение.",
        parse_mode="Markdown"
    )


@bot.message_handler(commands=["info"])
def send_info(message):
    """Информация о пользователе и чате."""
    user = message.from_user
    chat = message.chat
    bot.reply_to(
        message,
        f"👤 **Информация о пользователе:**\n"
        f"• ID: `{user.id}`\n"
        f"• Имя: `{user.first_name}`\n"
        f"• Username: `@{user.username or 'нет'}`\n\n"
        f"💬 **Информация о чате:**\n"
        f"• Chat ID: `{chat.id}`\n"
        f"• Тип: `{chat.type}`",
        parse_mode="Markdown"
    )


@bot.message_handler(content_types=["text"])
def echo_all(message):
    """Эхо-ответ на любое входящее текстовое сообщение."""
    bot.send_message(
        message.chat.id,
        f"🔁 Вы написали: {message.text}"
    )


@bot.message_handler(content_types=["photo", "document"])
def handle_media(message):
    """Обработка отправки файлов и фотографий."""
    caption = message.caption or "без подписи"
    content_name = "фотографию" if message.photo else "документ"
    bot.reply_to(
        message,
        f"📷 Получил {content_name}! Подпись: {caption}"
    )


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Запуск telebot Echo Bot в локальном Telegram Simulator...")
    print(f"📡 API URL: {apihelper.API_URL.format(TOKEN, '')}")
    print("💬 Откройте веб-интерфейс http://127.0.0.1:8000 и напишите боту!")
    print("=" * 60)
    bot.infinity_polling()
