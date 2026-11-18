# Архитектура Telegram Simulator

## 1. Введение и назначение

**Telegram Simulator** — это программный комплекс, предоставляющий локальную изолированную среду для разработки, преподавания и отладки Telegram-ботов на языке Python без необходимости подключения к серверам Telegram и без использования реальных API-токенов.

Главный принцип системы — **настоящая совместимость**: код ученика использует оригинальные немодифицированные библиотеки (`pyTelegramBotAPI`, `aiogram 3`, `python-telegram-bot` и др.), а симулятор эмулирует поведение официального Telegram Bot API на уровне HTTP-протокола.

---

## 2. Общая архитектурная схема

Система состоит из трёх ключевых подсистем:

1. **Telegram Bot API Emulator (Backend)**: HTTP-сервер на FastAPI, реализующий методы Bot API, моделирующий сущности Telegram (Users, Chats, Messages, Updates) и управляющий очередями Long Polling.
2. **Interactive UI (Frontend)**: клиентское SPA на React, TypeScript и Tailwind CSS, визуально и функционально повторяющее интерфейс Telegram Desktop, дополненное панелью разработчика (Developer Inspector).
3. **Process Manager**: подсистема асинхронного управления дочерними процессами Python, собирающая stdout, stderr, tracebacks и контролирующая жизненный цикл бота.

```
+-----------------------------------------------------------------------------------+
|                              Telegram Simulator                                   |
|                                                                                   |
|  +--------------------+        WebSocket (Events / Logs)       +---------------+  |
|  |     Frontend       | <====================================> |    Backend    |  |
|  | (React+TS+Tailwind)|                                        |   (FastAPI)   |  |
|  +--------------------+                                        +---------------+  |
|           ^                                                            ^          |
|           | REST API                                                   | Bot API  |
|           v                                                            v HTTP     |
|  +--------------------+       Async Subprocess Exec            +---------------+  |
|  |   Simulator UI     | -------------------------------------> | Student's Bot |  |
|  | (Chats, Inspector) |        stdout/stderr capture           | (telebot/aio) |  |
|  +--------------------+                                        +---------------+  |
+-----------------------------------------------------------------------------------+
```

---

## 3. Схема сущностей базы данных (ER-модель)

Система сохраняет персистентное состояние в SQLite с использованием SQLAlchemy 2.x Async ORM:

- **Bot**: виртуальный бот (`id`, `name`, `username`, `token`, `description`, `avatar`, `is_running`, `created_at`).
- **User**: виртуальный пользователь (`id`, `first_name`, `last_name`, `username`, `avatar`, `is_bot`, `created_at`).
- **Chat**: чат диалога (`id`, `type`, `title`, `bot_id`, `user_id`, `created_at`).
- **Message**: сообщение (`id`, `chat_id`, `from_user_id`, `from_bot_id`, `is_from_bot`, `date`, `text`, `reply_to_message_id`, `reply_markup`, `media_type`, `media_url`, `file_name`).
- **UpdateRecord**: журнал событий Update (`id`, `bot_id`, `update_type`, `payload`, `created_at`).
- **ApiRequest**: журнал HTTP-запросов к Bot API для API Inspector (`id`, `bot_id`, `method`, `endpoint`, `params`, `response_status`, `response_body`, `execution_time_ms`).
- **CallbackQueryRecord**: учет нажатий инлайн-кнопок (`id`, `bot_id`, `chat_id`, `message_id`, `from_user_id`, `data`).
- **ProcessRecord**: аудит запусков пользовательских процессов (`id`, `bot_id`, `file_path`, `work_dir`, `status`, `pid`, `exit_code`).

---

## 4. Механизм Long Polling

1. Бот отправляет запрос `POST /bot<TOKEN>/getUpdates` с параметрами `offset`, `limit`, `timeout`, `allowed_updates`.
2. Менеджер очередей `UpdateQueueManager`:
   - Находит очередь, закрепленную за данным `bot_id`.
   - Если передан `offset`, все подтверждённые события с `update_id < offset` немедленно удаляются из очереди, исключая повторную выдачу.
   - Если в очереди есть события с `update_id >= offset`, подходящие под фильтр `allowed_updates`, они возвращаются немедленно (до `limit` штук).
   - Если очередь пуста и `timeout > 0`, асинхронный обработчик ожидает срабатывания события `asyncio.Event` до истечения таймаута.
   - При появлении нового события (пользователь написал сообщение или нажал кнопку), событие устанавливается, и ожидавшему запросу возвращается обновленный список.
   - При остановке бота очередь пробуждается и возвращает пустой массив `[]`, предотвращая зависание запроса.

---

## 5. Система межкомпонентных событий и WebSocket

Backend использует централизованную шину `EventBus`, передающую JSON-события через WebSocket (`/ws`):

| Тип события | Назначение |
|---|---|
| `chat_message` | Новое входящее или исходящее сообщение в чате |
| `message_edit` | Изменение текста или клавиатуры сообщения |
| `message_delete` | Удаление сообщения из переписки |
| `process_log` | Строка потока вывода `stdout`, `stderr` или `system` |
| `process_status` | Смена статуса процесса (`STARTING`, `RUNNING`, `STOPPED`, `ERROR`) |
| `api_request` | Фиксация вызова метода Bot API (для API Inspector) |
| `update_event` | Фиксация генерации Telegram Update (для Updates Inspector) |
| `callback_query_answered` | Результат вызова `answerCallbackQuery` для показа уведомления пользователю |
