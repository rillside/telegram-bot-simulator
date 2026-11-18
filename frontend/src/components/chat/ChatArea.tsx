import React from 'react';
import { Chat, Message, ProcessStatus, ReplyKeyboardMarkup } from '../../types';
import { ChatHeader } from './ChatHeader';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { MessageSquare } from 'lucide-react';

interface Props {
  chat: Chat | null;
  messages: Message[];
  processStatus?: ProcessStatus;
  isDevPanelOpen: boolean;
  onToggleDevPanel: () => void;
  isBotDetailsOpen: boolean;
  onToggleBotDetails: () => void;
  debugMode: boolean;
  onToggleDebugMode: () => void;
  onSendMessage: (text: string) => void;
  onInlineClick: (messageId: number, callbackData: string) => Promise<void>;
}

export const ChatArea: React.FC<Props> = ({
  chat,
  messages,
  processStatus,
  isDevPanelOpen,
  onToggleDevPanel,
  isBotDetailsOpen,
  onToggleBotDetails,
  debugMode,
  onToggleDebugMode,
  onSendMessage,
  onInlineClick,
}) => {
  if (!chat) {
    return (
      <div className="flex-1 h-full flex flex-col items-center justify-center text-tg-textMuted bg-tg-bg select-none p-6">
        <div className="w-20 h-20 rounded-2xl bg-slate-800/60 border border-tg-border flex items-center justify-center mb-4 text-tg-accent/50 shadow">
          <MessageSquare className="w-10 h-10" />
        </div>
        <h2 className="text-lg font-bold text-tg-text mb-1">Telegram Simulator</h2>
        <p className="text-sm text-tg-textMuted max-w-sm text-center">
          Выберите чат слева или создайте нового виртуального бота, чтобы начать тестирование.
        </p>
      </div>
    );
  }

  // Find the latest active ReplyKeyboardMarkup in messages
  let activeReplyMarkup: ReplyKeyboardMarkup | null = null;
  for (let i = messages.length - 1; i >= 0; i--) {
    const m = messages[i];
    if (m.is_from_bot && m.reply_markup) {
      if ('keyboard' in m.reply_markup) {
        activeReplyMarkup = m.reply_markup;
        break;
      } else if ('remove_keyboard' in m.reply_markup && m.reply_markup.remove_keyboard) {
        activeReplyMarkup = null;
        break;
      }
    }
  }

  return (
    <div className="flex-1 h-full flex flex-col bg-tg-bg relative overflow-hidden">
      {/* Header */}
      <ChatHeader
        bot={chat.bot}
        processStatus={processStatus}
        isDevPanelOpen={isDevPanelOpen}
        onToggleDevPanel={onToggleDevPanel}
        isBotDetailsOpen={isBotDetailsOpen}
        onToggleBotDetails={onToggleBotDetails}
        debugMode={debugMode}
        onToggleDebugMode={onToggleDebugMode}
      />

      {/* Messages */}
      <MessageList
        messages={messages}
        chatId={chat.id}
        onInlineClick={onInlineClick}
        debugMode={debugMode}
      />

      {/* Input */}
      <MessageInput
        onSendMessage={onSendMessage}
        replyMarkup={activeReplyMarkup}
      />
    </div>
  );
};
