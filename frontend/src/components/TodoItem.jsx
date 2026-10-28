import React from 'react';
import { Calendar, Check, Loader2, Trash2 } from 'lucide-react';
import Badge from './ui/Badge';

function formatTaskDate(value) {
  if (!value) return '';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '';
  return new Intl.DateTimeFormat(undefined, { month: 'short', day: 'numeric' }).format(date);
}

export default function TodoItem({ todo, onComplete, onDelete, isCompleting = false, isDeleting = false }) {
  const priority = String(todo.priority || '').toLowerCase();
  const priorityVariants = { high: 'danger', medium: 'warning', low: 'success' };
  const priorityAccents = { high: 'bg-red-400', medium: 'bg-amber-400', low: 'bg-green-400' };
  const dateLabel = todo.is_completed && todo.completed_at
    ? 'Finished ' + formatTaskDate(todo.completed_at)
    : 'Added ' + formatTaskDate(todo.created_at);

  return (
    <article className={['group relative grid grid-cols-[auto_1fr_auto] items-center gap-3 overflow-hidden px-4 py-4 transition-colors sm:gap-4 sm:px-5', todo.is_completed ? 'bg-stone-50/65' : 'hover:bg-[var(--bg-subtle)]'].join(' ')}>
      <span className={['absolute inset-y-3 left-0 w-[3px] rounded-r-full transition-opacity', todo.is_completed ? 'bg-stone-200 opacity-40' : priorityAccents[priority] || 'bg-stone-300 opacity-80'].join(' ')} aria-hidden="true" />
      <button
        type="button"
        onClick={() => onComplete(todo.id)}
        disabled={todo.is_completed || isCompleting}
        aria-label={todo.is_completed ? 'Task completed' : 'Mark task complete'}
        className={['flex h-7 w-7 shrink-0 items-center justify-center rounded-full border-2 transition duration-200', todo.is_completed ? 'border-green-600 bg-green-600 text-white' : 'border-stone-300 bg-white text-transparent hover:border-[var(--primary)] hover:text-[var(--primary)]'].join(' ')}
      >
        {isCompleting ? <Loader2 className="h-4 w-4 animate-spin text-[var(--primary)]" /> : <Check className="h-4 w-4" strokeWidth={3} />}
      </button>

      <div className="min-w-0">
        <p className={['break-words text-sm font-bold leading-5 transition', todo.is_completed ? 'text-[var(--text-muted)] line-through decoration-stone-400' : 'text-[var(--text-primary)]'].join(' ')}>
          {todo.title}
        </p>
        <div className="mt-2 flex flex-wrap items-center gap-2">
          <Badge variant={priorityVariants[priority] || 'default'}>{priority || 'normal'}</Badge>
          {dateLabel && (
            <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-[var(--text-muted)]">
              <Calendar className="h-3 w-3" />
              {dateLabel}
            </span>
          )}
        </div>
      </div>

      <button
        type="button"
        onClick={onDelete}
        disabled={isDeleting}
        aria-label={'Delete task ' + todo.title}
        className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl text-[var(--text-muted)] transition hover:bg-red-50 hover:text-[var(--danger)] disabled:pointer-events-none disabled:opacity-50 sm:opacity-0 sm:group-hover:opacity-100 sm:group-focus-within:opacity-100"
      >
        {isDeleting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Trash2 className="h-4 w-4" />}
      </button>
    </article>
  );
}
