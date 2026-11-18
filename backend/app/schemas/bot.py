from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class BotBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    username: str = Field(..., min_length=3, max_length=64)
    description: Optional[str] = ""
    avatar: Optional[str] = ""

class BotCreate(BotBase):
    pass

class BotResponse(BotBase):
    id: int
    token: str
    is_running: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
