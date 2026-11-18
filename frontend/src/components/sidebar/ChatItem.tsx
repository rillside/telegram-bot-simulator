import React from 'react';
import { Chat } from '../../types';
import { Bot as BotIcon } from 'lucide-react';

interface Props {
  chat: Chat;
  isSelected: boolean;
  onSelect: () => void;
}

export const ChatItem: React.FC<Props> = ({ chat, isSelected, onSelect }) => {
  const formatTime = (ts?: number) => {
    if (!ts) return '';
    const date = new Date(ts * 1000);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const isBotRunning = chat.bot?.is_running;

  return (
    <div
      onClick={onSelect}
      className={`flex items-center gap-3 px-3 py-2.5 rounded-lg cursor-pointer transition-colors ${
        isSelected ? 'bg-tg-active text-white' : 'hover:bg-tg-hover text-tg-text'
      }`}
    >
      {/* Avatar */}
      <div className="relative flex-shrink-0">
        <div className="w-12 h-12 rounded-full bg-gradient-to-tr from-cyan-600 to-blue-500 flex items-center justify-center font-bold text-white shadow">
          {chat.bot?.avatar ? (
            <img src={chat.bot.avatar} alt="" className="w-full h-full rounded-full object-cover" />
          ) : (
            <BotIcon className="w-6 h-6" />
          )}
        </div>
        {/* Running status badge */}
        <span
          className={`absolute bottom-0 right-0 w-3.5 h-3.5 rounded-full border-2 border-tg-sidebar ${
            isBotRunning ? 'bg-emerald-500' : 'bg-slate-500'
          }`}
          title={isBotRunning ? 'Бот работает' : 'Бот остановлен'}
        />
      </div>

      {/* Info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between mb-0.5">
          <h4 className="font-semibold text-sm truncate">{chat.bot?.name || chat.title || 'Чат'}</h4>
          <span className={`text-xs ${isSelected ? 'text-blue-100' : 'text-tg-textMuted'}`}>
            {formatTime(chat.last_message?.date)}
          </span>
        </div>
        <div className="flex items-center justify-between">
          <p className={`text-xs truncate ${isSelected ? 'text-blue-100' : 'text-tg-textMuted'}`}>
            {chat.last_message?.text ? (
              <span>
                {chat.last_message.is_from_bot ? '' : 'Вы: '}
                {chat.last_message.text}
              </span>
            ) : (
              <span className="italic opacity-60">Нет сообщений</span>
            )}
          </p>
          {chat.unread_count && chat.unread_count > 0 ? (
            <span className="ml-2 bg-tg-accent text-slate-900 text-[10px] font-bold px-1.5 py-0.5 rounded-full">
              {chat.unread_count}
            </span>
          ) : null}
        </div>
      </div>
    </div>
  );
};
