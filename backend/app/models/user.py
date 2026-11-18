from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)  # Telegram-like user ID e.g. 10001
    first_name = Column(String(128), nullable=False)
    last_name = Column(String(128), nullable=True, default="")
    username = Column(String(64), nullable=True, default="")
    is_bot = Column(Boolean, default=False)
    avatar = Column(String(256), nullable=True, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    chats = relationship("Chat", back_populates="user", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="from_user", cascade="all, delete-orphan")
