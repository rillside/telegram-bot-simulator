import React, { useState, useEffect } from 'react';
import { Bot, User, Chat, Message, ProcessStatus, ProcessLogEntry, ApiRequestLog, UpdateLog } from './types';
import { api } from './services/api';
import { wsClient } from './services/websocket';
import { Sidebar } from './components/sidebar/Sidebar';
import { ChatArea } from './components/chat/ChatArea';
import { BotDetailsPanel } from './components/bot_info/BotDetailsPanel';
import { DeveloperPanel } from './components/inspector/DeveloperPanel';

export const App: React.FC = () => {
  const [bots, setBots] = useState<Bot[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [activeUser, setActiveUser] = useState<User | null>(null);
  const [chats, setChats] = useState<Chat[]>([]);
  const [selectedChatId, setSelectedChatId] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);

  // Process & Inspector states
  const [processStatus, setProcessStatus] = useState<ProcessStatus | undefined>(undefined);
  const [logs, setLogs] = useState<ProcessLogEntry[]>([]);
  const [apiRequests, setApiRequests] = useState<ApiRequestLog[]>([]);
  const [updates, setUpdates] = useState<UpdateLog[]>([]);

  // UI Drawer states
  const [isDevPanelOpen, setIsDevPanelOpen] = useState(false);
  const [isBotDetailsOpen, setIsBotDetailsOpen] = useState(false);
  const [debugMode, setDebugMode] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // 1. Initial Load: Users & Bots
  useEffect(() => {
    const init = async () => {
      try {
        const [fetchedUsers, fetchedBots] = await Promise.all([
          api.getUsers(),
          api.getBots(),
        ]);
        setUsers(fetchedUsers);
        setBots(fetchedBots);
        if (fetchedUsers.length > 0) {
          setActiveUser(fetchedUsers[0]);
        }
      } catch (err) {
        console.error('Initialization error:', err);
      }
    };
    init();
  }, []);

  // 2. Load Chats when activeUser changes
  useEffect(() => {
    if (!activeUser) return;
    const loadChats = async () => {
      try {
        const fetchedChats = await api.getChats(activeUser.id);
        setChats(fetchedChats);
        if (fetchedChats.length > 0 && !selectedChatId) {
          setSelectedChatId(fetchedChats[0].id);
        }
      } catch (err) {
        console.error('Failed to load chats:', err);
      }
    };
    loadChats();
  }, [activeUser]);

  // 3. Load Messages and Process Status when selectedChatId changes
  const activeChat = chats.find((c) => c.id === selectedChatId) || null;

  useEffect(() => {
    if (!selectedChatId || !activeChat) return;

    const loadChatData = async () => {
      try {
        const [msgs, pStatus, pLogs, apiReqs, upds] = await Promise.all([
          api.getMessages(selectedChatId),
          api.getProcessStatus(activeChat.bot_id),
          api.getProcessLogs(activeChat.bot_id),
          api.getApiRequests(activeChat.bot_id),
          api.getUpdates(activeChat.bot_id),
        ]);
        setMessages(msgs);
        setProcessStatus(pStatus);
        setLogs(pLogs);
        setApiRequests(apiReqs);
        setUpdates(upds);
      } catch (err) {
        console.error('Failed to load chat data:', err);
      }
    };
    loadChatData();
  }, [selectedChatId, activeChat?.bot_id]);

  // 4. Connect WebSocket & Subscribe to live events
  useEffect(() => {
    wsClient.connect();

    const unsubscribe = wsClient.subscribe((event) => {
      const { type, data } = event;

      if (type === 'chat_message') {
        const newMsg: Message = data.message;
        // Update messages if it belongs to selected chat
        setMessages((prev) => {
          if (prev.some((m) => m.id === newMsg.id)) return prev;
          if (newMsg.chat_id === selectedChatId) {
            return [...prev, newMsg];
          }
          return prev;
        });

        // Update chat's last message in sidebar
        setChats((prev) =>
          prev.map((c) => {
            if (c.id === newMsg.chat_id) {
              return {
                ...c,
                last_message: {
                  id: newMsg.id,
                  text: newMsg.text,
                  date: newMsg.date,
                  is_from_bot: newMsg.is_from_bot,
                  media_type: newMsg.media_type,
                },
              };
            }
            return c;
          })
        );
      } else if (type === 'message_edit') {
        const edited: Partial<Message> = data.message;
        setMessages((prev) =>
          prev.map((m) => (m.id === edited.id ? { ...m, ...edited } : m))
        );
      } else if (type === 'message_delete') {
        const { message_id } = data;
        setMessages((prev) => prev.filter((m) => m.id !== message_id));
      } else if (type === 'process_log') {
        const logEntry: ProcessLogEntry = data;
        if (!activeChat || logEntry.bot_id === activeChat.bot_id) {
          setLogs((prev) => [...prev, logEntry]);
        }
      } else if (type === 'process_status') {
        const pStatus: ProcessStatus = data;
        if (activeChat && pStatus.bot_id === activeChat.bot_id) {
          setProcessStatus(pStatus);
        }
        // Update bot running state in list
        setBots((prev) =>
          prev.map((b) =>
            b.id === pStatus.bot_id
              ? { ...b, is_running: pStatus.status === 'RUNNING' }
              : b
          )
        );
        setChats((prev) =>
          prev.map((c) =>
            c.bot_id === pStatus.bot_id && c.bot
              ? { ...c, bot: { ...c.bot, is_running: pStatus.status === 'RUNNING' } }
              : c
          )
        );
      } else if (type === 'api_request') {
        const req: ApiRequestLog = data;
        setApiRequests((prev) => [req, ...prev]);
      } else if (type === 'update_event') {
        const upd: UpdateLog = data;
        setUpdates((prev) => [upd, ...prev]);
      } else if (type === 'callback_query_answered') {
        const { text } = data;
        if (text) {
          setToastMessage(text);
          setTimeout(() => setToastMessage(null), 3000);
        }
      }
    });

    return () => {
      unsubscribe();
      wsClient.close();
    };
  }, [selectedChatId, activeChat?.bot_id]);

  // Actions
  const handleSendMessage = async (text: string) => {
    if (!activeChat || !activeUser) return;
    try {
      await api.sendMessage({
        chat_id: activeChat.id,
        user_id: activeUser.id,
        text,
      });
    } catch (err) {
      console.error('Failed to send message:', err);
    }
  };

  const handleInlineClick = async (messageId: number, callbackData: string) => {
    if (!activeChat || !activeUser) return;
    try {
      await api.clickInlineButton({
        chat_id: activeChat.id,
        user_id: activeUser.id,
        message_id: messageId,
        callback_data: callbackData,
      });
    } catch (err) {
      console.error('Failed to click inline button:', err);
    }
  };

  const handleCreateBot = async (data: { name: string; username: string; description?: string }) => {
    const newBot = await api.createBot(data);
    setBots((prev) => [newBot, ...prev]);

    // Automatically create chat with active user
    if (activeUser) {
      const newChat = await api.createChat(newBot.id, activeUser.id);
      setChats((prev) => [newChat, ...prev]);
      setSelectedChatId(newChat.id);
      setIsBotDetailsOpen(true);
    }
  };

  const handleCreateUser = async (name: string, username: string) => {
    const newUser = await api.createUser({ first_name: name, username });
    setUsers((prev) => [...prev, newUser]);
    setActiveUser(newUser);
  };

  const handleStartChatWithBot = async (botId: number) => {
    if (!activeUser) return;
    const newChat = await api.createChat(botId, activeUser.id);
    const existing = chats.find((c) => c.id === newChat.id);
    if (!existing) {
      setChats((prev) => [newChat, ...prev]);
    }
    setSelectedChatId(newChat.id);
  };

  const handleStartProcess = async (botId: number, filePath: string) => {
    try {
      const status = await api.startProcess(botId, filePath);
      setProcessStatus(status);
      setIsDevPanelOpen(true);
    } catch (err: any) {
      alert(`Не удалось запустить бота: ${err.message || err}`);
    }
  };

  const handleStopProcess = async (botId: number) => {
    const status = await api.stopProcess(botId);
    setProcessStatus(status);
  };

  const handleRestartProcess = async (botId: number) => {
    const status = await api.restartProcess(botId);
    setProcessStatus(status);
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-tg-bg text-tg-text">
      {/* Toast Notification for answerCallbackQuery */}
      {toastMessage && (
        <div className="fixed top-5 left-1/2 -translate-x-1/2 z-50 bg-slate-900 border border-tg-accent/60 shadow-2xl px-5 py-2.5 rounded-xl text-sm font-semibold text-tg-accent animate-in fade-in slide-in-from-top-4">
          🔔 {toastMessage}
        </div>
      )}

      {/* Left Sidebar */}
      <Sidebar
        chats={chats}
        bots={bots}
        users={users}
        activeUser={activeUser}
        selectedChatId={selectedChatId}
        onSelectChat={(id) => setSelectedChatId(id)}
        onSelectUser={(u) => setActiveUser(u)}
        onCreateBot={handleCreateBot}
        onCreateUser={handleCreateUser}
        onStartChatWithBot={handleStartChatWithBot}
      />

      {/* Main Center + Bottom Layout */}
      <div className="flex-1 flex flex-col h-full min-w-0">
        <ChatArea
          chat={activeChat}
          messages={messages}
          processStatus={processStatus}
          isDevPanelOpen={isDevPanelOpen}
          onToggleDevPanel={() => setIsDevPanelOpen(!isDevPanelOpen)}
          isBotDetailsOpen={isBotDetailsOpen}
          onToggleBotDetails={() => setIsBotDetailsOpen(!isBotDetailsOpen)}
          debugMode={debugMode}
          onToggleDebugMode={() => setDebugMode(!debugMode)}
          onSendMessage={handleSendMessage}
          onInlineClick={handleInlineClick}
        />

        {/* Developer Drawer */}
        <DeveloperPanel
          isOpen={isDevPanelOpen}
          onClose={() => setIsDevPanelOpen(false)}
          logs={logs}
          updates={updates}
          apiRequests={apiRequests}
          onClearLogs={() => setLogs([])}
          onClearUpdates={() => setUpdates([])}
          onClearApiRequests={() => setApiRequests([])}
        />
      </div>

      {/* Right Sidebar: Bot Details & Process Controls */}
      <BotDetailsPanel
        bot={activeChat?.bot}
        processStatus={processStatus}
        isOpen={isBotDetailsOpen}
        onClose={() => setIsBotDetailsOpen(false)}
        onStartProcess={handleStartProcess}
        onStopProcess={handleStopProcess}
        onRestartProcess={handleRestartProcess}
      />
    </div>
  );
};

export default App;
