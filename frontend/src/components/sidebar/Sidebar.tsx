import React, { useState } from 'react';
import { Chat, User, Bot } from '../../types';
import { ChatItem } from './ChatItem';
import { UserSwitcher } from './UserSwitcher';
import { NewBotModal } from './NewBotModal';
import { Search, Plus, MessageSquarePlus, Bot as BotIcon, Send } from 'lucide-react';

interface Props {
  chats: Chat[];
  bots: Bot[];
  users: User[];
  activeUser: User | null;
  selectedChatId: number | null;
  onSelectChat: (chatId: number) => void;
  onSelectUser: (user: User) => void;
  onCreateBot: (data: { name: string; username: string; description?: string }) => Promise<void>;
  onCreateUser: (name: string, username: string) => Promise<void>;
  onStartChatWithBot: (botId: number) => Promise<void>;
}

export const Sidebar: React.FC<Props> = ({
  chats,
  bots,
  users,
  activeUser,
  selectedChatId,
  onSelectChat,
  onSelectUser,
  onCreateBot,
  onCreateUser,
  onStartChatWithBot,
}) => {
  const [search, setSearch] = useState('');
  const [isBotModalOpen, setIsBotModalOpen] = useState(false);
  const [isNewChatDropdownOpen, setIsNewChatDropdownOpen] = useState(false);

  const filteredChats = chats.filter((c) => {
    const title = c.bot?.name || c.title || '';
    const username = c.bot?.username || '';
    const q = search.toLowerCase();
    return title.toLowerCase().includes(q) || username.toLowerCase().includes(q);
  });

  return (
    <aside className="w-80 h-full bg-tg-sidebar border-r border-tg-border flex flex-col flex-shrink-0">
      {/* Header */}
      <div className="p-3 border-b border-tg-border flex flex-col gap-2.5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-sky-500 to-blue-600 flex items-center justify-center text-white shadow">
              <Send className="w-4 h-4 transform rotate-[-20deg]" />
            </div>
            <div>
              <h1 className="font-bold text-sm text-tg-text leading-tight">Telegram Simulator</h1>
              <p className="text-[10px] text-tg-accent font-medium">Local Bot Environment</p>
            </div>
          </div>
          <UserSwitcher
            users={users}
            activeUser={activeUser}
            onSelectUser={onSelectUser}
            onCreateUser={onCreateUser}
          />
        </div>

        {/* Search & Actions */}
        <div className="flex items-center gap-1.5">
          <div className="relative flex-1">
            <Search className="w-4 h-4 absolute left-2.5 top-2.5 text-tg-textMuted" />
            <input
              type="text"
              placeholder="Поиск по чатам..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-slate-900 border border-tg-border rounded-lg pl-8 pr-3 py-1.5 text-xs text-tg-text placeholder-tg-textMuted focus:outline-none focus:border-tg-accent transition-colors"
            />
          </div>

          {/* New Chat Button */}
          <div className="relative">
            <button
              onClick={() => setIsNewChatDropdownOpen(!isNewChatDropdownOpen)}
              className="p-1.5 rounded-lg bg-slate-800 hover:bg-tg-hover text-tg-textMuted hover:text-white border border-tg-border transition-colors"
              title="Начать новый диалог"
            >
              <MessageSquarePlus className="w-4 h-4" />
            </button>

            {isNewChatDropdownOpen && (
              <div className="absolute right-0 top-full mt-1.5 w-56 bg-tg-sidebar border border-tg-border rounded-xl shadow-2xl p-2 z-50 animate-in fade-in zoom-in-95">
                <div className="text-[11px] font-semibold text-tg-textMuted px-2 py-1 uppercase tracking-wider">
                  Начать диалог с ботом
                </div>
                {bots.length === 0 ? (
                  <p className="text-xs text-tg-textMuted p-2 text-center">Нет ботов. Создайте первого!</p>
                ) : (
                  <div className="max-h-48 overflow-y-auto space-y-1">
                    {bots.map((b) => (
                      <button
                        key={b.id}
                        onClick={() => {
                          onStartChatWithBot(b.id);
                          setIsNewChatDropdownOpen(false);
                        }}
                        className="w-full text-left px-2 py-1.5 rounded-lg hover:bg-tg-hover text-xs flex items-center gap-2 truncate"
                      >
                        <BotIcon className="w-3.5 h-3.5 text-tg-accent flex-shrink-0" />
                        <span className="truncate">{b.name} (@{b.username})</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* New Bot Button */}
          <button
            onClick={() => setIsBotModalOpen(true)}
            className="p-1.5 rounded-lg bg-tg-accent/20 hover:bg-tg-accent/30 text-tg-accent border border-tg-accent/40 transition-colors"
            title="Создать нового бота"
          >
            <Plus className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Chat List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {filteredChats.length === 0 ? (
          <div className="text-center py-12 px-4 text-tg-textMuted">
            <BotIcon className="w-10 h-10 mx-auto mb-2 opacity-30" />
            <p className="text-sm font-medium">Нет активных чатов</p>
            <p className="text-xs opacity-70 mt-1">
              Нажмите кнопку «+» сверху, чтобы создать бота и начать общение!
            </p>
          </div>
        ) : (
          filteredChats.map((chat) => (
            <ChatItem
              key={chat.id}
              chat={chat}
              isSelected={chat.id === selectedChatId}
              onSelect={() => onSelectChat(chat.id)}
            />
          ))
        )}
      </div>

      <NewBotModal
        isOpen={isBotModalOpen}
        onClose={() => setIsBotModalOpen(false)}
        onCreate={onCreateBot}
      />
    </aside>
  );
};
