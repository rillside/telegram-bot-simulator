import React, { useState } from 'react';
import { Bot, ProcessStatus } from '../../types';
import { X, Copy, Check, Eye, EyeOff, Play, Square, RotateCcw, Bot as BotIcon, Cpu, FileCode } from 'lucide-react';

interface Props {
  bot?: Bot;
  processStatus?: ProcessStatus;
  isOpen: boolean;
  onClose: () => void;
  onStartProcess: (botId: number, filePath: string) => Promise<void>;
  onStopProcess: (botId: number) => Promise<void>;
  onRestartProcess: (botId: number) => Promise<void>;
}

export const BotDetailsPanel: React.FC<Props> = ({
  bot,
  processStatus,
  isOpen,
  onClose,
  onStartProcess,
  onStopProcess,
  onRestartProcess,
}) => {
  const [showToken, setShowToken] = useState(false);
  const [copiedToken, setCopiedToken] = useState(false);
  const [filePath, setFilePath] = useState(processStatus?.file_path || 'examples/telebot/echo_bot.py');
  const [loading, setLoading] = useState(false);

  if (!isOpen || !bot) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(bot.token);
    setCopiedToken(true);
    setTimeout(() => setCopiedToken(false), 2000);
  };

  const handleStart = async () => {
    if (!filePath.trim()) return;
    setLoading(true);
    try {
      await onStartProcess(bot.id, filePath.trim());
    } finally {
      setLoading(false);
    }
  };

  const handleStop = async () => {
    setLoading(true);
    try {
      await onStopProcess(bot.id);
    } finally {
      setLoading(false);
    }
  };

  const handleRestart = async () => {
    setLoading(true);
    try {
      await onRestartProcess(bot.id);
    } finally {
      setLoading(false);
    }
  };

  const isRunning = processStatus?.status === 'RUNNING';

  return (
    <aside className="w-80 h-full bg-tg-sidebar border-l border-tg-border flex flex-col flex-shrink-0 animate-in slide-in-from-right duration-200">
      {/* Header */}
      <div className="h-14 px-4 border-b border-tg-border flex items-center justify-between">
        <h3 className="font-semibold text-sm text-tg-text">Информация о боте</h3>
        <button onClick={onClose} className="text-tg-textMuted hover:text-white transition-colors">
          <X className="w-5 h-5" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-5">
        {/* Profile Card */}
        <div className="flex flex-col items-center text-center p-4 bg-slate-900 rounded-xl border border-tg-border">
          <div className="w-16 h-16 rounded-full bg-gradient-to-tr from-cyan-600 to-blue-500 flex items-center justify-center font-bold text-white text-xl shadow mb-2">
            {bot.avatar ? (
              <img src={bot.avatar} alt="" className="w-full h-full rounded-full object-cover" />
            ) : (
              <BotIcon className="w-8 h-8" />
            )}
          </div>
          <h4 className="font-bold text-base text-tg-text">{bot.name}</h4>
          <p className="text-xs text-tg-accent">@{bot.username}</p>
          <p className="text-[11px] text-tg-textMuted mt-1">Bot ID: {bot.id}</p>
          {bot.description && (
            <p className="text-xs text-tg-textMuted mt-2 italic px-2">{bot.description}</p>
          )}
        </div>

        {/* Token Card */}
        <div className="p-3.5 bg-slate-900 rounded-xl border border-tg-border space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-tg-textMuted uppercase tracking-wider">
              Локальный Bot API Token
            </span>
            <div className="flex items-center gap-1">
              <button
                onClick={() => setShowToken(!showToken)}
                className="p-1 rounded text-tg-textMuted hover:text-white transition-colors"
                title={showToken ? 'Скрыть токен' : 'Показать токен'}
              >
                {showToken ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
              </button>
              <button
                onClick={handleCopy}
                className="p-1 rounded text-tg-textMuted hover:text-white transition-colors"
                title="Копировать токен"
              >
                {copiedToken ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              </button>
            </div>
          </div>
          <div className="font-mono text-xs p-2 bg-slate-950 rounded border border-tg-border break-all select-all text-emerald-400">
            {showToken ? bot.token : `${bot.id}:••••••••••••••••••••••••••••••••••••`}
          </div>
          <p className="text-[11px] text-tg-textMuted leading-tight">
            Используйте этот токен в <code className="text-tg-accent">TeleBot(TOKEN)</code> или <code className="text-tg-accent">Bot(token=TOKEN)</code>.
          </p>
        </div>

        {/* Process Manager Section */}
        <div className="p-3.5 bg-slate-900 rounded-xl border border-tg-border space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5">
              <Cpu className="w-4 h-4 text-tg-accent" />
              <span className="text-xs font-semibold text-tg-text">Process Manager</span>
            </div>
            <span
              className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                isRunning
                  ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                  : 'bg-slate-800 text-slate-400 border-slate-700'
              }`}
            >
              {processStatus?.status || (bot.is_running ? 'RUNNING' : 'STOPPED')}
            </span>
          </div>

          <div>
            <label className="block text-[11px] font-medium text-tg-textMuted mb-1 flex items-center gap-1">
              <FileCode className="w-3.5 h-3.5" />
              Путь к Python-файлу бота
            </label>
            <input
              type="text"
              value={filePath}
              onChange={(e) => setFilePath(e.target.value)}
              disabled={isRunning}
              placeholder="examples/telebot/echo_bot.py"
              className="w-full bg-slate-950 border border-tg-border rounded-lg px-2.5 py-1.5 text-xs text-tg-text font-mono focus:outline-none focus:border-tg-accent disabled:opacity-60"
            />
          </div>

          {/* Controls */}
          <div className="flex gap-2 pt-1">
            {!isRunning ? (
              <button
                onClick={handleStart}
                disabled={loading}
                className="flex-1 flex items-center justify-center gap-1.5 py-2 px-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold shadow transition-colors disabled:opacity-50"
              >
                <Play className="w-3.5 h-3.5 fill-current" />
                Запустить бота
              </button>
            ) : (
              <>
                <button
                  onClick={handleStop}
                  disabled={loading}
                  className="flex-1 flex items-center justify-center gap-1.5 py-2 px-3 bg-rose-600 hover:bg-rose-500 text-white rounded-lg text-xs font-semibold shadow transition-colors disabled:opacity-50"
                >
                  <Square className="w-3.5 h-3.5 fill-current" />
                  Остановить
                </button>
                <button
                  onClick={handleRestart}
                  disabled={loading}
                  className="p-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-xs border border-tg-border transition-colors"
                  title="Перезапустить"
                >
                  <RotateCcw className="w-4 h-4" />
                </button>
              </>
            )}
          </div>

          {/* Process Metrics */}
          {processStatus?.pid && (
            <div className="text-[11px] text-tg-textMuted space-y-0.5 pt-1 border-t border-tg-border/50">
              <p>PID: <span className="font-mono text-tg-text">{processStatus.pid}</span></p>
              {processStatus.exit_code !== null && processStatus.exit_code !== undefined && (
                <p>Код завершения: <span className="font-mono text-tg-text">{processStatus.exit_code}</span></p>
              )}
            </div>
          )}
        </div>
      </div>
    </aside>
  );
};
