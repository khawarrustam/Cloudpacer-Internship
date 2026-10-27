import React, { useState } from 'react';
import { useTodos } from '../hooks/useTodos';
import { useKeyboardShortcuts } from '../hooks/useKeyboardShortcuts';
import Navbar from './ui/Navbar';
import { toast } from './ui/Toast';
import ConfirmModal from './ui/ConfirmModal';
import AddTodoForm from './todos/AddTodoForm';
import DashboardHero from './todos/DashboardHero';
import FocusCard from './todos/FocusCard';
import TodoListPanel from './todos/TodoListPanel';

export default function TodoDashboard({ onLogout, user }) {
  // English: Shared todo data comes from Redux through this custom hook.
  // Roman Urdu: Shared todo data is custom hook ke through Redux se aata hai.
  const todoState = useTodos();

  // English: The selected delete item is temporary UI state, so it stays local.
  // Roman Urdu: Selected delete item temporary UI state hai, is liye local hai.
  const [deleteTarget, setDeleteTarget] = useState(null);
  useKeyboardShortcuts();

  const progress = todoState.stats.total
    ? Math.round((todoState.stats.completed / todoState.stats.total) * 100)
    : 0;

  const handleAdd = async (todo) => {
    // English: This calls the Redux createTodo thunk through useTodos.
    // Roman Urdu: Yeh useTodos ke through Redux createTodo thunk call karta hai.
    await todoState.addTodo(todo);
    toast.success('Task added to your plan.');
  };

  const handleComplete = async (id) => {
    // English: Redux updates the matching todo after the backend succeeds.
    // Roman Urdu: Backend success ke baad Redux matching todo update karta hai.
    try {
      await todoState.finishTodo(id);
      toast.success('Nice work - task completed.');
    } catch (error) {
      toast.error(error);
    }
  };

  const handleRemove = async () => {
    // English: The modal chooses the id; Redux performs the delete request.
    // Roman Urdu: Modal id choose karta hai; Redux delete request chalata hai.
    if (!deleteTarget) return;

    try {
      await todoState.removeTodo(deleteTarget.id);
      setDeleteTarget(null);
      toast.success('Task removed.');
    } catch (error) {
      toast.error(error);
    }
  };

  return (
    <div className="min-h-screen">
      <Navbar user={user} onLogout={onLogout} />
      <main className="mx-auto max-w-7xl px-4 pb-16 pt-8 sm:px-6 sm:pt-10 lg:px-8">
        <DashboardHero user={user} stats={todoState.stats} progress={progress} />

        <div className="grid items-start gap-6 lg:grid-cols-[minmax(0,1fr)_360px]">
          <TodoListPanel
            todos={todoState.todos}
            visibleTodos={todoState.visibleTodos}
            stats={todoState.stats}
            loading={todoState.loading}
            error={todoState.error}
            filter={todoState.filter}
            query={todoState.query}
            sort={todoState.sort}
            completingIds={todoState.completingIds}
            deletingIds={todoState.deletingIds}
            onRefresh={todoState.refresh}
            onFilterChange={todoState.setFilter}
            onQueryChange={todoState.setQuery}
            onSortChange={todoState.setSort}
            onComplete={handleComplete}
            onDelete={setDeleteTarget}
          />

          <aside className="space-y-5 lg:sticky lg:top-24">
            <AddTodoForm creating={todoState.creating} onAdd={handleAdd} />
            <FocusCard
              progress={progress}
              pending={todoState.stats.pending}
              hasTodos={Boolean(todoState.stats.total)}
            />
          </aside>
        </div>
      </main>

      <ConfirmModal
        open={Boolean(deleteTarget)}
        title="Delete this task?"
        description={deleteTarget ? `"${deleteTarget.title}" will be permanently removed from your list.` : ''}
        isLoading={Boolean(deleteTarget && todoState.deletingIds[deleteTarget.id])}
        onCancel={() => setDeleteTarget(null)}
        onConfirm={handleRemove}
      />
    </div>
  );
}
