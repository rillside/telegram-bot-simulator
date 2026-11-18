export interface Bot {
  id: number;
  name: string;
  username: string;
  token: string;
  description?: string;
  avatar?: string;
  is_running: boolean;
  created_at: string;
}

export interface User {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  avatar?: string;
  is_bot: boolean;
  created_at: string;
}

export interface Chat {
  id: number;
  type: string;
  title?: string;
  bot_id: number;
  user_id: number;
  created_at: string;
  bot?: Bot;
  user?: User;
  last_message?: {
    id: number;
    text?: string;
    date: number;
    is_from_bot: boolean;
    media_type?: string;
  };
  unread_count?: number;
}

export interface InlineKeyboardButton {
  text: string;
  url?: string;
  callback_data?: string;
}

export interface InlineKeyboardMarkup {
  inline_keyboard: InlineKeyboardButton[][];
}

export interface KeyboardButton {
  text: string;
}

export interface ReplyKeyboardMarkup {
  keyboard: (KeyboardButton | string)[][];
  resize_keyboard?: boolean;
  one_time_keyboard?: boolean;
  is_persistent?: boolean;
  input_field_placeholder?: string;
  selective?: boolean;
}

export interface Message {
  id: number;
  chat_id: number;
  from_user_id?: number;
  from_bot_id?: number;
  is_from_bot: boolean;
  date: number;
  text?: string;
  reply_to_message_id?: number;
  reply_markup?: InlineKeyboardMarkup | ReplyKeyboardMarkup | any;
  media_type?: 'photo' | 'document';
  media_url?: string;
  file_name?: string;
  created_at: string;
}

export interface ProcessStatus {
  id?: number;
  bot_id: number;
  file_path?: string;
  work_dir?: string;
  status: 'STOPPED' | 'STARTING' | 'RUNNING' | 'STOPPING' | 'ERROR';
  pid?: number;
  exit_code?: number;
  started_at?: string;
  stopped_at?: string;
}

export interface ProcessLogEntry {
  bot_id: number;
  timestamp: number;
  stream: 'stdout' | 'stderr' | 'system';
  text: string;
}

export interface ApiRequestLog {
  id: number;
  bot_id?: number;
  method: string;
  endpoint: string;
  params?: Record<string, any>;
  response_status: number;
  response_body?: any;
  execution_time_ms: number;
  created_at: string;
}

export interface UpdateLog {
  id: number;
  bot_id: number;
  update_type: string;
  payload: Record<string, any>;
  created_at: string;
}
