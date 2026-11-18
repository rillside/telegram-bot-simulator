"""
Telegram Simulator - telebot Echo Bot Example
"""
import telebot
from telebot import apihelper

# 1. Point telebot to the local Telegram Simulator API URL
apihelper.API_URL = "http://127.0.0.1:8000/bot{0}/{1}"

# 2. Insert your local bot token from Telegram Simulator UI
# Example: "1:abc123secret..."
TOKEN = "1:ABxQGCi6k5lCttQZplU2t82hs61JI1JJqyV"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    bot.reply_to(
        message,
        "Привет! Я тестовый бот на pyTelegramBotAPI (telebot), "
        "работающий через локальный Telegram Simulator!"
    )

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.send_message(
        message.chat.id,
        f"Вы написали: {message.text}"
    )

if __name__ == "__main__":
    print("Запуск telebot Echo Bot...")
    bot.infinity_polling()
