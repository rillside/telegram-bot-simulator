import React, { useState } from 'react';
import { UpdateLog } from '../../types';
import { Trash2, ChevronRight, Eye } from 'lucide-react';

interface Props {
  updates: UpdateLog[];
  onClear: () => void;
}

export const UpdatesInspectorTab: React.FC<Props> = ({ updates, onClear }) => {
  const [selectedUpdate, setSelectedUpdate] = useState<UpdateLog | null>(null);

  const formatTime = (iso: string) => {
    return new Date(iso).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  return (
    <div className="flex-1 flex h-full bg-slate-950 font-mono text-xs overflow-hidden">
      {/* Table list */}
      <div className="w-1/2 border-r border-tg-border flex flex-col h-full">
        <div className="h-8 px-3 border-b border-tg-border bg-slate-900/80 flex items-center justify-between text-tg-textMuted text-[11px]">
          <span>События Update ({updates.length})</span>
          <button onClick={onClear} className="flex items-center gap-1 hover:text-white transition-colors">
            <Trash2 className="w-3.5 h-3.5" />
            <span>Очистить</span>
          </button>
        </div>

        <div className="flex-1 overflow-y-auto divide-y divide-slate-800">
          {updates.length === 0 ? (
            <p className="text-slate-600 p-4 italic">Нет событий. Отправьте сообщение или нажмите кнопку...</p>
          ) : (
            updates.map((u) => {
              const isSelected = selectedUpdate?.id === u.id;
              return (
                <div
                  key={u.id}
                  onClick={() => setSelectedUpdate(u)}
                  className={`px-3 py-2 cursor-pointer flex items-center justify-between transition-colors ${
                    isSelected ? 'bg-tg-active/20 text-sky-300' : 'hover:bg-slate-900 text-slate-300'
                  }`}
                >
                  <div className="flex items-center gap-2 truncate">
                    <span className="text-slate-500 font-bold">#{u.id}</span>
                    <span className="px-1.5 py-0.5 rounded text-[10px] bg-slate-800 text-tg-accent font-semibold uppercase">
                      {u.update_type}
                    </span>
                    <span className="text-slate-400 truncate">Bot:{u.bot_id}</span>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <span className="text-slate-500 text-[10px]">{formatTime(u.created_at)}</span>
                    <ChevronRight className="w-3.5 h-3.5 text-slate-600" />
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* JSON Viewer */}
      <div className="w-1/2 flex flex-col h-full bg-slate-900/40">
        <div className="h-8 px-3 border-b border-tg-border bg-slate-900/80 flex items-center justify-between text-tg-textMuted text-[11px]">
          <span className="flex items-center gap-1">
            <Eye className="w-3.5 h-3.5" />
            JSON структуры Update
          </span>
          {selectedUpdate && <span className="text-tg-accent">update_id: {selectedUpdate.id}</span>}
        </div>

        <div className="flex-1 overflow-y-auto p-3">
          {selectedUpdate ? (
            <pre className="text-emerald-300 text-[11px] whitespace-pre-wrap break-all select-text">
              {JSON.stringify(selectedUpdate.payload, null, 2)}
            </pre>
          ) : (
            <p className="text-slate-600 italic">Выберите Update из списка слева для просмотра полного JSON-объекта...</p>
          )}
        </div>
      </div>
    </div>
  );
};
