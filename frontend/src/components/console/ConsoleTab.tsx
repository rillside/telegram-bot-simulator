import React, { useEffect, useRef } from 'react';
import { ProcessLogEntry } from '../../types';
import { Trash2 } from 'lucide-react';

interface Props {
  logs: ProcessLogEntry[];
  onClear: () => void;
}

export const ConsoleTab: React.FC<Props> = ({ logs, onClear }) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const formatTime = (ts: number) => {
    return new Date(ts * 1000).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-slate-950 font-mono text-xs overflow-hidden relative">
      {/* Action bar */}
      <div className="h-8 px-3 border-b border-tg-border bg-slate-900/80 flex items-center justify-between text-tg-textMuted text-[11px]">
        <span>stdout / stderr / tracebacks</span>
        <button
          onClick={onClear}
          className="flex items-center gap-1 hover:text-white transition-colors"
          title="Очистить консоль"
        >
          <Trash2 className="w-3.5 h-3.5" />
          <span>Очистить</span>
        </button>
      </div>

      {/* Log Output */}
      <div className="flex-1 overflow-y-auto p-3 space-y-1 select-text">
        {logs.length === 0 ? (
          <p className="text-slate-600 italic">Консоль пуста. Запустите бота, чтобы увидеть вывод программы...</p>
        ) : (
          logs.map((log, index) => {
            let textColor = 'text-slate-300';
            let prefix = 'STDOUT';

            if (log.stream === 'stderr') {
              textColor = 'text-rose-400';
              prefix = 'STDERR';
            } else if (log.stream === 'system') {
              textColor = 'text-amber-300';
              prefix = 'SYSTEM';
            }

            return (
              <div key={index} className="flex items-start gap-2 leading-relaxed">
                <span className="text-slate-600 flex-shrink-0 select-none">[{formatTime(log.timestamp)}]</span>
                <span
                  className={`text-[10px] font-bold px-1 rounded flex-shrink-0 select-none ${
                    log.stream === 'stderr'
                      ? 'bg-rose-500/20 text-rose-300'
                      : log.stream === 'system'
                      ? 'bg-amber-500/20 text-amber-300'
                      : 'bg-slate-800 text-slate-400'
                  }`}
                >
                  {prefix}
                </span>
                <span className={`break-all whitespace-pre-wrap ${textColor}`}>{log.text}</span>
              </div>
            );
          })
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
};
