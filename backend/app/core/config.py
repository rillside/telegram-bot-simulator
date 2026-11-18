import os
from pathlib import Path
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ROOT_DIR = BASE_DIR.parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"

DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

class Settings(BaseModel):
    app_name: str = "Telegram Simulator"
    app_version: str = "1.0.0"
    debug: bool = True
    host: str = os.getenv("HOST", "127.0.0.1")
    port: int = int(os.getenv("PORT", "8000"))
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{DATA_DIR / 'telegram_simulator.db'}")
    
    # Uploads
    upload_dir: Path = UPLOAD_DIR
    base_url: str = os.getenv("BASE_URL", "http://127.0.0.1:8000")
    
    # CORS
    cors_origins: list[str] = ["*"]
    root_dir: Path = ROOT_DIR

settings = Settings()
