import json
import time
import uuid
from typing import Dict, Any, Optional
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.core.config import settings
from backend.app.core.events import event_bus
from backend.app.models.bot import Bot
from backend.app.models.user import User
from backend.app.models.chat import Chat
from backend.app.models.message import Message
from backend.app.bot_api.exceptions import TelegramApiException
from backend.app.bot_api.keyboards import parse_reply_markup
from backend.app.bot_api.updates import build_message_dict
from backend.app.bot_api.polling import update_queue_manager

async def handle_get_me(bot: Bot, params: Dict[str, Any], db: AsyncSession, files=None) -> Dict[str, Any]:
    return {
        "id": bot.id,
        "is_bot": True,
        "first_name": bot.name,
        "username": bot.username,
        "can_join_groups": True,
        "can_read_all_group_messages": False,
        "supports_inline_queries": False
    }

async def handle_get_updates(bot: Bot, params: Dict[str, Any], db: AsyncSession, files=None) -> list:
    offset = None
    if "offset" in params and params["offset"] is not None and str(params["offset"]).strip():
        try:
            offset = int(params["offset"])
        except ValueError:
            pass

    limit = 100
    if "limit" in params and params["limit"] is not None:
        try:
            limit = int(params["limit"])
        except ValueError:
            pass

    timeout = 0
    if "timeout" in params and params["timeout"] is not None:
        try:
            timeout = int(params["timeout"])
        except ValueError:
            pass

    allowed_updates = None
    if "allowed_updates" in params and params["allowed_updates"]:
        au = params["allowed_updates"]
        if isinstance(au, str):
            try:
                allowed_updates = json.loads(au)
            except Exception:
                allowed_updates = [au]
        elif isinstance(au, list):
            allowed_updates = au

    return await update_queue_manager.get_updates(
        bot_id=bot.id,
        offset=offset,
        limit=limit,
        timeout=timeout,
        allowed_updates=allowed_updates
    )

async def handle_get_webhook_info(bot: Bot, params: Dict[str, Any], db: AsyncSession, files=None) -> Dict[str, Any]:
    return {
        "url": "",
        "has_custom_certificate": False,
        "pending_update_count": 0
    }

async def handle_delete_webhook(bot: Bot, params: Dict[str, Any], db: AsyncSession, files=None) -> bool:
    return True

async def handle_set_webhook(bot: Bot, params: Dict[str, Any], db: AsyncSession, files=None) -> bool:
    return True

async def _get_or_create_chat(db: AsyncSession, bot_id: int, chat_id_raw: Any) -> Chat:
    try:
        chat_id = int(chat_id_raw)
    except (ValueError, TypeError):
        raise TelegramApiException(400, "Bad Request: chat_id must be an integer")

    # Look for existing chat
    result = await db.execute(select(Chat).where(Chat.id == chat_id, Chat.bot_id == bot_id))
    chat = result.scalar_one_or_none()
    if chat:
        return chat

    # If chat not found, check if a chat exists with this ID overall
    result = await db.execute(select(Chat).where(Chat.id == chat_id))
    chat = result.scalar_one_or_none()
    if chat:
        # Link this chat or return it
        return chat

    # Check if a user with this chat_id exists (private chat)
    result = await db.execute(select(User).where(User.id == chat_id))
    user = result.scalar_one_or_none()
    if not user:
        # Create user automatically for convenience in simulation
        user = User(
            id=chat_id,
            first_name=f"User_{chat_id}",
            username=f"user_{chat_id}"
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    chat = Chat(
        id=chat_id,
        type="private",
        bot_id=bot_id,
        user_id=user.id
    )
    db.add(chat)
    await db.commit()
    await db.refresh(chat)
    return chat

async def handle_send_message(bot: Bot, params: Dict[str, Any], db: AsyncSession, files=None) -> Dict[str, Any]:
    chat_id_raw = params.get("chat_id")
    if not chat_id_raw:
        raise TelegramApiException(400, "Bad Request: chat_id is required")

    text = params.get("text")
    if text is None:
        raise TelegramApiException(400, "Bad Request: message text is empty")

    chat = await _get_or_create_chat(db, bot.id, chat_id_raw)

    reply_to_message_id = None
    if params.get("reply_to_message_id"):
        try:
            reply_to_message_id = int(params["reply_to_message_id"])
        except ValueError:
            pass

    reply_markup = parse_reply_markup(params.get("reply_markup"))
    now = int(time.time())

    msg = Message(
        chat_id=chat.id,
        from_bot_id=bot.id,
        is_from_bot=True,
        date=now,
        text=str(text),
        reply_to_message_id=reply_to_message_id,
        reply_markup=reply_markup
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)

    # Format Telegram Message
    tg_msg = build_message_dict(
        message_id=msg.id,
        date=msg.date,
        chat_id=chat.id,
        chat_type=chat.type,
        from_id=bot.id,
        from_is_bot=True,
        from_first_name=bot.name,
        from_username=bot.username,
        text=msg.text,
        reply_markup=reply_markup
    )

    # Broadcast to WebSocket
    await event_bus.broadcast("chat_message", {
        "message": {
            "id": msg.id,
            "chat_id": chat.id,
            "from_bot_id": bot.id,
            "from_user_id": None,
            "is_from_bot": True,
            "date": msg.date,
            "text": msg.text,
            "reply_to_message_id": msg.reply_to_message_id,
            "reply_markup": msg.reply_markup,
            "media_type": None,
            "media_url": None,
            "file_name": None,
            "created_at": msg.created_at.isoformat()
        }
    })

    return tg_msg

async def handle_forward_message(bot: Bot, params: Dict[str, Any], db: AsyncSession, files=None) -> Dict[str, Any]:
    chat_id_raw = params.get("chat_id")
    from_chat_id_raw = params.get("from_chat_id")
    message_id_raw = params.get("message_id")

    if not chat_id_raw or not from_chat_id_raw or not message_id_raw:
        raise TelegramApiException(400, "Bad Request: chat_id, from_chat_id, and message_id are required")

    dest_chat = await _get_or_create_chat(db, bot.id, chat_id_raw)
    orig_msg_res = await db.execute(select(Message).where(Message.id == int(message_id_raw)))
    orig_msg = orig_msg_res.scalar_one_or_none()
    if not orig_msg:
        raise TelegramApiException(400, "Bad Request: message to forward not found")

    now = int(time.time())
    new_msg = Message(
        chat_id=dest_chat.id,
        from_bot_id=bot.id,
        is_from_bot=True,
        date=now,
        text=orig_msg.text,
        media_type=orig_msg.media_type,
        media_url=orig_msg.media_url,
        file_name=orig_msg.file_name
    )
    db.add(new_msg)
    await db.commit()
    await db.refresh(new_msg)

    tg_msg = build_message_dict(
        message_id=new_msg.id,
        date=new_msg.date,
        chat_id=dest_chat.id,
        chat_type=dest_chat.type,
        from_id=bot.id,
        from_is_bot=True,
        from_first_name=bot.name,
        from_username=bot.username,
        text=new_msg.text
    )

    await event_bus.broadcast("chat_message", {
        "message": {
            "id": new_msg.id,
            "chat_id": dest_chat.id,
            "from_bot_id": bot.id,
            "from_user_id": None,
            "is_from_bot": True,
            "date": new_msg.date,
            "text": new_msg.text,
            "media_type": new_msg.media_type,
            "media_url": new_msg.media_url,
            "file_name": new_msg.file_name,
            "created_at": new_msg.created_at.isoformat()
        }
    })
    return tg_msg

async def handle_edit_message_text(bot: Bot, params: Dict[str, Any], db: AsyncSession, files=None) -> Dict[str, Any]:
    message_id = params.get("message_id")
    chat_id = params.get("chat_id")
    text = params.get("text")
    if not message_id or text is None:
        raise TelegramApiException(400, "Bad Request: message_id and text are required")

    result = await db.execute(select(Message).where(Message.id == int(message_id)))
    msg = result.scalar_one_or_none()
    if not msg:
        raise TelegramApiException(400, "Bad Request: message to edit not found")

    msg.text = str(text)
    if "reply_markup" in params:
        msg.reply_markup = parse_reply_markup(params.get("reply_markup"))

    await db.commit()
    await db.refresh(msg)

    # Broadcast update
    await event_bus.broadcast("message_edit", {
        "message": {
            "id": msg.id,
            "chat_id": msg.chat_id,
            "text": msg.text,
            "reply_markup": msg.reply_markup
        }
    })

    return build_message_dict(
        message_id=msg.id,
        date=msg.date,
        chat_id=msg.chat_id,
        chat_type="private",
        from_id=bot.id,
        from_is_bot=True,
        from_first_name=bot.name,
        from_username=bot.username,
        text=msg.text,
        reply_markup=msg.reply_markup
    )

async def handle_edit_message_reply_markup(bot: Bot, params: Dict[str, Any], db: AsyncSession, files=None) -> Dict[str, Any]:
    message_id = params.get("message_id")
    if not message_id:
        raise TelegramApiException(400, "Bad Request: message_id is required")

    result = await db.execute(select(Message).where(Message.id == int(message_id)))
    msg = result.scalar_one_or_none()
    if not msg:
        raise TelegramApiException(400, "Bad Request: message to edit not found")

    msg.reply_markup = parse_reply_markup(params.get("reply_markup"))
    await db.commit()
    await db.refresh(msg)

    await event_bus.broadcast("message_edit", {
        "message": {
            "id": msg.id,
            "chat_id": msg.chat_id,
            "text": msg.text,
            "reply_markup": msg.reply_markup
        }
    })

    return build_message_dict(
        message_id=msg.id,
        date=msg.date,
        chat_id=msg.chat_id,
        chat_type="private",
        from_id=bot.id,
        from_is_bot=True,
        from_first_name=bot.name,
        from_username=bot.username,
        text=msg.text,
        reply_markup=msg.reply_markup
    )

async def handle_delete_message(bot: Bot, params: Dict[str, Any], db: AsyncSession, files=None) -> bool:
    message_id = params.get("message_id")
    if not message_id:
        raise TelegramApiException(400, "Bad Request: message_id is required")

    result = await db.execute(select(Message).where(Message.id == int(message_id)))
    msg = result.scalar_one_or_none()
    if msg:
        chat_id = msg.chat_id
        await db.delete(msg)
        await db.commit()
        await event_bus.broadcast("message_delete", {
            "message_id": int(message_id),
            "chat_id": chat_id
        })
    return True

async def handle_get_chat(bot: Bot, params: Dict[str, Any], db: AsyncSession, files=None) -> Dict[str, Any]:
    chat_id_raw = params.get("chat_id")
    if not chat_id_raw:
        raise TelegramApiException(400, "Bad Request: chat_id is required")
    chat = await _get_or_create_chat(db, bot.id, chat_id_raw)
    return {
        "id": chat.id,
        "type": chat.type,
        "title": chat.title or f"Chat {chat.id}",
        "first_name": chat.title or f"Chat {chat.id}"
    }

async def handle_get_chat_member(bot: Bot, params: Dict[str, Any], db: AsyncSession, files=None) -> Dict[str, Any]:
    chat_id_raw = params.get("chat_id")
    user_id_raw = params.get("user_id")
    if not chat_id_raw or not user_id_raw:
        raise TelegramApiException(400, "Bad Request: chat_id and user_id are required")

    user_id = int(user_id_raw)
    if user_id == bot.id:
        return {
            "status": "administrator",
            "can_be_edited": False,
            "can_manage_chat": True,
            "user": {
                "id": bot.id,
                "is_bot": True,
                "first_name": bot.name,
                "username": bot.username
            }
        }
    else:
        user_res = await db.execute(select(User).where(User.id == user_id))
        user = user_res.scalar_one_or_none()
        first_name = user.first_name if user else f"User {user_id}"
        return {
            "status": "member",
            "user": {
                "id": user_id,
                "is_bot": False,
                "first_name": first_name
            }
        }

async def handle_answer_callback_query(bot: Bot, params: Dict[str, Any], db: AsyncSession, files=None) -> bool:
    callback_query_id = params.get("callback_query_id")
    text = params.get("text", "")
    show_alert = bool(params.get("show_alert", False))

    await event_bus.broadcast("callback_query_answered", {
        "callback_query_id": callback_query_id,
        "text": text,
        "show_alert": show_alert
    })
    return True

async def handle_send_photo(bot: Bot, params: Dict[str, Any], db: AsyncSession, files=None) -> Dict[str, Any]:
    chat_id_raw = params.get("chat_id")
    if not chat_id_raw:
        raise TelegramApiException(400, "Bad Request: chat_id is required")

    chat = await _get_or_create_chat(db, bot.id, chat_id_raw)
    caption = params.get("caption")
    reply_markup = parse_reply_markup(params.get("reply_markup"))

    file_id = f"photo_{uuid.uuid4().hex[:12]}"
    file_url = ""

    # Check uploaded file
    if files and "photo" in files:
        uploaded_file = files["photo"]
        filename = f"{uuid.uuid4().hex}_{uploaded_file.filename}"
        save_path = settings.upload_dir / filename
        content = await uploaded_file.read()
        with open(save_path, "wb") as f:
            f.write(content)
        file_url = f"{settings.base_url}/uploads/{filename}"
    elif params.get("photo"):
        file_url = str(params["photo"])

    now = int(time.time())
    msg = Message(
        chat_id=chat.id,
        from_bot_id=bot.id,
        is_from_bot=True,
        date=now,
        text=caption,
        media_type="photo",
        media_url=file_url,
        reply_markup=reply_markup
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)

    photo_sizes = [
        {
            "file_id": file_id,
            "file_unique_id": f"u_{file_id}",
            "width": 800,
            "height": 600,
            "file_size": 10240
        }
    ]

    tg_msg = build_message_dict(
        message_id=msg.id,
        date=msg.date,
        chat_id=chat.id,
        chat_type=chat.type,
        from_id=bot.id,
        from_is_bot=True,
        from_first_name=bot.name,
        from_username=bot.username,
        caption=caption,
        photo=photo_sizes,
        reply_markup=reply_markup
    )

    await event_bus.broadcast("chat_message", {
        "message": {
            "id": msg.id,
            "chat_id": chat.id,
            "from_bot_id": bot.id,
            "from_user_id": None,
            "is_from_bot": True,
            "date": msg.date,
            "text": msg.text,
            "media_type": "photo",
            "media_url": file_url,
            "reply_markup": msg.reply_markup,
            "created_at": msg.created_at.isoformat()
        }
    })

    return tg_msg

async def handle_send_document(bot: Bot, params: Dict[str, Any], db: AsyncSession, files=None) -> Dict[str, Any]:
    chat_id_raw = params.get("chat_id")
    if not chat_id_raw:
        raise TelegramApiException(400, "Bad Request: chat_id is required")

    chat = await _get_or_create_chat(db, bot.id, chat_id_raw)
    caption = params.get("caption")
    reply_markup = parse_reply_markup(params.get("reply_markup"))

    file_id = f"doc_{uuid.uuid4().hex[:12]}"
    file_url = ""
    filename = "document"

    if files and "document" in files:
        uploaded_file = files["document"]
        filename = uploaded_file.filename
        saved_name = f"{uuid.uuid4().hex}_{filename}"
        save_path = settings.upload_dir / saved_name
        content = await uploaded_file.read()
        with open(save_path, "wb") as f:
            f.write(content)
        file_url = f"{settings.base_url}/uploads/{saved_name}"
    elif params.get("document"):
        file_url = str(params["document"])
        filename = Path(file_url).name

    now = int(time.time())
    msg = Message(
        chat_id=chat.id,
        from_bot_id=bot.id,
        is_from_bot=True,
        date=now,
        text=caption,
        media_type="document",
        media_url=file_url,
        file_name=filename,
        reply_markup=reply_markup
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)

    doc_obj = {
        "file_id": file_id,
        "file_unique_id": f"u_{file_id}",
        "file_name": filename,
        "file_size": 2048
    }

    tg_msg = build_message_dict(
        message_id=msg.id,
        date=msg.date,
        chat_id=chat.id,
        chat_type=chat.type,
        from_id=bot.id,
        from_is_bot=True,
        from_first_name=bot.name,
        from_username=bot.username,
        caption=caption,
        document=doc_obj,
        reply_markup=reply_markup
    )

    await event_bus.broadcast("chat_message", {
        "message": {
            "id": msg.id,
            "chat_id": chat.id,
            "from_bot_id": bot.id,
            "from_user_id": None,
            "is_from_bot": True,
            "date": msg.date,
            "text": msg.text,
            "media_type": "document",
            "media_url": file_url,
            "file_name": filename,
            "reply_markup": msg.reply_markup,
            "created_at": msg.created_at.isoformat()
        }
    })

    return tg_msg

HANDLERS = {
    "getMe": handle_get_me,
    "getUpdates": handle_get_updates,
    "getWebhookInfo": handle_get_webhook_info,
    "deleteWebhook": handle_delete_webhook,
    "setWebhook": handle_set_webhook,
    "sendMessage": handle_send_message,
    "forwardMessage": handle_forward_message,
    "editMessageText": handle_edit_message_text,
    "editMessageReplyMarkup": handle_edit_message_reply_markup,
    "deleteMessage": handle_delete_message,
    "getChat": handle_get_chat,
    "getChatMember": handle_get_chat_member,
    "answerCallbackQuery": handle_answer_callback_query,
    "sendPhoto": handle_send_photo,
    "sendDocument": handle_send_document,
}
