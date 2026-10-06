import React from 'react';
import { CheckCircle2, Circle, Loader2, Trash2 } from 'lucide-react';
import Badge from './ui/Badge';

export default function TodoItem({ todo, onComplete, onDelete, isCompleting = false, isDeleting = false }) {
  const priorityColors = {
    'high': 'danger',
    'medium': 'warning',
    'low': 'success',
  };

  return (
    <article className={`group flex items-center justify-between gap-4 p-4 transition-all duration-200 hover:bg-slate-50 rounded-lg border border-transparent hover:border-slate-200 ${todo.is_completed ? 'opacity-60' : ''} animate-fade-in`}>
      <div className="flex min-w-0 items-center gap-4">
        <button
          onClick={() => onComplete(todo.id)}
          disabled={todo.is_completed || isCompleting}
          aria-label={todo.is_completed ? 'Task completed' : 'Complete task'}
          className="flex h-6 w-6 shrink-0 items-center justify-center text-slate-400 transition-all duration-200 hover:text-indigo-600 active:scale-90 disabled:pointer-events-none"
        >
          {isCompleting ? (
            <Loader2 className="h-5 w-5 animate-spin text-indigo-500" />
          ) : todo.is_completed ? (
            <CheckCircle2 className="h-5 w-5 text-emerald-500" />
          ) : (
            <Circle className="h-5 w-5" />
          )}
        </button>

        <div className="min-w-0">
          <p className={`truncate text-sm font-medium transition-all duration-200 ${todo.is_completed ? 'line-through text-slate-400' : 'text-slate-800'}`}>
            {todo.title}
          </p>
          <div className="mt-1 flex items-center gap-2">
            <Badge variant={priorityColors[todo.priority] || 'default'}>
              {todo.priority}
            </Badge>
          </div >
        </div >
      </div >

      <button
        onClick={() => onDelete(todo.id)}
        disabled={isDeleting}
        aria-label={`Delete task ${todo.title}`}
        className="flex h-8 w-8 shrink-0 items-center justify-center text-slate-300 transition-all duration-200 hover:text-red-600 disabled:pointer-events-none disabled:opacity-50 opacity-0 group-hover:opacity-100"
      >
        {isDeleting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Trash2 className="h-4 w-4" />}
      </button>
    </article>
  );
}
