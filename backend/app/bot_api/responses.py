from typing import Any, Dict
from fastapi.responses import JSONResponse

def ok_response(result: Any) -> Dict[str, Any]:
    return {
        "ok": True,
        "result": result
    }

def error_response(error_code: int, description: str, status_code: int = 400) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "ok": False,
            "error_code": error_code,
            "description": description
        }
    )
