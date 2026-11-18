# Telegram Simulator

**Telegram Simulator** — локальная учебная платформа и среда разработки, позволяющая запускать настоящие Python-боты, написанные на `pyTelegramBotAPI` (telebot) и `aiogram 3`, без подключения к реальным серверам Telegram и без использования боевых токенов.

Проект включает в себя полноценный эмулятор Telegram Bot API, менеджер изолированных дочерних процессов и современный графический интерфейс в стиле Telegram Desktop с панелью разработчика (Console, Updates Inspector, API Inspector).

---

## 🌟 Основные возможности

- **100% совместимость с оригинальными библиотеками**: никаких самописных форков и модификаций — боты работают с установленными из PyPI библиотеками `telebot` и `aiogram`.
- **Эмуляция Telegram Bot API**:
  - `getMe`
  - `getUpdates` (полноценный Long Polling с `offset`, `limit`, `timeout`, `allowed_updates` и гарантией отсутствия дублей)
  - `sendMessage` (поддержка `InlineKeyboardMarkup` и `ReplyKeyboardMarkup`)
  - `forwardMessage`
  - `editMessageText` и `editMessageReplyMarkup`
  - `deleteMessage`
  - `getChat` и `getChatMember`
  - `answerCallbackQuery` (с отображением toast-уведомлений в UI)
  - `sendPhoto` и `sendDocument` (с загрузкой через multipart и локальной раздачей)
  - `setWebhook`, `deleteWebhook`, `getWebhookInfo`
- **Графический интерфейс Telegram Desktop**:
  - Список диалогов с аватарами, поиском и временем последнего сообщения
  - Переписка в реальном времени через WebSocket
  - Визуализация сообщений, фотографий и документов
  - Интерактивные кнопки Inline Keyboard (с генерацией реальных CallbackQuery)
  - Интерактивные кнопки Reply Keyboard (с отправкой текста от лица пользователя)
  - Система виртуальных пользователей: возможность переключаться между разными учениками и проверять работу бота с несколькими собеседниками одновременно
- **Process Manager**:
  - Запуск, остановка и перезапуск Python-скрипта бота
  - Контроль жизненного цикла процесса, статусы (`STOPPED`, `STARTING`, `RUNNING`, `STOPPING`, `ERROR`)
  - Асинхронный перехват `stdout`, `stderr` и полных tracebacks в реальном времени
  - Предотвращение зависших long-polling запросов при завершении процесса
- **Панель разработчика (Developer Inspector)**:
  - **Console**: live-поток вывода бота (`stdout`, `stderr`, `print()`, исключения)
  - **Updates Inspector**: список сгенерированных событий `Update` с возможностью просмотра полного JSON-объекта
  - **API Inspector**: аудит всех HTTP-запросов к Bot API с параметрами, телом ответа и временем выполнения в миллисекундах
- **Персистентное хранилище (SQLite + SQLAlchemy 2.x)**:
  - Боты, пользователи, чаты и история сообщений сохраняются между перезапусками приложения.

---

## 📋 Системные требования

- **Python**: 3.12+
- **Node.js**: 18+ (для сборки frontend)
- **ОС**: Windows, macOS, Linux

---

## 🚀 Быстрый старт

### 1. Установка зависимостей Backend

```bash
cd backend
pip install -r requirements.txt
```

### 2. Сборка Frontend

```bash
cd ../frontend
npm install
npm run build
```

### 3. Запуск приложения

Запустите сервер одной командой:

```bash
python run.py
```

или:

```bash
python backend/app/main.py
```

После запуска откройте браузер:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 🤖 Подключение библиотек

### 1. Подключение pyTelegramBotAPI (telebot)

Переопределите `apihelper.API_URL` перед созданием экземпляра бота:

```python
import telebot
from telebot import apihelper

# Направляем библиотеку на локальный симулятор
apihelper.API_URL = "http://127.0.0.1:8000/bot{0}/{1}"

# Токен берется из интерфейса Telegram Simulator
bot = telebot.TeleBot("1:SIMULATOR_TOKEN")


@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "Привет! Я работаю в локальном Telegram Simulator!")


@bot.message_handler(func=lambda msg: True)
def echo(message):
    bot.send_message(message.chat.id, f"Вы написали: {message.text}")


if __name__ == "__main__":
    bot.infinity_polling()
```

### 2. Подключение aiogram 3

Переопределите `TelegramAPIServer` и передайте его в сессию:

```python
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.filters import CommandStart
from aiogram.types import Message

API = TelegramAPIServer.from_base("http://127.0.0.1:8000")
session = AiohttpSession(api=API)

bot = Bot(token="1:SIMULATOR_TOKEN", session=session)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Привет! Я асинхронный бот на aiogram 3!")


@dp.message()
async def echo(message: Message):
    await message.answer(f"Эхо: {message.text}")


async def main():
    try:
        await dp.start_polling(bot)
    finally:
        await session.close()


if __name__ == "__main__":
    asyncio.run(main())
```

Готовые рабочие примеры с Inline и Reply клавиатурами находятся в папках:
- [examples/telebot/](file:///c:/Users/Дмитрий/Downloads/tgemulator/examples/telebot/)
- [examples/aiogram/](file:///c:/Users/Дмитрий/Downloads/tgemulator/examples/aiogram/)

---

## 🧪 Автоматическое тестирование

Проект полностью покрыт автоматическими тестами:

```bash
python -m pytest backend/app/tests -v
```

Покрыты сценарии:
- Unit-тесты генерации Telegram Update и моделей сообщений.
- Авторизация токенов симулятора и обработка параметров.
- Очереди Long Polling, подтверждение offset, многопоточная изоляция и отмена при остановке.
- Сквозной цикл взаимодействия с настоящим **pyTelegramBotAPI**.
- Сквозной цикл взаимодействия с настоящим **aiogram 3** (включая обработку CallbackQuery).
- Управление процессами, асинхронный перехват потоков вывода и аварийное завершение.
- Персистентное хранение сущностей в SQLite.

---

## 📂 Структура проекта

```text
telegram-simulator/
├── backend/
│   ├── app/
│   │   ├── main.py                   # Точка входа FastAPI и раздача интерфейса
│   │   ├── api/
│   │   │   ├── routes/               # REST API симулятора (боты, чаты, сообщения, процессы)
│   │   │   └── websocket.py          # WebSocket для real-time событий и логов
│   │   ├── bot_api/                  # Эмулятор Telegram Bot API
│   │   │   ├── router.py             # Маршрутизатор /bot<TOKEN>/<METHOD>
│   │   │   ├── methods.py            # Обработчики getMe, getUpdates, sendMessage и др.
│   │   │   ├── polling.py            # Менеджер очередей Long Polling
│   │   │   ├── updates.py            # Фабрика объектов Telegram Update
│   │   │   └── keyboards.py          # Парсер клавиатур
│   │   ├── core/                     # Конфигурация, база данных, event bus
│   │   ├── services/                 # Бизнес-логика и Process Manager
│   │   ├── models/                   # Модели SQLAlchemy 2.x
│   │   ├── schemas/                  # Pydantic схемы
│   │   └── tests/                    # Комплекс автоматических тестов
│   ├── requirements.txt
│   └── pyproject.toml
│
├── frontend/
│   ├── src/
│   │   ├── components/               # Компоненты интерфейса (чат, клавиатуры, инспекторы)
│   │   ├── services/                 # Клиенты API и WebSocket
│   │   ├── types/                    # Интерфейсы TypeScript
│   │   ├── App.tsx                   # Главный компонент
│   │   └── main.tsx
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
│
├── examples/                         # Примеры ботов на telebot и aiogram
├── docs/                             # Полная документация проекта
└── README.md
```

---

## 🔒 Безопасность и ограничения локального прототипа

1. В текущей версии для локального использования код учеников запускается в отдельном асинхронном процессе Python с ограничением прав доступа и перехватом вывода.
2. Для многопользовательского коммерческого развертывания или онлайн-курсов с запуском произвольного кода рекомендуется запуск процессов внутри изолированных Docker-контейнеров с лимитами RAM, CPU и изоляцией сети.
