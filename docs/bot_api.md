# Спецификация поддерживаемых методов Telegram Bot API

Локальный базовый URL для обращения библиотек:
```text
http://127.0.0.1:8000/bot<TOKEN>/<METHOD_NAME>
```

Каждый запрос валидируется по токену, фиксируется в журнале для **API Inspector** и возвращает стандартный JSON-ответ формата Telegram Bot API:

Успешный ответ:
```json
{
  "ok": true,
  "result": { ... }
}
```

Ошибка:
```json
{
  "ok": false,
  "error_code": 400,
  "description": "Bad Request: description of error"
}
```

---

## 1. getMe
Возвращает базовую информацию о боте в виде объекта `User`.
- **HTTP метод**: GET или POST.
- **Параметры**: отсутствуют.
- **Пример ответа**:
```json
{
  "ok": true,
  "result": {
    "id": 1,
    "is_bot": true,
    "first_name": "Учебный бот",
    "username": "learning_bot",
    "can_join_groups": true,
    "can_read_all_group_messages": false,
    "supports_inline_queries": false
  }
}
```

---

## 2. getUpdates
Получает входящие события с поддержкой Long Polling.
- **Параметры**:
  - `offset` (integer, optional) — идентификатор первого обновления, которое необходимо вернуть. Подтверждает получение всех обновлений с `update_id < offset`.
  - `limit` (integer, optional, default: 100) — максимальное число обновлений (1–100).
  - `timeout` (integer, optional, default: 0) — таймаут long polling ожидания новых событий в секундах.
  - `allowed_updates` (Array of String / JSON string, optional) — список типов обновлений.
- **Пример ответа**:
```json
{
  "ok": true,
  "result": [
    {
      "update_id": 1001,
      "message": {
        "message_id": 1,
        "date": 1795000000,
        "chat": {
          "id": 12345,
          "type": "private",
          "first_name": "Дмитрий"
        },
        "from": {
          "id": 12345,
          "is_bot": false,
          "first_name": "Дмитрий"
        },
        "text": "/start"
      }
    }
  ]
}
```

---

## 3. sendMessage
Отправляет текстовое сообщение в указанный чат.
- **Параметры**:
  - `chat_id` (integer / string, required) — ID чата.
  - `text` (string, required) — текст сообщения.
  - `reply_to_message_id` (integer, optional) — ID сообщения, на которое дается ответ.
  - `reply_markup` (JSON object / string, optional) — инлайн-клавиатура (`InlineKeyboardMarkup`), реплай-клавиатура (`ReplyKeyboardMarkup`) или удаление клавиатуры (`ReplyKeyboardRemove`).
  - `parse_mode` (string, optional) — режим разметки.
- **Возвращает**: Объект отправленного сообщения `Message`.

---

## 4. forwardMessage
Пересылает сообщение из одного чата в другой.
- **Параметры**:
  - `chat_id` (integer, required) — целевой чат.
  - `from_chat_id` (integer, required) — исходный чат.
  - `message_id` (integer, required) — ID пересылаемого сообщения.

---

## 5. editMessageText
Редактирует текст отправленного ранее сообщения.
- **Параметры**:
  - `chat_id` (integer, required) — ID чата.
  - `message_id` (integer, required) — ID сообщения для изменения.
  - `text` (string, required) — новый текст сообщения.
  - `reply_markup` (JSON, optional) — обновленная клавиатура.
- **Возвращает**: Обновленный объект `Message`.

---

## 6. editMessageReplyMarkup
Редактирует только инлайн-клавиатуру сообщения.
- **Параметры**:
  - `chat_id` (integer, required)
  - `message_id` (integer, required)
  - `reply_markup` (JSON, optional) — новая инлайн-клавиатура.

---

## 7. deleteMessage
Удаляет сообщение из чата.
- **Параметры**:
  - `chat_id` (integer, required)
  - `message_id` (integer, required)
- **Возвращает**: `{"ok": true, "result": true}`.

---

## 8. getChat и getChatMember
Получение информации о чате и статусе участника.
- `getChat`: возвращает объект `Chat` с полями `id`, `type`, `title`.
- `getChatMember`: возвращает объект `ChatMember` (статус `administrator` для бота или `member` для пользователя).

---

## 9. answerCallbackQuery
Отправляет ответ на нажатие кнопки `InlineKeyboardButton` с полем `callback_data`.
- **Параметры**:
  - `callback_query_id` (string, required) — ID входящего запроса.
  - `text` (string, optional) — текст всплывающего уведомления.
  - `show_alert` (boolean, optional) — отобразить модальное окно вместо плавающего уведомления.
- **Возвращает**: `{"ok": true, "result": true}`.
- **Поведение**: В интерфейсе симулятора немедленно отображается toast-уведомление пользователю с переданным текстом!

---

## 10. sendPhoto и sendDocument
Отправка медиафайлов:
- Поддерживает загрузку файлов через стандартный `multipart/form-data` (`files={'photo': ...}` или `files={'document': ...}`) либо прямую передачу URL/имени.
- Файлы сохраняются в директорию `backend/data/uploads` и отдаются через статический маршрут `/uploads/...`.
- В интерфейсе симулятора изображения отображаются в виде превью, а документы — в виде кликабельной плашки скачивания.

---

## 11. Webhook методы
- `setWebhook`, `deleteWebhook`, `getWebhookInfo` возвращают корректные ответы согласно спецификации Telegram Bot API.
