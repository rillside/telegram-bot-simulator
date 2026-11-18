from fastapi import APIRouter, HTTPException
from backend.app.schemas.process import (
    ProcessStartRequest,
    ProcessStopRequest,
    ProcessStatusResponse,
    ProcessLogEntry
)
from backend.app.services.process_manager import process_manager

router = APIRouter()

@router.get("/{bot_id}/status", response_model=ProcessStatusResponse)
async def get_process_status(bot_id: int):
    return await process_manager.get_status(bot_id)

@router.get("/{bot_id}/logs")
async def get_process_logs(bot_id: int):
    return await process_manager.get_logs(bot_id)

@router.post("/start")
async def start_process(body: ProcessStartRequest):
    try:
        mp = await process_manager.start_process(body.bot_id, body.file_path, body.work_dir)
        return await process_manager.get_status(body.bot_id)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop")
async def stop_process(body: ProcessStopRequest):
    success = await process_manager.stop_process(body.bot_id)
    return await process_manager.get_status(body.bot_id)

@router.post("/restart")
async def restart_process(body: ProcessStopRequest):
    try:
        await process_manager.restart_process(body.bot_id)
        return await process_manager.get_status(body.bot_id)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
