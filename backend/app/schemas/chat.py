from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from backend.app.schemas.bot import BotResponse
from backend.app.schemas.user import UserResponse

class ChatCreate(BaseModel):
    bot_id: int
    user_id: int
    type: Optional[str] = "private"
    title: Optional[str] = None

class ChatResponse(BaseModel):
    id: int
    type: str
    title: Optional[str] = None
    bot_id: int
    user_id: int
    created_at: datetime
    bot: Optional[BotResponse] = None
    user: Optional[UserResponse] = None
    last_message: Optional[dict] = None
    unread_count: int = 0

    model_config = ConfigDict(from_attributes=True)
