import React, { useState } from 'react';
import { InlineKeyboardMarkup, InlineKeyboardButton } from '../../types';

interface Props {
  markup: InlineKeyboardMarkup;
  chatId: number;
  messageId: number;
  onButtonClick: (messageId: number, callbackData: string) => Promise<void>;
}

export const InlineKeyboard: React.FC<Props> = ({ markup, messageId, onButtonClick }) => {
  const [loadingBtn, setLoadingBtn] = useState<string | null>(null);

  if (!markup || !markup.inline_keyboard || markup.inline_keyboard.length === 0) {
    return null;
  }

  const handleClick = async (btn: InlineKeyboardButton) => {
    if (btn.url) {
      window.open(btn.url, '_blank');
      return;
    }
    if (btn.callback_data !== undefined) {
      setLoadingBtn(btn.callback_data);
      try {
        await onButtonClick(messageId, btn.callback_data);
      } finally {
        setLoadingBtn(null);
      }
    }
  };

  return (
    <div className="mt-2 space-y-1 w-full">
      {markup.inline_keyboard.map((row, rowIndex) => (
        <div key={rowIndex} className="flex gap-1.5 w-full">
          {row.map((btn, btnIndex) => {
            const isLoading = loadingBtn === btn.callback_data;
            return (
              <button
                key={btnIndex}
                onClick={() => handleClick(btn)}
                disabled={isLoading}
                className="flex-1 min-w-0 bg-slate-800/90 hover:bg-slate-700 active:bg-slate-600 text-tg-accent hover:text-sky-300 font-medium text-xs px-3 py-2 rounded-lg border border-slate-700/60 shadow-sm transition-all text-center truncate disabled:opacity-50"
              >
                {isLoading ? '⏳...' : btn.text}
              </button>
            );
          })}
        </div>
      ))}
    </div>
  );
};
