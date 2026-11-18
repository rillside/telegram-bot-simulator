from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from backend.app.models.chat import Chat
from backend.app.models.bot import Bot
from backend.app.models.user import User
from backend.app.models.message import Message

class ChatService:
    @staticmethod
    async def get_or_create_chat(db: AsyncSession, bot_id: int, user_id: int) -> Chat:
        res = await db.execute(
            select(Chat)
            .options(selectinload(Chat.bot), selectinload(Chat.user))
            .where(Chat.bot_id == bot_id, Chat.user_id == user_id)
        )
        chat = res.scalar_one_or_none()
        if chat:
            return chat

        # Verify bot & user
        bot_res = await db.execute(select(Bot).where(Bot.id == bot_id))
        bot = bot_res.scalar_one_or_none()
        if not bot:
            raise ValueError(f"Bot with id {bot_id} not found")

        user_res = await db.execute(select(User).where(User.id == user_id))
        user = user_res.scalar_one_or_none()
        if not user:
            raise ValueError(f"User with id {user_id} not found")

        chat = Chat(
            type="private",
            title=bot.name,
            bot_id=bot.id,
            user_id=user.id
        )
        db.add(chat)
        await db.commit()
        await db.refresh(chat)

        res = await db.execute(
            select(Chat)
            .options(selectinload(Chat.bot), selectinload(Chat.user))
            .where(Chat.id == chat.id)
        )
        return res.scalar_one()

    @staticmethod
    async def get_user_chats(db: AsyncSession, user_id: int) -> List[dict]:
        res = await db.execute(
            select(Chat)
            .options(selectinload(Chat.bot), selectinload(Chat.user))
            .where(Chat.user_id == user_id)
            .order_by(Chat.id.desc())
        )
        chats = res.scalars().all()
        result = []
        for c in chats:
            # get last message
            last_msg_res = await db.execute(
                select(Message)
                .where(Message.chat_id == c.id)
                .order_by(Message.id.desc())
                .limit(1)
            )
            last_msg = last_msg_res.scalar_one_or_none()
            last_msg_dict = None
            if last_msg:
                last_msg_dict = {
                    "id": last_msg.id,
                    "text": last_msg.text,
                    "date": last_msg.date,
                    "is_from_bot": last_msg.is_from_bot,
                    "media_type": last_msg.media_type
                }
            result.append({
                "id": c.id,
                "type": c.type,
                "title": c.title or (c.bot.name if c.bot else "Chat"),
                "bot_id": c.bot_id,
                "user_id": c.user_id,
                "created_at": c.created_at,
                "bot": {
                    "id": c.bot.id,
                    "name": c.bot.name,
                    "username": c.bot.username,
                    "avatar": c.bot.avatar,
                    "token": c.bot.token,
                    "is_running": c.bot.is_running,
                    "description": c.bot.description,
                    "created_at": c.bot.created_at
                } if c.bot else None,
                "user": {
                    "id": c.user.id,
                    "first_name": c.user.first_name,
                    "last_name": c.user.last_name,
                    "username": c.user.username,
                    "avatar": c.user.avatar,
                    "is_bot": c.user.is_bot,
                    "created_at": c.user.created_at
                } if c.user else None,
                "last_message": last_msg_dict
            })
        return result

    @staticmethod
    async def get_chat_messages(db: AsyncSession, chat_id: int) -> List[Message]:
        res = await db.execute(
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.id.asc())
        )
        return list(res.scalars().all())

chat_service = ChatService()
