from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from backend.app.core.database import Base

class CallbackQueryRecord(Base):
    __tablename__ = "callback_queries"

    id = Column(String(64), primary_key=True)
    bot_id = Column(Integer, nullable=False, index=True)
    chat_id = Column(Integer, nullable=False)
    message_id = Column(Integer, nullable=False)
    from_user_id = Column(Integer, nullable=False)
    data = Column(String(256), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
