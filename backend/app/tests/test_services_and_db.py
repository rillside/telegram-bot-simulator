import pytest
from backend.app.core.database import AsyncSessionLocal, init_db
from backend.app.services.bot_service import bot_service
from backend.app.services.user_service import user_service
from backend.app.services.chat_service import chat_service
from backend.app.services.message_service import message_service
from backend.app.schemas.bot import BotCreate
from backend.app.schemas.user import UserCreate

@pytest.fixture(autouse=True)
async def setup_db():
    await init_db()

@pytest.mark.asyncio
async def test_bot_and_user_creation():
    async with AsyncSessionLocal() as session:
        bot = await bot_service.create_bot(
            session,
            BotCreate(name="HelperBot", username="helper_bot", description="Helpful")
        )
        assert bot.id is not None
        assert bot.token.startswith(f"{bot.id}:")

        user1 = await user_service.create_user(
            session,
            UserCreate(first_name="Иван", username="ivan_student")
        )
        user2 = await user_service.create_user(
            session,
            UserCreate(first_name="Ольга", username="olga_student")
        )
        assert user1.id != user2.id

        # Create chats
        chat1 = await chat_service.get_or_create_chat(session, bot.id, user1.id)
        chat2 = await chat_service.get_or_create_chat(session, bot.id, user2.id)
        assert chat1.id != chat2.id

        # Ivan sends message to bot
        msg1 = await message_service.send_user_message(session, chat1.id, user1.id, "Привет от Ивана!")
        assert msg1.text == "Привет от Ивана!"
        assert msg1.is_from_bot is False

        # Olga sends message to bot
        msg2 = await message_service.send_user_message(session, chat2.id, user2.id, "Привет от Ольги!")
        assert msg2.text == "Привет от Ольги!"

        # Messages are partitioned by chat
        chat1_msgs = await chat_service.get_chat_messages(session, chat1.id)
        chat2_msgs = await chat_service.get_chat_messages(session, chat2.id)
        assert len(chat1_msgs) == 1
        assert len(chat2_msgs) == 1
        assert chat1_msgs[0].text == "Привет от Ивана!"
        assert chat2_msgs[0].text == "Привет от Ольги!"
