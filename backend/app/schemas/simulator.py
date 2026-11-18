from datetime import datetime
from typing import Optional, Any, Dict
from pydantic import BaseModel, ConfigDict

class ApiRequestLogResponse(BaseModel):
    id: int
    bot_id: Optional[int] = None
    method: str
    endpoint: str
    params: Optional[Dict[str, Any]] = None
    response_status: int
    response_body: Optional[Any] = None
    execution_time_ms: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UpdateLogResponse(BaseModel):
    id: int
    bot_id: int
    update_type: str
    payload: Dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
