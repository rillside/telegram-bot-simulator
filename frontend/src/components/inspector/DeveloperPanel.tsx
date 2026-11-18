import React, { useState } from 'react';
import { ConsoleTab } from '../console/ConsoleTab';
import { UpdatesInspectorTab } from './UpdatesInspectorTab';
import { ApiInspectorTab } from './ApiInspectorTab';
import { ProcessLogEntry, UpdateLog, ApiRequestLog } from '../../types';
import { Terminal, RefreshCw, Layers, ChevronDown, ChevronUp, X } from 'lucide-react';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  logs: ProcessLogEntry[];
  updates: UpdateLog[];
  apiRequests: ApiRequestLog[];
  onClearLogs: () => void;
  onClearUpdates: () => void;
  onClearApiRequests: () => void;
}

export const DeveloperPanel: React.FC<Props> = ({
  isOpen,
  onClose,
  logs,
  updates,
  apiRequests,
  onClearLogs,
  onClearUpdates,
  onClearApiRequests,
}) => {
  const [activeTab, setActiveTab] = useState<'console' | 'updates' | 'api'>('console');
  const [isExpanded, setIsExpanded] = useState(false);

  if (!isOpen) return null;

  return (
    <div
      className={`border-t border-tg-border bg-slate-950 flex flex-col transition-all duration-200 z-40 ${
        isExpanded ? 'h-[60vh]' : 'h-64'
      }`}
    >
      {/* Tab bar */}
      <div className="h-9 px-3 bg-tg-sidebar border-b border-tg-border flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-1">
          <button
            onClick={() => setActiveTab('console')}
            className={`flex items-center gap-1.5 px-3 py-1 rounded text-xs font-medium transition-colors ${
              activeTab === 'console'
                ? 'bg-slate-950 text-tg-accent shadow'
                : 'text-tg-textMuted hover:text-white'
            }`}
          >
            <Terminal className="w-3.5 h-3.5" />
            <span>Console</span>
            {logs.length > 0 && (
              <span className="text-[10px] px-1 rounded-full bg-slate-800 text-slate-400">
                {logs.length}
              </span>
            )}
          </button>

          <button
            onClick={() => setActiveTab('updates')}
            className={`flex items-center gap-1.5 px-3 py-1 rounded text-xs font-medium transition-colors ${
              activeTab === 'updates'
                ? 'bg-slate-950 text-tg-accent shadow'
                : 'text-tg-textMuted hover:text-white'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>Updates Inspector</span>
            {updates.length > 0 && (
              <span className="text-[10px] px-1 rounded-full bg-slate-800 text-slate-400">
                {updates.length}
              </span>
            )}
          </button>

          <button
            onClick={() => setActiveTab('api')}
            className={`flex items-center gap-1.5 px-3 py-1 rounded text-xs font-medium transition-colors ${
              activeTab === 'api'
                ? 'bg-slate-950 text-tg-accent shadow'
                : 'text-tg-textMuted hover:text-white'
            }`}
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>API Inspector</span>
            {apiRequests.length > 0 && (
              <span className="text-[10px] px-1 rounded-full bg-slate-800 text-slate-400">
                {apiRequests.length}
              </span>
            )}
          </button>
        </div>

        {/* Panel Controls */}
        <div className="flex items-center gap-1">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-1 rounded text-tg-textMuted hover:text-white transition-colors"
            title={isExpanded ? 'Уменьшить панель' : 'Развернуть панель'}
          >
            {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
          </button>
          <button
            onClick={onClose}
            className="p-1 rounded text-tg-textMuted hover:text-white transition-colors"
            title="Закрыть панель"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Tab content */}
      <div className="flex-1 overflow-hidden">
        {activeTab === 'console' && <ConsoleTab logs={logs} onClear={onClearLogs} />}
        {activeTab === 'updates' && <UpdatesInspectorTab updates={updates} onClear={onClearUpdates} />}
        {activeTab === 'api' && <ApiInspectorTab requests={apiRequests} onClear={onClearApiRequests} />}
      </div>
    </div>
  );
};
