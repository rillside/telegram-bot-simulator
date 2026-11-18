import React from 'react';
import { Message } from '../../types';
import { InlineKeyboard } from './InlineKeyboard';
import { CheckCheck, FileText } from 'lucide-react';

interface Props {
  message: Message;
  chatId: number;
  onInlineClick: (messageId: number, callbackData: string) => Promise<void>;
  debugMode?: boolean;
}

export const MessageBubble: React.FC<Props> = ({ message, chatId, onInlineClick, debugMode = false }) => {
  const isOutgoing = !message.is_from_bot;

  const formatTime = (ts: number) => {
    return new Date(ts * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const hasInlineMarkup =
    message.reply_markup &&
    typeof message.reply_markup === 'object' &&
    'inline_keyboard' in message.reply_markup;

  return (
    <div className={`flex flex-col mb-3 ${isOutgoing ? 'items-end' : 'items-start'}`}>
      <div
        className={`max-w-[75%] rounded-2xl px-4 py-2.5 shadow relative ${
          isOutgoing
            ? 'bg-tg-bubbleOut text-white rounded-br-none'
            : 'bg-tg-bubbleIn text-tg-text border border-slate-700/50 rounded-bl-none'
        }`}
      >
        {/* Debug info */}
        {debugMode && (
          <div className="text-[10px] opacity-60 font-mono mb-1 border-b border-white/10 pb-0.5">
            msg_id: {message.id} | date: {message.date}
          </div>
        )}

        {/* Media: Photo */}
        {message.media_type === 'photo' && message.media_url && (
          <div className="mb-2 rounded-lg overflow-hidden border border-black/20 max-h-80 bg-black/20">
            <img src={message.media_url} alt="Photo" className="w-full h-full object-contain" />
          </div>
        )}

        {/* Media: Document */}
        {message.media_type === 'document' && (
          <div className="mb-2 flex items-center gap-2.5 p-2 rounded-lg bg-black/20 border border-white/10">
            <div className="p-2 rounded bg-tg-accent/20 text-tg-accent">
              <FileText className="w-5 h-5" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium truncate">{message.file_name || 'document'}</p>
              {message.media_url && (
                <a
                  href={message.media_url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-[11px] text-tg-accent hover:underline"
                >
                  Скачать
                </a>
              )}
            </div>
          </div>
        )}

        {/* Message Text */}
        {message.text && (
          <p className="text-sm whitespace-pre-wrap break-words leading-relaxed select-text">
            {message.text}
          </p>
        )}

        {/* Timestamp & Status */}
        <div className="flex items-center justify-end gap-1 mt-1 text-[10px] opacity-70">
          <span>{formatTime(message.date)}</span>
          {isOutgoing && <CheckCheck className="w-3.5 h-3.5 text-blue-200" />}
        </div>
      </div>

      {/* Inline Keyboard */}
      {hasInlineMarkup && (
        <div className="max-w-[75%] w-full">
          <InlineKeyboard
            markup={message.reply_markup}
            chatId={chatId}
            messageId={message.id}
            onButtonClick={onInlineClick}
          />
        </div>
      )}
    </div>
  );
};
