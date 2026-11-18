from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.schemas.bot import BotCreate, BotResponse
from backend.app.services.bot_service import bot_service

router = APIRouter()

@router.get("", response_model=List[BotResponse])
async def list_bots(db: AsyncSession = Depends(get_db)):
    return await bot_service.get_all_bots(db)

@router.post("", response_model=BotResponse)
async def create_bot(bot_in: BotCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await bot_service.create_bot(db, bot_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{bot_id}", response_model=BotResponse)
async def get_bot(bot_id: int, db: AsyncSession = Depends(get_db)):
    bot = await bot_service.get_bot_by_id(db, bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    return bot

@router.delete("/{bot_id}")
async def delete_bot(bot_id: int, db: AsyncSession = Depends(get_db)):
    success = await bot_service.delete_bot(db, bot_id)
    if not success:
        raise HTTPException(status_code=404, detail="Bot not found")
    return {"ok": True}
