import time
import json
from typing import Dict, Any
from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.core.database import get_db
from backend.app.core.events import event_bus
from backend.app.models.bot import Bot
from backend.app.models.api_request import ApiRequest
from backend.app.bot_api.responses import ok_response, error_response
from backend.app.bot_api.exceptions import TelegramApiException
from backend.app.bot_api.methods import HANDLERS

router = APIRouter()

@router.api_route("/bot{token}/{method_name}", methods=["GET", "POST"])
async def telegram_bot_api_endpoint(
    token: str,
    method_name: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    start_time = time.time()
    
    # 1. Authorize bot by token
    result = await db.execute(select(Bot).where(Bot.token == token))
    bot = result.scalar_one_or_none()
    if not bot:
        execution_time_ms = round((time.time() - start_time) * 1000, 2)
        return error_response(401, "Unauthorized: bot token is invalid", status_code=401)

    # 2. Extract parameters and uploaded files
    params: Dict[str, Any] = {}
    params.update(request.query_params)
    files = {}

    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            body = await request.json()
            if isinstance(body, dict):
                params.update(body)
        except Exception:
            pass
    elif "multipart/form-data" in content_type or "application/x-www-form-urlencoded" in content_type:
        try:
            form_data = await request.form()
            for key, value in form_data.items():
                if hasattr(value, "filename"):  # UploadFile
                    files[key] = value
                else:
                    params[key] = value
        except Exception:
            pass

    # 3. Check if method is supported
    handler = HANDLERS.get(method_name)
    if not handler:
        execution_time_ms = round((time.time() - start_time) * 1000, 2)
        err = error_response(404, f"Not Found: method '{method_name}' not found", status_code=404)
        
        # Log to ApiRequest
        api_req = ApiRequest(
            bot_id=bot.id,
            method=request.method,
            endpoint=method_name,
            params={k: str(v)[:200] for k, v in params.items()},
            response_status=404,
            response_body={"ok": False, "error_code": 404, "description": f"Method '{method_name}' not found"},
            execution_time_ms=execution_time_ms
        )
        db.add(api_req)
        await db.commit()
        await db.refresh(api_req)

        await event_bus.broadcast("api_request", {
            "id": api_req.id,
            "bot_id": bot.id,
            "method": request.method,
            "endpoint": method_name,
            "params": api_req.params,
            "response_status": 404,
            "response_body": api_req.response_body,
            "execution_time_ms": execution_time_ms,
            "created_at": api_req.created_at.isoformat()
        })
        return err

    # 4. Execute handler
    try:
        handler_result = await handler(bot, params, db, files=files)
        execution_time_ms = round((time.time() - start_time) * 1000, 2)
        response_data = ok_response(handler_result)

        # Log for API Inspector (skip empty getUpdates polling heartbeats to avoid flooding DB and UI)
        if method_name != "getUpdates" or handler_result:
            sanitized_params = {k: (f"<file: {v.filename}>" if hasattr(v, "filename") else v) for k, v in params.items()}
            
            api_req = ApiRequest(
                bot_id=bot.id,
                method=request.method,
                endpoint=method_name,
                params=sanitized_params,
                response_status=200,
                response_body=response_data,
                execution_time_ms=execution_time_ms
            )
            db.add(api_req)
            await db.commit()
            await db.refresh(api_req)

            # Broadcast via WebSocket for API Inspector
            await event_bus.broadcast("api_request", {
                "id": api_req.id,
                "bot_id": bot.id,
                "method": request.method,
                "endpoint": method_name,
                "params": sanitized_params,
                "response_status": 200,
                "response_body": response_data,
                "execution_time_ms": execution_time_ms,
                "created_at": api_req.created_at.isoformat()
            })

        return response_data

    except TelegramApiException as e:
        execution_time_ms = round((time.time() - start_time) * 1000, 2)
        err = error_response(e.error_code, e.description, status_code=400)
        
        api_req = ApiRequest(
            bot_id=bot.id,
            method=request.method,
            endpoint=method_name,
            params={k: str(v)[:200] for k, v in params.items()},
            response_status=e.error_code,
            response_body={"ok": False, "error_code": e.error_code, "description": e.description},
            execution_time_ms=execution_time_ms
        )
        db.add(api_req)
        await db.commit()
        await db.refresh(api_req)

        await event_bus.broadcast("api_request", {
            "id": api_req.id,
            "bot_id": bot.id,
            "method": request.method,
            "endpoint": method_name,
            "params": api_req.params,
            "response_status": e.error_code,
            "response_body": api_req.response_body,
            "execution_time_ms": execution_time_ms,
            "created_at": api_req.created_at.isoformat()
        })
        return err

    except Exception as e:
        execution_time_ms = round((time.time() - start_time) * 1000, 2)
        desc = f"Internal Server Error: {str(e)}"
        err = error_response(500, desc, status_code=500)
        return err
