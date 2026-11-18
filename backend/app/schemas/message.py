from datetime import datetime
from typing import Optional, Any, Dict
from pydantic import BaseModel, ConfigDict

class SendUserMessageRequest(BaseModel):
    chat_id: int
    user_id: int
    text: Optional[str] = None
    media_type: Optional[str] = None
    media_url: Optional[str] = None
    file_name: Optional[str] = None
    reply_to_message_id: Optional[int] = None

class ClickInlineButtonRequest(BaseModel):
    chat_id: int
    user_id: int
    message_id: int
    callback_data: str

class MessageResponse(BaseModel):
    id: int
    chat_id: int
    from_user_id: Optional[int] = None
    from_bot_id: Optional[int] = None
    is_from_bot: bool
    date: int
    text: Optional[str] = None
    reply_to_message_id: Optional[int] = None
    reply_markup: Optional[Dict[str, Any]] = None
    media_type: Optional[str] = None
    media_url: Optional[str] = None
    file_name: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
