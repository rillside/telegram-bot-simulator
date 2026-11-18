from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class UserBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=128)
    last_name: Optional[str] = ""
    username: Optional[str] = ""
    avatar: Optional[str] = ""

class UserCreate(UserBase):
    id: Optional[int] = None

class UserResponse(UserBase):
    id: int
    is_bot: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
