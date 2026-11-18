import { Bot, User, Chat, Message, ProcessStatus, ProcessLogEntry, ApiRequestLog, UpdateLog } from '../types';

const BASE = '/api';

export const api = {
  // Bots
  async getBots(): Promise<Bot[]> {
    const res = await fetch(`${BASE}/bots`);
    return res.json();
  },

  async createBot(data: { name: string; username: string; description?: string }): Promise<Bot> {
    const res = await fetch(`${BASE}/bots`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Failed to create bot');
    return res.json();
  },

  async deleteBot(botId: number): Promise<void> {
    await fetch(`${BASE}/bots/${botId}`, { method: 'DELETE' });
  },

  // Users
  async getUsers(): Promise<User[]> {
    const res = await fetch(`${BASE}/users`);
    return res.json();
  },

  async createUser(data: { first_name: string; last_name?: string; username?: string }): Promise<User> {
    const res = await fetch(`${BASE}/users`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return res.json();
  },

  // Chats
  async getChats(userId: number): Promise<Chat[]> {
    const res = await fetch(`${BASE}/chats?user_id=${userId}`);
    return res.json();
  },

  async createChat(botId: number, userId: number): Promise<Chat> {
    const res = await fetch(`${BASE}/chats`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ bot_id: botId, user_id: userId }),
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Failed to create chat');
    return res.json();
  },

  async getMessages(chatId: number): Promise<Message[]> {
    const res = await fetch(`${BASE}/chats/${chatId}/messages`);
    return res.json();
  },

  // Messages
  async sendMessage(data: {
    chat_id: number;
    user_id: number;
    text?: string;
    media_type?: string;
    media_url?: string;
    file_name?: string;
  }): Promise<Message> {
    const res = await fetch(`${BASE}/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return res.json();
  },

  async clickInlineButton(data: {
    chat_id: number;
    user_id: number;
    message_id: number;
    callback_data: string;
  }): Promise<{ ok: boolean; callback_query_id: string }> {
    const res = await fetch(`${BASE}/messages/inline-click`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return res.json();
  },

  // Process
  async getProcessStatus(botId: number): Promise<ProcessStatus> {
    const res = await fetch(`${BASE}/processes/${botId}/status`);
    return res.json();
  },

  async getProcessLogs(botId: number): Promise<ProcessLogEntry[]> {
    const res = await fetch(`${BASE}/processes/${botId}/logs`);
    return res.json();
  },

  async startProcess(botId: number, filePath: string, workDir?: string): Promise<ProcessStatus> {
    const res = await fetch(`${BASE}/processes/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ bot_id: botId, file_path: filePath, work_dir: workDir }),
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Failed to start process');
    return res.json();
  },

  async stopProcess(botId: number): Promise<ProcessStatus> {
    const res = await fetch(`${BASE}/processes/stop`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ bot_id: botId }),
    });
    return res.json();
  },

  async restartProcess(botId: number): Promise<ProcessStatus> {
    const res = await fetch(`${BASE}/processes/restart`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ bot_id: botId }),
    });
    return res.json();
  },

  // Simulator Inspector
  async getApiRequests(botId?: number): Promise<ApiRequestLog[]> {
    const url = botId !== undefined ? `${BASE}/simulator/api-requests?bot_id=${botId}` : `${BASE}/simulator/api-requests`;
    const res = await fetch(url);
    return res.json();
  },

  async getUpdates(botId?: number): Promise<UpdateLog[]> {
    const url = botId !== undefined ? `${BASE}/simulator/updates?bot_id=${botId}` : `${BASE}/simulator/updates`;
    const res = await fetch(url);
    return res.json();
  },

  async clearSimulatorLogs(): Promise<void> {
    await fetch(`${BASE}/simulator/clear`, { method: 'POST' });
  },
};
