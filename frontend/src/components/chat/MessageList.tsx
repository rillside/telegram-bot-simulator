import React, { useEffect, useRef } from 'react';
import { Message } from '../../types';
import { MessageBubble } from '../messages/MessageBubble';
import { Bot } from 'lucide-react';

interface Props {
  messages: Message[];
  chatId: number;
  onInlineClick: (messageId: number, callbackData: string) => Promise<void>;
  debugMode?: boolean;
}

export const MessageList: React.FC<Props> = ({ messages, chatId, onInlineClick, debugMode }) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto p-4 flex flex-col">
      {messages.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center text-tg-textMuted select-none">
          <div className="w-16 h-16 rounded-full bg-slate-800/80 border border-tg-border flex items-center justify-center mb-3">
            <Bot className="w-8 h-8 opacity-40 text-tg-accent" />
          </div>
          <p className="text-sm font-semibold text-tg-text">Диалог пуст</p>
          <p className="text-xs text-tg-textMuted max-w-xs text-center mt-1">
            Отправьте команду <span className="text-tg-accent font-mono font-bold">/start</span> или текстовое сообщение, чтобы начать взаимодействие с ботом.
          </p>
        </div>
      ) : (
        <div className="space-y-1">
          {messages.map((msg) => (
            <MessageBubble
              key={msg.id}
              message={msg}
              chatId={chatId}
              onInlineClick={onInlineClick}
              debugMode={debugMode}
            />
          ))}
          <div ref={bottomRef} />
        </div>
      )}
    </div>
  );
};
