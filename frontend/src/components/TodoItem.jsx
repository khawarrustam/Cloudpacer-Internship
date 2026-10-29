import React from 'react';
import { Check, Loader2, Trash2 } from 'lucide-react';

export default function TodoItem({ todo, onComplete, onDelete, isCompleting, isDeleting }) {
  // English: This presentation component receives data and sends user events to its parent.
  // Roman Urdu: Ye presentation component data props se leta aur events parent ko deta hai.
  const priority = String(todo.priority || 'medium').toLowerCase();

  return (
    <article className="flex items-center gap-3 border-b border-[var(--border)] px-4 py-4 last:border-b-0">
      <button
        type="button"
        onClick={() => onComplete(todo.id)}
        disabled={todo.is_completed || isCompleting}
        className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full border border-stone-300 text-green-700 disabled:bg-green-100"
        aria-label={todo.is_completed ? 'Task completed' : 'Complete task'}
      >
        {isCompleting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Check className="h-4 w-4" />}
      </button>

      <div className="min-w-0 flex-1">
        <p className={todo.is_completed ? 'break-words text-sm text-stone-400 line-through' : 'break-words text-sm font-semibold'}>
          {todo.title}
        </p>
        <span className="mt-1 inline-block text-xs capitalize text-[var(--text-muted)]">
          {priority} priority
        </span>
      </div>

      <button
        type="button"
        onClick={onDelete}
        disabled={isDeleting}
        className="rounded-lg p-2 text-stone-400 hover:bg-red-50 hover:text-red-600 disabled:opacity-50"
        aria-label={`Delete ${todo.title}`}
      >
        {isDeleting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Trash2 className="h-4 w-4" />}
      </button>
    </article>
  );
}
