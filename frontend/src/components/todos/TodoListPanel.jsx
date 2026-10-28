import React from 'react';
import TodoItem from '../TodoItem';
import Button from '../ui/Button';

function emptyMessage(filter, query) {
  if (query.trim()) return 'No tasks match your search.';
  if (filter === 'completed') return 'No completed tasks yet.';
  if (filter === 'active') return 'No open tasks.';
  return 'No tasks yet. Add your first task.';
}

export default function TodoListPanel({ todoState, onComplete, onDelete }) {
  // Dashboard Redux values aur actions ko aik simple object mein pass karta hai.
  const {
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
    refresh,
    setFilter,
    setQuery,
    setSort,
  } = todoState;

  const filters = [
    ['all', 'All', stats.total],
    ['active', 'Open', stats.pending],
    ['completed', 'Done', stats.completed],
  ];

  const renderContent = () => {
    // UI order: loading, error, empty state, phir actual todo list.
    if (loading && !todos.length) {
      return <p className="p-8 text-center text-sm text-[var(--text-secondary)]">Loading tasks…</p>;
    }

    if (error) {
      return (
        <div className="m-4 rounded-xl bg-red-50 p-4 text-sm text-red-700">
          <p className="font-bold">Could not load tasks.</p>
          <p className="mt-1">{error}</p>
          <Button variant="secondary" size="sm" className="mt-3" onClick={refresh}>
            Try again
          </Button>
        </div>
      );
    }

    if (!visibleTodos.length) {
      return <p className="p-8 text-center text-sm text-[var(--text-secondary)]">{emptyMessage(filter, query)}</p>;
    }

    // key React ko har rendered todo uniquely identify karne mein help karti hai.
    return visibleTodos.map((todo) => (
      <TodoItem
        key={todo.id}
        todo={todo}
        onComplete={onComplete}
        onDelete={() => onDelete(todo)}
        isCompleting={Boolean(completingIds[todo.id])}
        isDeleting={Boolean(deletingIds[todo.id])}
      />
    ));
  };

  return (
    <section className="overflow-hidden rounded-2xl border border-[var(--border)] bg-white shadow-[var(--shadow-sm)]">
      <div className="border-b border-[var(--border)] p-4">
        <div className="flex items-center justify-between gap-3">
          <h3 className="font-extrabold">Task list</h3>
          <Button variant="secondary" size="sm" onClick={refresh} disabled={loading}>
            Refresh
          </Button>
        </div>

        <div className="mt-4 grid gap-2 sm:grid-cols-[1fr_150px]">
          <input
            id="task-search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search tasks"
            className="h-10 rounded-xl border border-[var(--border)] px-3 text-sm"
          />
          <select
            value={sort}
            onChange={(event) => setSort(event.target.value)}
            className="h-10 rounded-xl border border-[var(--border)] bg-white px-3 text-sm"
          >
            <option value="smart">Smart order</option>
            <option value="newest">Newest first</option>
            <option value="oldest">Oldest first</option>
          </select>
        </div>

        <div className="mt-3 flex gap-2">
          {filters.map(([value, label, count]) => (
            <button
              key={value}
              type="button"
              onClick={() => setFilter(value)}
              className={[
                'rounded-lg px-3 py-2 text-xs font-bold',
                filter === value
                  ? 'bg-[var(--primary)] text-white'
                  : 'bg-stone-100 text-[var(--text-secondary)]',
              ].join(' ')}
            >
              {label} ({count})
            </button>
          ))}
        </div>
      </div>

      <div>{renderContent()}</div>
    </section>
  );
}
