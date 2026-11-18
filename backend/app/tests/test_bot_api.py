import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.core.database import AsyncSessionLocal, init_db
from backend.app.models.bot import Bot
from backend.app.models.user import User
from backend.app.models.chat import Chat

@pytest.fixture(autouse=True)
async def prepare_db():
    await init_db()

@pytest.mark.asyncio
async def test_get_me_and_auth():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Invalid token
        resp = await client.get("/botinvalid_token/getMe")
        assert resp.status_code == 401
        data = resp.json()
        assert data["ok"] is False

        # Create valid bot in DB
        async with AsyncSessionLocal() as session:
            bot = Bot(id=501, name="TestBot", username="test_bot_501", token="501:SECRET_TOKEN")
            session.add(bot)
            await session.commit()

        # Valid getMe
        resp = await client.get("/bot501:SECRET_TOKEN/getMe")
        assert resp.status_code == 200
        data = resp.json()
        assert data["ok"] is True
        assert data["result"]["id"] == 501
        assert data["result"]["username"] == "test_bot_501"
        assert data["result"]["is_bot"] is True

@pytest.mark.asyncio
async def test_send_message_and_edit():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        async with AsyncSessionLocal() as session:
            bot = Bot(id=502, name="TestBot2", username="test_bot_502", token="502:TOKEN")
            user = User(id=777, first_name="Alice", username="alice777")
            session.add_all([bot, user])
            await session.commit()

        # Send message
        resp = await client.post(
            "/bot502:TOKEN/sendMessage",
            json={"chat_id": 777, "text": "Hello Alice!"}
        )
        assert resp.status_code == 200
        msg_data = resp.json()
        assert msg_data["ok"] is True
        msg_id = msg_data["result"]["message_id"]
        assert msg_data["result"]["text"] == "Hello Alice!"
        assert msg_data["result"]["chat"]["id"] == 777

        # Edit message
        resp_edit = await client.post(
            "/bot502:TOKEN/editMessageText",
            json={"chat_id": 777, "message_id": msg_id, "text": "Edited text!"}
        )
        assert resp_edit.status_code == 200
        edited_data = resp_edit.json()
        assert edited_data["ok"] is True
        assert edited_data["result"]["text"] == "Edited text!"

        # Delete message
        resp_del = await client.post(
            "/bot502:TOKEN/deleteMessage",
            json={"chat_id": 777, "message_id": msg_id}
        )
        assert resp_del.status_code == 200
        assert resp_del.json()["ok"] is True
