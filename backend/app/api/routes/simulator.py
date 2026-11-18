from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from backend.app.core.database import get_db
from backend.app.models.api_request import ApiRequest
from backend.app.models.update import UpdateRecord
from backend.app.schemas.simulator import ApiRequestLogResponse, UpdateLogResponse

router = APIRouter()

@router.get("/api-requests", response_model=List[ApiRequestLogResponse])
async def list_api_requests(
    bot_id: Optional[int] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    query = select(ApiRequest)
    if bot_id is not None:
        query = query.where(ApiRequest.bot_id == bot_id)
    query = query.order_by(ApiRequest.id.desc()).limit(limit)
    res = await db.execute(query)
    return list(res.scalars().all())

@router.get("/updates", response_model=List[UpdateLogResponse])
async def list_updates(
    bot_id: Optional[int] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    query = select(UpdateRecord)
    if bot_id is not None:
        query = query.where(UpdateRecord.bot_id == bot_id)
    query = query.order_by(UpdateRecord.id.desc()).limit(limit)
    res = await db.execute(query)
    return list(res.scalars().all())

@router.post("/clear")
async def clear_inspector_logs(db: AsyncSession = Depends(get_db)):
    await db.execute(delete(ApiRequest))
    await db.execute(delete(UpdateRecord))
    await db.commit()
    return {"ok": True}
