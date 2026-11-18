import sys
from pathlib import Path

# Add project root to sys.path so 'backend...' imports work regardless of launch directory
_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.core.config import settings
from backend.app.core.database import init_db
from backend.app.bot_api.router import router as bot_api_router
from backend.app.api.websocket import router as ws_router
from backend.app.api.routes.bots import router as bots_router
from backend.app.api.routes.users import router as users_router
from backend.app.api.routes.chats import router as chats_router
from backend.app.api.routes.messages import router as messages_router
from backend.app.api.routes.processes import router as processes_router
from backend.app.api.routes.simulator import router as simulator_router
from backend.app.services.process_manager import process_manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown: gracefully terminate all running child processes
    for bot_id in list(process_manager._processes.keys()):
        try:
            await process_manager.stop_process(bot_id)
        except Exception:
            pass

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file serving for uploads
app.mount("/uploads", StaticFiles(directory=str(settings.upload_dir)), name="uploads")

# Mount Telegram Bot API router (handles /bot<token>/<method>)
app.include_router(bot_api_router)

# Mount Frontend WebSocket
app.include_router(ws_router)

# Mount REST API for Simulator UI
app.include_router(bots_router, prefix="/api/bots", tags=["Bots"])
app.include_router(users_router, prefix="/api/users", tags=["Users"])
app.include_router(chats_router, prefix="/api/chats", tags=["Chats"])
app.include_router(messages_router, prefix="/api/messages", tags=["Messages"])
app.include_router(processes_router, prefix="/api/processes", tags=["Processes"])
app.include_router(simulator_router, prefix="/api/simulator", tags=["Simulator"])

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version
    }

# Serve built frontend if dist exists
dist_dir = settings.root_dir / "frontend" / "dist"
if dist_dir.exists():
    app.mount("/", StaticFiles(directory=str(dist_dir), html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.host, port=settings.port, app_dir=str(_root), reload=False)
