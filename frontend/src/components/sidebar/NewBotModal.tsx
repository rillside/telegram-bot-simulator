import React, { useState } from 'react';
import { X, Bot } from 'lucide-react';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onCreate: (data: { name: string; username: string; description?: string }) => Promise<void>;
}

export const NewBotModal: React.FC<Props> = ({ isOpen, onClose, onCreate }) => {
  const [name, setName] = useState('');
  const [username, setUsername] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !username.trim()) {
      setError('Имя и username обязательны');
      return;
    }
    setError('');
    setLoading(true);
    try {
      await onCreate({
        name: name.trim(),
        username: username.trim().replace(/^@/, ''),
        description: description.trim(),
      });
      setName('');
      setUsername('');
      setDescription('');
      onClose();
    } catch (err: any) {
      setError(err.message || 'Ошибка создания бота');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-tg-sidebar border border-tg-border rounded-xl w-full max-w-md shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        <div className="flex items-center justify-between px-5 py-4 border-b border-tg-border">
          <div className="flex items-center gap-2">
            <Bot className="w-5 h-5 text-tg-accent" />
            <h3 className="font-semibold text-tg-text">Создать виртуального бота</h3>
          </div>
          <button onClick={onClose} className="text-tg-textMuted hover:text-white transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-5 space-y-4">
          {error && <div className="p-3 text-xs bg-red-500/20 border border-red-500/50 rounded text-red-200">{error}</div>}

          <div>
            <label className="block text-xs font-medium text-tg-textMuted mb-1">Имя бота</label>
            <input
              type="text"
              placeholder="Например: Мой первый бот"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full bg-slate-900 border border-tg-border rounded-lg px-3 py-2 text-sm text-tg-text focus:outline-none focus:border-tg-accent"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-tg-textMuted mb-1">Username бота</label>
            <div className="relative">
              <span className="absolute left-3 top-2 text-tg-textMuted text-sm">@</span>
              <input
                type="text"
                placeholder="my_super_bot"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full bg-slate-900 border border-tg-border rounded-lg pl-8 pr-3 py-2 text-sm text-tg-text focus:outline-none focus:border-tg-accent"
                required
              />
            </div>
            <p className="text-[11px] text-tg-textMuted mt-1">Должен заканчиваться на bot (например: test_bot)</p>
          </div>

          <div>
            <label className="block text-xs font-medium text-tg-textMuted mb-1">Описание (опционально)</label>
            <textarea
              placeholder="Учебный бот для курса по Python..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={2}
              className="w-full bg-slate-900 border border-tg-border rounded-lg px-3 py-2 text-sm text-tg-text focus:outline-none focus:border-tg-accent resize-none"
            />
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm rounded-lg text-tg-textMuted hover:text-white hover:bg-tg-hover transition-colors"
            >
              Отмена
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 text-sm rounded-lg bg-tg-accent text-slate-900 font-semibold hover:bg-sky-400 transition-colors disabled:opacity-50"
            >
              {loading ? 'Создание...' : 'Создать бота'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
