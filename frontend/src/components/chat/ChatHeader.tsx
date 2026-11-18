import React from 'react';
import { Bot, ProcessStatus } from '../../types';
import { Bot as BotIcon, Terminal, Info, Bug } from 'lucide-react';

interface Props {
  bot?: Bot;
  processStatus?: ProcessStatus;
  isDevPanelOpen: boolean;
  onToggleDevPanel: () => void;
  isBotDetailsOpen: boolean;
  onToggleBotDetails: () => void;
  debugMode: boolean;
  onToggleDebugMode: () => void;
}

export const ChatHeader: React.FC<Props> = ({
  bot,
  processStatus,
  isDevPanelOpen,
  onToggleDevPanel,
  isBotDetailsOpen,
  onToggleBotDetails,
  debugMode,
  onToggleDebugMode,
}) => {
  const status = processStatus?.status || (bot?.is_running ? 'RUNNING' : 'STOPPED');

  const getStatusColor = () => {
    switch (status) {
      case 'RUNNING':
        return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30';
      case 'STARTING':
      case 'STOPPING':
        return 'text-amber-400 bg-amber-500/10 border-amber-500/30';
      case 'ERROR':
        return 'text-rose-400 bg-rose-500/10 border-rose-500/30';
      default:
        return 'text-slate-400 bg-slate-500/10 border-slate-500/30';
    }
  };

  return (
    <div className="h-14 px-4 bg-tg-sidebar border-b border-tg-border flex items-center justify-between flex-shrink-0">
      {/* Bot Info */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-cyan-600 to-blue-500 flex items-center justify-center font-bold text-white shadow">
          {bot?.avatar ? (
            <img src={bot.avatar} alt="" className="w-full h-full rounded-full object-cover" />
          ) : (
            <BotIcon className="w-5 h-5" />
          )}
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h3 className="font-semibold text-sm text-tg-text">{bot?.name || 'Чат с ботом'}</h3>
            <span
              className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${getStatusColor()}`}
            >
              {status}
            </span>
          </div>
          <p className="text-xs text-tg-textMuted">
            {bot ? `@${bot.username}` : ''}
          </p>
        </div>
      </div>

      {/* Header Actions */}
      <div className="flex items-center gap-2">
        {/* Toggle Debug Mode */}
        <button
          onClick={onToggleDebugMode}
          className={`p-2 rounded-lg border text-xs flex items-center gap-1.5 transition-colors ${
            debugMode
              ? 'bg-purple-500/20 border-purple-500/50 text-purple-300'
              : 'border-tg-border text-tg-textMuted hover:text-white hover:bg-tg-hover'
          }`}
          title="Режим отладки (отображать ID сообщений)"
        >
          <Bug className="w-4 h-4" />
          <span className="hidden sm:inline">Debug</span>
        </button>

        {/* Toggle Developer Inspector Panel */}
        <button
          onClick={onToggleDevPanel}
          className={`p-2 rounded-lg border text-xs flex items-center gap-1.5 transition-colors ${
            isDevPanelOpen
              ? 'bg-tg-accent/20 border-tg-accent/50 text-tg-accent'
              : 'border-tg-border text-tg-textMuted hover:text-white hover:bg-tg-hover'
          }`}
          title="Открыть консоль и инспектор API"
        >
          <Terminal className="w-4 h-4" />
          <span className="hidden sm:inline">Инспектор</span>
        </button>

        {/* Toggle Bot Details */}
        <button
          onClick={onToggleBotDetails}
          className={`p-2 rounded-lg border text-xs flex items-center gap-1.5 transition-colors ${
            isBotDetailsOpen
              ? 'bg-blue-500/20 border-blue-500/50 text-blue-300'
              : 'border-tg-border text-tg-textMuted hover:text-white hover:bg-tg-hover'
          }`}
          title="Информация о боте и процесс"
        >
          <Info className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
