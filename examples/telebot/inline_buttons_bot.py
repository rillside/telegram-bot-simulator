"""
Telegram Simulator - telebot Inline Keyboard Bot Example
"""
import telebot
from telebot import apihelper
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

apihelper.API_URL = "http://127.0.0.1:8000/bot{0}/{1}"

TOKEN = "1:ABxQGCi6k5lCttQZplU2t82hs61JI1JJqyV"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=["start", "menu"])
def send_menu(message):
    markup = InlineKeyboardMarkup(row_width=2)
    btn1 = InlineKeyboardButton("👍 Нравится", callback_data="like")
    btn2 = InlineKeyboardButton("👎 Не нравится", callback_data="dislike")
    btn3 = InlineKeyboardButton("ℹ️ О проекте", callback_data="info")
    markup.add(btn1, btn2)
    markup.add(btn3)

    bot.send_message(
        message.chat.id,
        "Выберите действие:",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == "like":
        bot.answer_callback_query(call.id, "Спасибо за отзыв! 🎉", show_alert=True)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Вы поставили отметку «👍 Нравится»!"
        )
    elif call.data == "dislike":
        bot.answer_callback_query(call.id, "Мы исправимся! 🛠", show_alert=True)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Вы поставили отметку «👎 Не нравится»."
        )
    elif call.data == "info":
        bot.answer_callback_query(call.id, "Telegram Simulator v1.0", show_alert=False)

if __name__ == "__main__":
    print("Запуск telebot Inline Keyboard Bot...")
    bot.infinity_polling()
