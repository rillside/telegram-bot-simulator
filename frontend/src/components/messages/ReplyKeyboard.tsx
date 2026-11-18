import React from 'react';
import { ReplyKeyboardMarkup } from '../../types';

interface Props {
  markup: ReplyKeyboardMarkup;
  onButtonClick: (text: string) => void;
}

export const ReplyKeyboard: React.FC<Props> = ({ markup, onButtonClick }) => {
  if (!markup || !markup.keyboard || markup.keyboard.length === 0) {
    return null;
  }

  return (
    <div className="p-2 bg-slate-900 border-t border-tg-border space-y-1.5 animate-in slide-in-from-bottom-2">
      {markup.keyboard.map((row, rIdx) => (
        <div key={rIdx} className="flex gap-1.5">
          {row.map((btn, bIdx) => {
            const text = typeof btn === 'string' ? btn : btn.text;
            return (
              <button
                key={bIdx}
                onClick={() => onButtonClick(text)}
                className="flex-1 min-w-0 bg-slate-800 hover:bg-slate-700 active:bg-slate-600 border border-tg-border text-xs text-tg-text font-medium py-2 px-3 rounded-lg shadow-sm transition-all text-center truncate"
              >
                {text}
              </button>
            );
          })}
        </div>
      ))}
    </div>
  );
};
