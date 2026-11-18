import pytest
import asyncio
import threading
import time
import uvicorn
from aiogram import Bot, Dispatcher, F
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from backend.app.main import app
from backend.app.core.database import AsyncSessionLocal, init_db
from backend.app.models.bot import Bot as BotModel
from backend.app.models.user import User as UserModel
from backend.app.models.chat import Chat as ChatModel
from backend.app.services.message_service import message_service
from backend.app.services.chat_service import chat_service

@pytest.fixture(scope="module")
def server():
    config = uvicorn.Config(app, host="127.0.0.1", port=8003, log_level="warning")
    srv = uvicorn.Server(config)
    th = threading.Thread(target=srv.run, daemon=True)
    th.start()
    time.sleep(1.0)
    yield "http://127.0.0.1:8003"
    srv.should_exit = True

@pytest.mark.asyncio
async def test_aiogram_full_cycle(server):
    await init_db()
    token = "701:AIOGRAM_SECRET_KEY"

    async with AsyncSessionLocal() as session:
        bot_rec = BotModel(id=701, name="AiogramUnit", username="aiogram_unit", token=token)
        user_rec = UserModel(id=901, first_name="StudentAio", username="student_aio")
        session.add_all([bot_rec, user_rec])
        await session.commit()

        chat = ChatModel(id=901, type="private", bot_id=bot_rec.id, user_id=user_rec.id)
        session.add(chat)
        await session.commit()

    api = TelegramAPIServer.from_base(server)
    session_aio = AiohttpSession(api=api)
    bot = Bot(token=token, session=session_aio)
    dp = Dispatcher()

    handled_commands = []
    handled_callbacks = []

    @dp.message(Command("test"))
    async def on_test(msg: Message):
        handled_commands.append(msg.text)
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="ClickMe", callback_data="btn_click")]
        ])
        await msg.answer("Response from aiogram 3!", reply_markup=kb)

    @dp.callback_query(F.data == "btn_click")
    async def on_btn_click(cb: CallbackQuery):
        handled_callbacks.append(cb.data)
        await cb.answer("Button received!", show_alert=False)
        await cb.message.edit_text("Inline clicked successfully!")

    # 1. Check get_me
    me = await bot.get_me()
    assert me.id == 701
    assert me.username == "aiogram_unit"

    # 2. Run polling in background
    polling_task = asyncio.create_task(dp.start_polling(bot, handle_as_tasks=False, polling_timeout=1))
    await asyncio.sleep(0.5)

    # 3. Simulate user sending /test
    async with AsyncSessionLocal() as session:
        user_msg = await message_service.send_user_message(session, 901, 901, "/test")

    await asyncio.sleep(0.8)
    assert "/test" in handled_commands

    # 4. Check response in chat
    bot_reply_id = None
    async with AsyncSessionLocal() as session:
        msgs = await chat_service.get_chat_messages(session, 901)
        bot_msgs = [m for m in msgs if m.is_from_bot]
        assert len(bot_msgs) >= 1
        bot_reply_id = bot_msgs[-1].id
        assert bot_msgs[-1].text == "Response from aiogram 3!"

    # 5. Simulate clicking the inline button
    assert bot_reply_id is not None
    async with AsyncSessionLocal() as session:
        await message_service.click_inline_button(session, 901, 901, bot_reply_id, "btn_click")

    await asyncio.sleep(0.8)
    assert "btn_click" in handled_callbacks

    # Verify edited text in chat
    async with AsyncSessionLocal() as session:
        msgs = await chat_service.get_chat_messages(session, 901)
        last_msg = msgs[-1]
        assert last_msg.text == "Inline clicked successfully!"

    await dp.stop_polling()
    await polling_task
    await session_aio.close()
