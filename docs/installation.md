# Установка и запуск Telegram Simulator

## 1. Системные требования

- **Операционная система**: Windows 10/11, macOS или Linux.
- **Python**: версия 3.12 или выше.
- **Node.js**: версия 18 или выше (для сборки фронтенда).
- **Пакетный менеджер**: pip, npm.

---

## 2. Установка зависимостей

### 2.1. Backend (Python)

Перейдите в директорию `backend` и установите зависимости:

```bash
cd backend
pip install -r requirements.txt
```

Основные зависимости:
- `fastapi` — веб-фреймворк для API и эмуляции Bot API.
- `uvicorn` — ASGI-сервер.
- `sqlalchemy` и `aiosqlite` — асинхронный ORM и работа со SQLite.
- `greenlet` — поддержка асинхронности в SQLAlchemy.
- `pyTelegramBotAPI` и `aiogram` — поддерживаемые фреймворки ботов.
- `pytest` и `pytest-asyncio` — автоматическое тестирование.

### 2.2. Frontend (React + TypeScript)

Перейдите в директорию `frontend` и установите npm-зависимости:

```bash
cd ../frontend
npm install
```

Соберите фронтенд в статическую сборку (production build):

```bash
npm run build
```

---

## 3. Запуск приложения

Telegram Simulator поддерживает два режима запуска.

### Вариант А: Единый запуск (рекомендуемый для использования)

Если фронтенд собран командой `npm run build`, FastAPI автоматически отдаёт графический интерфейс прямо из корня:

```bash
python run.py
```
или:
```bash
python backend/app/main.py
```

После этого откройте браузер по адресу:
**http://127.0.0.1:8000**

Вы получите полноценно работающий симулятор и интерфейс на одном порту!

### Вариант Б: Режим разработки (Hot Reload для React)

В одном терминале запустите Backend:
```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

Во втором терминале запустите Vite dev server:
```bash
cd frontend
npm run dev
```

Интерфейс разработки будет доступен по адресу **http://localhost:3000** (с автоматическим проксированием запросов к бэкенду на порт 8000).

---

## 4. Запуск автоматических тестов

Для запуска полного набора тестов выполните команду из корневой директории:

```bash
python -m pytest backend/app/tests -v
```

Все 9 тестовых наборов (включая проверку интеграции с pyTelegramBotAPI и aiogram 3) должны завершиться со статусом `PASSED`.
