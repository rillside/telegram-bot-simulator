from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class ProcessStartRequest(BaseModel):
    bot_id: int
    file_path: str
    work_dir: Optional[str] = None

class ProcessStopRequest(BaseModel):
    bot_id: int

class ProcessStatusResponse(BaseModel):
    id: Optional[int] = None
    bot_id: int
    file_path: Optional[str] = None
    work_dir: Optional[str] = None
    status: str  # STOPPED, STARTING, RUNNING, STOPPING, ERROR
    pid: Optional[int] = None
    exit_code: Optional[int] = None
    started_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None

class ProcessLogEntry(BaseModel):
    bot_id: int
    timestamp: float
    stream: str  # stdout, stderr, system
    text: str
