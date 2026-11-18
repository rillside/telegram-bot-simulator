from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.schemas.chat import ChatCreate, ChatResponse
from backend.app.schemas.message import MessageResponse
from backend.app.services.chat_service import chat_service

router = APIRouter()

@router.get("", response_model=List[ChatResponse])
async def list_chats(user_id: int = Query(...), db: AsyncSession = Depends(get_db)):
    return await chat_service.get_user_chats(db, user_id)

@router.post("", response_model=ChatResponse)
async def create_chat(chat_in: ChatCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await chat_service.get_or_create_chat(db, chat_in.bot_id, chat_in.user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{chat_id}/messages", response_model=List[MessageResponse])
async def get_chat_messages(chat_id: int, db: AsyncSession = Depends(get_db)):
    return await chat_service.get_chat_messages(db, chat_id)
