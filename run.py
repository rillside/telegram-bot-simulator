import sys
import os
import time
import threading
import webbrowser
from pathlib import Path

# Configure UTF-8 on Windows console to prevent UnicodeEncodeError in cp1251
if sys.platform == "win32":
    try:
        if sys.stdout and hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if sys.stderr and hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ensure root directory is in sys.path
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

def open_browser():
    """Автоматическое открытие веб-интерфейса в браузере при запуске."""
    time.sleep(1.2)
    try:
        webbrowser.open("http://127.0.0.1:8000")
    except Exception:
        pass

if __name__ == "__main__":
    import uvicorn
    from backend.app.main import app
    from backend.app.core.config import settings

    print("=" * 65)
    print("[*] Telegram Simulator запущен и готов к работе!")
    print(f"[>] Веб-интерфейс: http://{settings.host}:{settings.port}")
    print("[i] Чтобы остановить сервер, нажмите Ctrl+C или закройте это окно")
    print("=" * 65)

    # Запуск авто-открытия браузера в отдельном потоке
    threading.Thread(target=open_browser, daemon=True).start()

    # Запуск сервера Uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port, reload=False)
