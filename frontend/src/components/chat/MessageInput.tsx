import React, { useState } from 'react';
import { Send } from 'lucide-react';
import { ReplyKeyboard } from '../messages/ReplyKeyboard';
import { ReplyKeyboardMarkup } from '../../types';

interface Props {
  onSendMessage: (text: string) => void;
  replyMarkup?: ReplyKeyboardMarkup | null;
  placeholder?: string;
  disabled?: boolean;
}

export const MessageInput: React.FC<Props> = ({
  onSendMessage,
  replyMarkup,
  placeholder = 'Написать сообщение...',
  disabled = false,
}) => {
  const [text, setText] = useState('');

  const handleSend = () => {
    if (!text.trim() || disabled) return;
    onSendMessage(text.trim());
    setText('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const customPlaceholder =
    replyMarkup && replyMarkup.input_field_placeholder
      ? replyMarkup.input_field_placeholder
      : placeholder;

  return (
    <div className="bg-tg-sidebar border-t border-tg-border flex flex-col flex-shrink-0">
      {/* Reply Keyboard if active */}
      {replyMarkup && (
        <ReplyKeyboard
          markup={replyMarkup}
          onButtonClick={(btnText) => onSendMessage(btnText)}
        />
      )}

      {/* Input row */}
      <div className="p-3 flex items-end gap-2">
        <textarea
          rows={1}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={customPlaceholder}
          disabled={disabled}
          className="flex-1 max-h-32 min-h-[42px] bg-slate-900 border border-tg-border rounded-xl px-4 py-2.5 text-sm text-tg-text placeholder-tg-textMuted focus:outline-none focus:border-tg-accent resize-none transition-colors"
        />

        <button
          onClick={handleSend}
          disabled={!text.trim() || disabled}
          className="w-11 h-11 rounded-xl bg-tg-accent hover:bg-sky-400 active:bg-sky-500 text-slate-900 flex items-center justify-center transition-all disabled:opacity-40 disabled:hover:bg-tg-accent shadow"
          title="Отправить (Enter)"
        >
          <Send className="w-5 h-5 ml-0.5" />
        </button>
      </div>
    </div>
  );
};
