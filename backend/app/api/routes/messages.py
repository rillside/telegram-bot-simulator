from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.schemas.message import (
    SendUserMessageRequest,
    ClickInlineButtonRequest,
    MessageResponse
)
from backend.app.services.message_service import message_service

router = APIRouter()

@router.post("", response_model=MessageResponse)
async def send_user_message(
    body: SendUserMessageRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        return await message_service.send_user_message(
            db=db,
            chat_id=body.chat_id,
            user_id=body.user_id,
            text=body.text,
            media_type=body.media_type,
            media_url=body.media_url,
            file_name=body.file_name,
            reply_to_message_id=body.reply_to_message_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/inline-click")
async def click_inline_button(
    body: ClickInlineButtonRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        cbq_id = await message_service.click_inline_button(
            db=db,
            chat_id=body.chat_id,
            user_id=body.user_id,
            message_id=body.message_id,
            callback_data=body.callback_data
        )
        return {"ok": True, "callback_query_id": cbq_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
