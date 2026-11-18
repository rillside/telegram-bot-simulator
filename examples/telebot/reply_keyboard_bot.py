"""
Telegram Simulator - telebot Reply Keyboard Bot Example
"""
import telebot
from telebot import apihelper
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

apihelper.API_URL = "http://127.0.0.1:8000/bot{0}/{1}"

TOKEN = "1:dK-NpGYa1RmUKZcI_5GKbzOfFdfHWX1fpwA"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=["start"])
def send_welcome(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = KeyboardButton("🐍 Изучать Python")
    btn2 = KeyboardButton("🤖 Создавать ботов")
    btn3 = KeyboardButton("❌ Закрыть меню")
    markup.add(btn1, btn2)
    markup.add(btn3)

    bot.send_message(
        message.chat.id,
        "Добро пожаловать в учебный симулятор! Выберите опцию:",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == "🐍 Изучать Python")
def on_python(message):
    bot.send_message(message.chat.id, "Отличный выбор! Python — прекрасный язык для начинающих и профессионалов.")

@bot.message_handler(func=lambda message: message.text == "🤖 Создавать ботов")
def on_bots(message):
    bot.send_message(message.chat.id, "Telegram Simulator позволяет отлаживать ботов локально без интернета!")

@bot.message_handler(func=lambda message: message.text == "❌ Закрыть меню")
def on_close(message):
    bot.send_message(
        message.chat.id,
        "Меню закрыто. Напишите /start, чтобы открыть снова.",
        reply_markup=ReplyKeyboardRemove()
    )

if __name__ == "__main__":
    print("Запуск telebot Reply Keyboard Bot...")
    bot.infinity_polling()
