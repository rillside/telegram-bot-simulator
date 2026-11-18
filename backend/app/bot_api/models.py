from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field

class TelegramUser(BaseModel):
    id: int
    is_bot: bool
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None
    can_join_groups: Optional[bool] = None
    can_read_all_group_messages: Optional[bool] = None
    supports_inline_queries: Optional[bool] = None

class TelegramChat(BaseModel):
    id: int
    type: str  # private, group, supergroup, channel
    title: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class PhotoSize(BaseModel):
    file_id: str
    file_unique_id: str
    width: int
    height: int
    file_size: Optional[int] = None

class Document(BaseModel):
    file_id: str
    file_unique_id: str
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None

class InlineKeyboardButton(BaseModel):
    text: str
    url: Optional[str] = None
    callback_data: Optional[str] = None

class InlineKeyboardMarkup(BaseModel):
    inline_keyboard: List[List[InlineKeyboardButton]]

class KeyboardButton(BaseModel):
    text: str
    request_contact: Optional[bool] = None
    request_location: Optional[bool] = None

class ReplyKeyboardMarkup(BaseModel):
    keyboard: List[List[Union[KeyboardButton, str]]]
    resize_keyboard: Optional[bool] = False
    one_time_keyboard: Optional[bool] = False
    is_persistent: Optional[bool] = False
    input_field_placeholder: Optional[str] = None
    selective: Optional[bool] = False

class ReplyKeyboardRemove(BaseModel):
    remove_keyboard: bool = True
    selective: Optional[bool] = False

class TelegramMessage(BaseModel):
    message_id: int
    date: int
    chat: TelegramChat
    from_: Optional[TelegramUser] = Field(None, alias="from")
    text: Optional[str] = None
    reply_to_message: Optional[Any] = None
    reply_markup: Optional[Union[InlineKeyboardMarkup, Dict[str, Any]]] = None
    photo: Optional[List[PhotoSize]] = None
    document: Optional[Document] = None
    caption: Optional[str] = None

    class Config:
        populate_by_name = True

class TelegramCallbackQuery(BaseModel):
    id: str
    from_: TelegramUser = Field(..., alias="from")
    message: Optional[TelegramMessage] = None
    chat_instance: str = "simulator_chat_instance"
    data: Optional[str] = None

    class Config:
        populate_by_name = True

class TelegramUpdate(BaseModel):
    update_id: int
    message: Optional[TelegramMessage] = None
    edited_message: Optional[TelegramMessage] = None
    callback_query: Optional[TelegramCallbackQuery] = None

    class Config:
        populate_by_name = True
