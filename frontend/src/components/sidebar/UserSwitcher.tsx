import React, { useState } from 'react';
import { User } from '../../types';
import { Plus, Check } from 'lucide-react';

interface Props {
  users: User[];
  activeUser: User | null;
  onSelectUser: (user: User) => void;
  onCreateUser: (name: string, username: string) => Promise<void>;
}

export const UserSwitcher: React.FC<Props> = ({ users, activeUser, onSelectUser, onCreateUser }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [newName, setNewName] = useState('');
  const [newUsername, setNewUsername] = useState('');

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName.trim()) return;
    await onCreateUser(newName.trim(), newUsername.trim());
    setNewName('');
    setNewUsername('');
    setIsCreating(false);
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-2.5 py-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 border border-tg-border text-xs text-tg-text transition-colors"
      >
        <div className="w-5 h-5 rounded-full bg-emerald-600 flex items-center justify-center font-bold text-white text-[10px]">
          {activeUser?.first_name[0] || 'U'}
        </div>
        <span className="font-medium truncate max-w-[100px]">
          {activeUser ? `${activeUser.first_name} ${activeUser.last_name || ''}`.trim() : 'Пользователь'}
        </span>
        <span className="text-[10px] text-tg-accent">ID:{activeUser?.id}</span>
      </button>

      {isOpen && (
        <div className="absolute top-full left-0 mt-2 w-64 bg-tg-sidebar border border-tg-border rounded-xl shadow-2xl p-2 z-50 animate-in fade-in zoom-in-95">
          <div className="px-2 py-1.5 text-[11px] font-semibold text-tg-textMuted uppercase tracking-wider">
            Виртуальный пользователь
          </div>

          <div className="max-h-48 overflow-y-auto space-y-1 mb-2">
            {users.map((u) => (
              <div
                key={u.id}
                onClick={() => {
                  onSelectUser(u);
                  setIsOpen(false);
                }}
                className={`flex items-center justify-between px-2.5 py-1.5 rounded-lg cursor-pointer text-xs transition-colors ${
                  activeUser?.id === u.id ? 'bg-tg-active text-white' : 'hover:bg-tg-hover text-tg-text'
                }`}
              >
                <div className="flex items-center gap-2 truncate">
                  <div className="w-6 h-6 rounded-full bg-emerald-600 flex items-center justify-center font-bold text-white text-xs">
                    {u.first_name[0]}
                  </div>
                  <div className="truncate">
                    <p className="font-medium truncate">{u.first_name} {u.last_name}</p>
                    <p className="text-[10px] opacity-70">ID: {u.id} {u.username ? `@${u.username}` : ''}</p>
                  </div>
                </div>
                {activeUser?.id === u.id && <Check className="w-4 h-4 flex-shrink-0" />}
              </div>
            ))}
          </div>

          {isCreating ? (
            <form onSubmit={handleCreate} className="p-2 bg-slate-900 rounded-lg space-y-2 border border-tg-border">
              <input
                type="text"
                placeholder="Имя ученика"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                className="w-full bg-slate-800 border border-tg-border rounded px-2 py-1 text-xs text-tg-text focus:outline-none focus:border-tg-accent"
                required
              />
              <input
                type="text"
                placeholder="Username (опц.)"
                value={newUsername}
                onChange={(e) => setNewUsername(e.target.value)}
                className="w-full bg-slate-800 border border-tg-border rounded px-2 py-1 text-xs text-tg-text focus:outline-none focus:border-tg-accent"
              />
              <div className="flex justify-end gap-1.5">
                <button
                  type="button"
                  onClick={() => setIsCreating(false)}
                  className="px-2 py-1 text-[11px] text-tg-textMuted hover:text-white"
                >
                  Отмена
                </button>
                <button
                  type="submit"
                  className="px-2 py-1 text-[11px] bg-tg-accent text-slate-900 font-semibold rounded hover:bg-sky-400"
                >
                  Добавить
                </button>
              </div>
            </form>
          ) : (
            <button
              onClick={() => setIsCreating(true)}
              className="w-full flex items-center justify-center gap-1.5 px-3 py-1.5 text-xs text-tg-accent hover:bg-tg-hover rounded-lg transition-colors font-medium border border-dashed border-tg-border"
            >
              <Plus className="w-3.5 h-3.5" />
              Добавить ученика
            </button>
          )}
        </div>
      )}
    </div>
  );
};
