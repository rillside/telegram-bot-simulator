import React, { useState } from 'react';
import { ApiRequestLog } from '../../types';
import { Trash2, ChevronRight } from 'lucide-react';

interface Props {
  requests: ApiRequestLog[];
  onClear: () => void;
}

export const ApiInspectorTab: React.FC<Props> = ({ requests, onClear }) => {
  const [selectedReq, setSelectedReq] = useState<ApiRequestLog | null>(null);

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
          <span>HTTP API Requests ({requests.length})</span>
          <button onClick={onClear} className="flex items-center gap-1 hover:text-white transition-colors">
            <Trash2 className="w-3.5 h-3.5" />
            <span>Очистить</span>
          </button>
        </div>

        <div className="flex-1 overflow-y-auto divide-y divide-slate-800">
          {requests.length === 0 ? (
            <p className="text-slate-600 p-4 italic">Нет запросов. Запустите бота для фиксации вызовов API...</p>
          ) : (
            requests.map((r) => {
              const isSelected = selectedReq?.id === r.id;
              const isOk = r.response_status === 200;

              return (
                <div
                  key={r.id}
                  onClick={() => setSelectedReq(r)}
                  className={`px-3 py-2 cursor-pointer flex items-center justify-between transition-colors ${
                    isSelected ? 'bg-tg-active/20 text-sky-300' : 'hover:bg-slate-900 text-slate-300'
                  }`}
                >
                  <div className="flex items-center gap-2 truncate">
                    <span
                      className={`px-1 py-0.5 rounded text-[10px] font-bold ${
                        r.method === 'POST' ? 'bg-blue-500/20 text-blue-400' : 'bg-green-500/20 text-green-400'
                      }`}
                    >
                      {r.method}
                    </span>
                    <span className="font-semibold truncate">/{r.endpoint}</span>
                    <span
                      className={`text-[10px] font-bold px-1.5 py-0.2 rounded ${
                        isOk ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'
                      }`}
                    >
                      {r.response_status}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <span className="text-slate-500 text-[10px]">{r.execution_time_ms} ms</span>
                    <ChevronRight className="w-3.5 h-3.5 text-slate-600" />
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Request & Response Inspector */}
      <div className="w-1/2 flex flex-col h-full bg-slate-900/40 overflow-y-auto p-3 space-y-3">
        {selectedReq ? (
          <>
            <div className="flex items-center justify-between border-b border-tg-border pb-2">
              <div>
                <span className="text-tg-accent font-bold text-sm">/{selectedReq.endpoint}</span>
                <p className="text-[10px] text-slate-500">Время: {formatTime(selectedReq.created_at)} | Длительность: {selectedReq.execution_time_ms} ms</p>
              </div>
              <span
                className={`text-xs font-bold px-2 py-0.5 rounded ${
                  selectedReq.response_status === 200
                    ? 'bg-emerald-500/20 text-emerald-400'
                    : 'bg-rose-500/20 text-rose-400'
                }`}
              >
                Status: {selectedReq.response_status}
              </span>
            </div>

            <div>
              <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1">Параметры запроса:</p>
              <pre className="p-2.5 rounded-lg bg-slate-950 border border-tg-border text-sky-300 text-[11px] whitespace-pre-wrap break-all select-text">
                {JSON.stringify(selectedReq.params || {}, null, 2)}
              </pre>
            </div>

            <div>
              <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1">Ответ сервера (JSON):</p>
              <pre className="p-2.5 rounded-lg bg-slate-950 border border-tg-border text-emerald-300 text-[11px] whitespace-pre-wrap break-all select-text">
                {JSON.stringify(selectedReq.response_body || {}, null, 2)}
              </pre>
            </div>
          </>
        ) : (
          <p className="text-slate-600 italic">Выберите запрос из списка слева для инспекции параметров и ответа...</p>
        )}
      </div>
    </div>
  );
};
