import time
import uuid
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.app.models.message import Message
from backend.app.models.chat import Chat
from backend.app.models.user import User
from backend.app.models.bot import Bot
from backend.app.models.update import UpdateRecord
from backend.app.models.callback_query import CallbackQueryRecord
from backend.app.core.events import event_bus
from backend.app.bot_api.updates import (
    build_message_dict,
    build_message_update,
    build_callback_query_update
)
from backend.app.bot_api.polling import update_queue_manager

class MessageService:
    @staticmethod
    async def send_user_message(
        db: AsyncSession,
        chat_id: int,
        user_id: int,
        text: Optional[str] = None,
        media_type: Optional[str] = None,
        media_url: Optional[str] = None,
        file_name: Optional[str] = None,
        reply_to_message_id: Optional[int] = None
    ) -> Message:
        # Load chat with bot and user
        res = await db.execute(
            select(Chat)
            .options(selectinload(Chat.bot), selectinload(Chat.user))
            .where(Chat.id == chat_id)
        )
        chat = res.scalar_one_or_none()
        if not chat:
            raise ValueError(f"Chat with id {chat_id} not found")

        user_res = await db.execute(select(User).where(User.id == user_id))
        user = user_res.scalar_one_or_none()
        if not user:
            raise ValueError(f"User with id {user_id} not found")

        now = int(time.time())
        msg = Message(
            chat_id=chat.id,
            from_user_id=user.id,
            is_from_bot=False,
            date=now,
            text=text,
            reply_to_message_id=reply_to_message_id,
            media_type=media_type,
            media_url=media_url,
            file_name=file_name
        )
        db.add(msg)
        await db.commit()
        await db.refresh(msg)

        # Build Telegram Message dict
        tg_msg = build_message_dict(
            message_id=msg.id,
            date=msg.date,
            chat_id=chat.id,
            chat_type=chat.type,
            from_id=user.id,
            from_is_bot=False,
            from_first_name=user.first_name,
            from_last_name=user.last_name,
            from_username=user.username,
            text=msg.text
        )

        # Create Update record
        update_record = UpdateRecord(
            bot_id=chat.bot_id,
            update_type="message",
            payload={}
        )
        db.add(update_record)
        await db.commit()
        await db.refresh(update_record)

        update_dict = build_message_update(update_record.id, tg_msg)
        update_record.payload = update_dict
        await db.commit()

        # Enqueue for bot Long Polling
        await update_queue_manager.enqueue_update(chat.bot_id, update_dict)

        # Broadcast via WebSocket for UI
        await event_bus.broadcast("chat_message", {
            "message": {
                "id": msg.id,
                "chat_id": chat.id,
                "from_user_id": user.id,
                "from_bot_id": None,
                "is_from_bot": False,
                "date": msg.date,
                "text": msg.text,
                "reply_to_message_id": msg.reply_to_message_id,
                "media_type": msg.media_type,
                "media_url": msg.media_url,
                "file_name": msg.file_name,
                "created_at": msg.created_at.isoformat()
            }
        })

        # Broadcast update to Updates Inspector
        await event_bus.broadcast("update_event", {
            "id": update_record.id,
            "bot_id": chat.bot_id,
            "update_type": "message",
            "payload": update_dict,
            "created_at": update_record.created_at.isoformat()
        })

        return msg

    @staticmethod
    async def click_inline_button(
        db: AsyncSession,
        chat_id: int,
        user_id: int,
        message_id: int,
        callback_data: str
    ) -> str:
        # Load chat
        res = await db.execute(
            select(Chat)
            .options(selectinload(Chat.bot), selectinload(Chat.user))
            .where(Chat.id == chat_id)
        )
        chat = res.scalar_one_or_none()
        if not chat:
            raise ValueError(f"Chat with id {chat_id} not found")

        user_res = await db.execute(select(User).where(User.id == user_id))
        user = user_res.scalar_one_or_none()
        if not user:
            raise ValueError(f"User with id {user_id} not found")

        msg_res = await db.execute(select(Message).where(Message.id == message_id))
        msg = msg_res.scalar_one_or_none()
        if not msg:
            raise ValueError(f"Message with id {message_id} not found")

        cbq_id = f"cbq_{uuid.uuid4().hex[:16]}"
        cbq_record = CallbackQueryRecord(
            id=cbq_id,
            bot_id=chat.bot_id,
            chat_id=chat.id,
            message_id=msg.id,
            from_user_id=user.id,
            data=callback_data
        )
        db.add(cbq_record)

        # Build message dict for the callback query
        msg_dict = build_message_dict(
            message_id=msg.id,
            date=msg.date,
            chat_id=chat.id,
            chat_type=chat.type,
            from_id=chat.bot.id,
            from_is_bot=True,
            from_first_name=chat.bot.name,
            from_username=chat.bot.username,
            text=msg.text,
            reply_markup=msg.reply_markup
        )

        from_user = {
            "id": user.id,
            "is_bot": False,
            "first_name": user.first_name,
            "username": user.username
        }
        if user.last_name:
            from_user["last_name"] = user.last_name

        update_record = UpdateRecord(
            bot_id=chat.bot_id,
            update_type="callback_query",
            payload={}
        )
        db.add(update_record)
        await db.commit()
        await db.refresh(update_record)

        cbq_update = build_callback_query_update(
            update_id=update_record.id,
            query_id=cbq_id,
            from_user=from_user,
            message_dict=msg_dict,
            data=callback_data
        )
        update_record.payload = cbq_update
        await db.commit()

        # Enqueue for bot
        await update_queue_manager.enqueue_update(chat.bot_id, cbq_update)

        # Broadcast update for Updates Inspector
        await event_bus.broadcast("update_event", {
            "id": update_record.id,
            "bot_id": chat.bot_id,
            "update_type": "callback_query",
            "payload": cbq_update,
            "created_at": update_record.created_at.isoformat()
        })

        return cbq_id

message_service = MessageService()
