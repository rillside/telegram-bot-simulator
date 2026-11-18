from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class Bot(Base):
    __tablename__ = "bots"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    username = Column(String(64), unique=True, index=True, nullable=False)
    token = Column(String(128), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True, default="")
    avatar = Column(String(256), nullable=True, default="")
    is_running = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    chats = relationship("Chat", back_populates="bot", cascade="all, delete-orphan")
    processes = relationship("ProcessRecord", back_populates="bot", cascade="all, delete-orphan")
    api_requests = relationship("ApiRequest", back_populates="bot", cascade="all, delete-orphan")
    updates = relationship("UpdateRecord", back_populates="bot", cascade="all, delete-orphan")
