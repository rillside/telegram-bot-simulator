from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class UpdateRecord(Base):
    __tablename__ = "updates"

    id = Column(Integer, primary_key=True, index=True)  # update_id
    bot_id = Column(Integer, ForeignKey("bots.id"), nullable=False, index=True)
    update_type = Column(String(32), nullable=False)  # message, edited_message, callback_query
    payload = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    bot = relationship("Bot", back_populates="updates")
