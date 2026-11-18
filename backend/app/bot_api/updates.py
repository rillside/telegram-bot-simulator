import time
from typing import Dict, Any, Optional

def build_message_dict(
    message_id: int,
    date: int,
    chat_id: int,
    chat_type: str,
    from_id: int,
    from_is_bot: bool,
    from_first_name: str,
    from_last_name: Optional[str] = None,
    from_username: Optional[str] = None,
    text: Optional[str] = None,
    reply_to_message: Optional[Dict[str, Any]] = None,
    reply_markup: Optional[Dict[str, Any]] = None,
    photo: Optional[list] = None,
    document: Optional[Dict[str, Any]] = None,
    caption: Optional[str] = None
) -> Dict[str, Any]:
    msg = {
        "message_id": message_id,
        "date": date,
        "chat": {
            "id": chat_id,
            "type": chat_type,
            "first_name": from_first_name,
        },
        "from": {
            "id": from_id,
            "is_bot": from_is_bot,
            "first_name": from_first_name,
        }
    }
    if from_last_name:
        msg["from"]["last_name"] = from_last_name
    if from_username:
        msg["from"]["username"] = from_username
        if chat_type == "private":
            msg["chat"]["username"] = from_username
    if text is not None:
        msg["text"] = text
    if reply_to_message:
        msg["reply_to_message"] = reply_to_message
    if reply_markup and isinstance(reply_markup, dict) and "inline_keyboard" in reply_markup:
        msg["reply_markup"] = reply_markup
    if photo:
        msg["photo"] = photo
    if document:
        msg["document"] = document
    if caption:
        msg["caption"] = caption
    return msg

def build_message_update(update_id: int, message_dict: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "update_id": update_id,
        "message": message_dict
    }

def build_edited_message_update(update_id: int, message_dict: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "update_id": update_id,
        "edited_message": message_dict
    }

def build_callback_query_update(
    update_id: int,
    query_id: str,
    from_user: Dict[str, Any],
    message_dict: Dict[str, Any],
    data: str,
    chat_instance: str = "simulator_chat_instance"
) -> Dict[str, Any]:
    return {
        "update_id": update_id,
        "callback_query": {
            "id": query_id,
            "from": from_user,
            "message": message_dict,
            "chat_instance": chat_instance,
            "data": data
        }
    }
