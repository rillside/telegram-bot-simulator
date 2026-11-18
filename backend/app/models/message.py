from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)  # message_id in Telegram
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False, index=True)
    from_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    from_bot_id = Column(Integer, ForeignKey("bots.id"), nullable=True, index=True)
    is_from_bot = Column(Boolean, default=False)
    date = Column(Integer, nullable=False)  # Unix timestamp
    text = Column(Text, nullable=True)
    reply_to_message_id = Column(Integer, nullable=True)
    reply_markup = Column(JSON, nullable=True)
    media_type = Column(String(32), nullable=True)  # photo, document
    media_url = Column(String(512), nullable=True)
    file_name = Column(String(256), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    chat = relationship("Chat", back_populates="messages")
    from_user = relationship("User", back_populates="messages")
