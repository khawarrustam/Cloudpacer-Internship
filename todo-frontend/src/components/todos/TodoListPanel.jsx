import React from 'react';
import {
  AlertTriangle,
  ArrowDownUp,
  Inbox,
  RefreshCw,
  Search,
} from 'lucide-react';
import TodoItem from '../TodoItem';
import Button from '../ui/Button';

function LoadingRows() {
  return (
    <div className="divide-y divide-[var(--border)]" aria-label="Loading tasks">
      {[1, 2, 3, 4].map((item) => (
        <div key={item} className="flex animate-pulse items-center gap-4 px-5 py-5">
          <div className="h-7 w-7 rounded-full bg-stone-200" />
          <div className="flex-1 space-y-2">
            <div className="h-3 w-2/3 rounded bg-stone-200" />
            <div className="h-2 w-1/3 rounded bg-stone-100" />
          </div>
        </div>
      ))}
    </div>
  );
}

function EmptyState({ filter, query }) {
  const hasSearch = Boolean(query.trim());
  const title = hasSearch
    ? 'No matching tasks'
    : filter === 'completed'
      ? 'Nothing completed yet'
      : 'Your list is clear';
  const message = hasSearch
    ? 'Try a different search phrase or clear your filters.'
    : filter === 'completed'
      ? 'Complete a task and it will appear here.'
      : 'Add one meaningful task and start with that.';

  return (
    <div className="px-6 py-16 text-center">
      <span className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-[var(--bg-muted)] text-[var(--text-secondary)]">
        <Inbox className="h-6 w-6" />
      </span>
      <h3 className="mt-5 text-base font-extrabold">{title}</h3>
      <p className="mx-auto mt-2 max-w-sm text-sm leading-6 text-[var(--text-secondary)]">{message}</p>
    </div>
  );
}

function TodoRows({ todos, completingIds, deletingIds, onComplete, onDelete }) {
  return (
    <div className="divide-y divide-[var(--border)]">
      {todos.map((todo) => (
        <TodoItem
          key={todo.id}
          todo={todo}
          onComplete={onComplete}
          onDelete={() => onDelete(todo)}
          isCompleting={Boolean(completingIds[todo.id])}
          isDeleting={Boolean(deletingIds[todo.id])}
        />
      ))}
    </div>
  );
}

export default function TodoListPanel({
  todos,
  visibleTodos,
  stats,
  loading,
  error,
  filter,
  query,
  sort,
  completingIds,
  deletingIds,
  onRefresh,
  onFilterChange,
  onQueryChange,
  onSortChange,
  onComplete,
  onDelete,
}) {
  const filters = [
    { value: 'all', label: 'All', count: stats.total },
    { value: 'active', label: 'Open', count: stats.pending },
    { value: 'completed', label: 'Done', count: stats.completed },
  ];

  let content;
  if (loading && !todos.length) {
    content = <LoadingRows />;
  } else if (error) {
    content = (
      <div className="m-4 flex flex-col items-start gap-4 rounded-2xl border border-red-200 bg-red-50 p-5 sm:flex-row sm:items-center">
        <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-white text-[var(--danger)]">
          <AlertTriangle className="h-5 w-5" />
        </span>
        <div className="flex-1">
          <p className="font-extrabold text-red-900">We could not sync your tasks</p>
          <p className="mt-1 text-sm text-red-700">{error}</p>
        </div>
        <Button variant="secondary" size="sm" onClick={onRefresh}>
          <RefreshCw className="h-3.5 w-3.5" />
          Try again
        </Button>
      </div>
    );
  } else if (!visibleTodos.length) {
    content = <EmptyState filter={filter} query={query} />;
  } else {
    content = (
      <TodoRows
        todos={visibleTodos}
        completingIds={completingIds}
        deletingIds={deletingIds}
        onComplete={onComplete}
        onDelete={onDelete}
      />
    );
  }

  return (
    <section className="overflow-hidden rounded-[var(--radius-xl)] border border-[var(--border)] bg-white shadow-[var(--shadow-md)]">
      <div className="border-b border-[var(--border)] p-4 sm:p-5">
        <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
          <div>
            <h2 className="text-lg font-extrabold tracking-tight">Your tasks</h2>
            <p className="mt-1 text-xs text-[var(--text-secondary)]">{visibleTodos.length} shown of {stats.total}</p>
          </div>

          <div className="flex flex-col gap-2 sm:flex-row">
            <label className="relative min-w-0 sm:w-60">
              <span className="sr-only">Search tasks</span>
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--text-muted)]" />
              <input
                id="task-search"
                value={query}
                onChange={(event) => onQueryChange(event.target.value)}
                placeholder="Search tasks..."
                className="h-10 w-full rounded-xl border border-[var(--border)] bg-stone-50 pl-9 pr-10 text-xs font-semibold focus:border-[var(--primary)] focus:bg-white"
              />
              <kbd className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 rounded-md border border-[var(--border)] bg-white px-1.5 py-0.5 font-mono text-[9px] text-[var(--text-muted)]">/</kbd>
            </label>

            <label className="relative">
              <span className="sr-only">Sort tasks</span>
              <ArrowDownUp className="pointer-events-none absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-[var(--text-muted)]" />
              <select
                value={sort}
                onChange={(event) => onSortChange(event.target.value)}
                className="h-10 appearance-none rounded-xl border border-[var(--border)] bg-stone-50 py-0 pl-8 pr-8 text-xs font-bold text-[var(--text-secondary)] focus:border-[var(--primary)]"
              >
                <option value="smart">Smart order</option>
                <option value="newest">Newest first</option>
                <option value="oldest">Oldest first</option>
              </select>
            </label>

            <Button variant="secondary" size="icon" onClick={onRefresh} disabled={loading} aria-label="Refresh tasks">
              <RefreshCw className={['h-4 w-4', loading ? 'animate-spin' : ''].join(' ')} />
            </Button>
          </div>
        </div>

        <div className="mt-4 flex gap-1 rounded-xl bg-[var(--bg-muted)] p-1" aria-label="Filter tasks">
          {filters.map((item) => (
            <button
              key={item.value}
              type="button"
              onClick={() => onFilterChange(item.value)}
              aria-pressed={filter === item.value}
              className={[
                'flex flex-1 items-center justify-center gap-1.5 rounded-lg px-3 py-2 text-xs font-bold transition',
                filter === item.value
                  ? 'bg-white text-[var(--text-primary)] shadow-sm'
                  : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]',
              ].join(' ')}
            >
              {item.label}
              <span className="text-[10px] text-[var(--text-muted)]">{item.count}</span>
            </button>
          ))}
        </div>
      </div>

      {content}
    </section>
  );
}
