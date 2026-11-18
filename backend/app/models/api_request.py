from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class ApiRequest(Base):
    __tablename__ = "api_requests"

    id = Column(Integer, primary_key=True, index=True)
    bot_id = Column(Integer, ForeignKey("bots.id"), nullable=True, index=True)
    method = Column(String(16), nullable=False)  # GET, POST
    endpoint = Column(String(128), nullable=False)  # sendMessage, getUpdates, etc.
    params = Column(JSON, nullable=True)
    response_status = Column(Integer, nullable=False)
    response_body = Column(JSON, nullable=True)
    execution_time_ms = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    bot = relationship("Bot", back_populates="api_requests")
