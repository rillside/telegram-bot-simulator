import pytest
import asyncio
import threading
import time
import uvicorn
import telebot
from telebot import apihelper
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from backend.app.main import app
from backend.app.core.database import AsyncSessionLocal, init_db
from backend.app.models.bot import Bot
from backend.app.models.user import User
from backend.app.models.chat import Chat
from backend.app.services.message_service import message_service

@pytest.fixture(scope="module")
def server():
    # Run uvicorn on port 8002 for tests
    config = uvicorn.Config(app, host="127.0.0.1", port=8002, log_level="warning")
    srv = uvicorn.Server(config)
    th = threading.Thread(target=srv.run, daemon=True)
    th.start()
    time.sleep(1.0)
    yield "http://127.0.0.1:8002"
    srv.should_exit = True

@pytest.mark.asyncio
async def test_telebot_full_cycle(server):
    await init_db()
    token = "601:TELEBOT_SECRET_KEY"

    async with AsyncSessionLocal() as session:
        bot_rec = Bot(id=601, name="TeleBotUnit", username="telebot_unit", token=token)
        user_rec = User(id=801, first_name="Student", username="student801")
        session.add_all([bot_rec, user_rec])
        await session.commit()

        chat = Chat(id=801, type="private", bot_id=bot_rec.id, user_id=user_rec.id)
        session.add(chat)
        await session.commit()

    # Configure real telebot
    apihelper.API_URL = f"{server}/bot{{0}}/{{1}}"
    bot = telebot.TeleBot(token, threaded=False)

    # 1. Test get_me
    me = bot.get_me()
    assert me.id == 601
    assert me.username == "telebot_unit"

    # 2. Setup handlers
    received_messages = []
    @bot.message_handler(commands=["start"])
    def on_start(msg):
        received_messages.append(msg.text)
        bot.send_message(msg.chat.id, "Welcome from real TeleBot!")

    # 3. Simulate user sending /start
    async with AsyncSessionLocal() as session:
        await message_service.send_user_message(session, 801, 801, "/start")

    # 4. Fetch updates via telebot
    updates = bot.get_updates(timeout=1)
    assert len(updates) >= 1
    bot.process_new_updates(updates)

    assert "/start" in received_messages

    # Check that bot's reply arrived in the chat
    async with AsyncSessionLocal() as session:
        from backend.app.services.chat_service import chat_service
        msgs = await chat_service.get_chat_messages(session, 801)
        bot_msgs = [m for m in msgs if m.is_from_bot]
        assert len(bot_msgs) >= 1
        assert bot_msgs[-1].text == "Welcome from real TeleBot!"

    # 5. Test sending ReplyKeyboardMarkup without KeyError 'inline_keyboard'
    from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
    reply_kb = ReplyKeyboardMarkup(resize_keyboard=True)
    reply_kb.add(KeyboardButton("Кнопка 1"))
    sent_with_kb = bot.send_message(801, "Menu opened", reply_markup=reply_kb)
    assert sent_with_kb.text == "Menu opened"

    # 6. Test sending ReplyKeyboardRemove without KeyError
    sent_with_rm = bot.send_message(801, "Menu closed", reply_markup=ReplyKeyboardRemove())
    assert sent_with_rm.text == "Menu closed"
