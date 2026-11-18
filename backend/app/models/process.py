from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class ProcessRecord(Base):
    __tablename__ = "processes"

    id = Column(Integer, primary_key=True, index=True)
    bot_id = Column(Integer, ForeignKey("bots.id"), nullable=False, index=True)
    file_path = Column(String(512), nullable=False)
    work_dir = Column(String(512), nullable=True)
    status = Column(String(32), default="STOPPED")  # STOPPED, STARTING, RUNNING, STOPPING, ERROR
    pid = Column(Integer, nullable=True)
    exit_code = Column(Integer, nullable=True)
    started_at = Column(DateTime, nullable=True)
    stopped_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    bot = relationship("Bot", back_populates="processes")
