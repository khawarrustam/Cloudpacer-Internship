import React, { useEffect, useState } from 'react';
import { LogOut } from 'lucide-react';
import { useDispatch, useSelector } from 'react-redux';
import {
  completeTodo,
  createTodo,
  deleteTodo,
  fetchTodos,
} from '../features/todos/todosSlice';
import {
  selectAllTodos,
  selectCompletingIds,
  selectCreateStatus,
  selectDeletingIds,
  selectTodoStats,
  selectTodosError,
  selectTodosFetchStatus,
  selectVisibleTodos,
} from '../features/todos/todosSelectors';
import {
  filterChanged,
  queryChanged,
  selectTaskFilter,
  selectTaskQuery,
  selectTaskSort,
  sortChanged,
} from '../features/taskView/taskViewSlice';
import { useKeyboardShortcuts } from '../hooks/useKeyboardShortcuts';
import AddTodoForm from './todos/AddTodoForm';
import TodoListPanel from './todos/TodoListPanel';
import Button from './ui/Button';
import ConfirmModal from './ui/ConfirmModal';
import { toast } from './ui/Toast';

export default function TodoDashboard({ onLogout, user }) {
  // Component direct Redux hooks use karta hai, is liye data flow yahin visible hai.
  const dispatch = useDispatch();

  // Delete target local UI state hai; shared app data nahi, is liye Redux mein nahi hai.
  const [deleteTarget, setDeleteTarget] = useState(null);
  useKeyboardShortcuts();

  // Selectors Redux state read karte hain aur state change par component re-render hota hai.
  const todos = useSelector(selectAllTodos);
  const visibleTodos = useSelector(selectVisibleTodos);
  const stats = useSelector(selectTodoStats);
  const fetchStatus = useSelector(selectTodosFetchStatus);
  const createStatus = useSelector(selectCreateStatus);
  const completingIds = useSelector(selectCompletingIds);
  const deletingIds = useSelector(selectDeletingIds);
  const error = useSelector(selectTodosError);
  const filter = useSelector(selectTaskFilter);
  const query = useSelector(selectTaskQuery);
  const sort = useSelector(selectTaskSort);

  // Dashboard pehli dafa open ho to backend se todos load karo.
  useEffect(() => {
    if (fetchStatus === 'idle') {
      dispatch(fetchTodos());
    }
  }, [dispatch, fetchStatus]);

  // Async thunks API call karte hain; fulfilled reducer Redux state update karta hai.
  const handleAdd = async (newTodo) => {
    await dispatch(createTodo(newTodo)).unwrap();
    toast.success('Task added.');
  };

  const handleComplete = async (id) => {
    try {
      await dispatch(completeTodo(id)).unwrap();
      toast.success('Task completed.');
    } catch (requestError) {
      toast.error(requestError);
    }
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;

    try {
      await dispatch(deleteTodo(deleteTarget.id)).unwrap();
      setDeleteTarget(null);
      toast.success('Task deleted.');
    } catch (requestError) {
      toast.error(requestError);
    }
  };

  // Related list props group ki hain; Redux hooks upar component mein direct visible hain.
  const todoState = {
    todos,
    visibleTodos,
    stats,
    error,
    filter,
    query,
    sort,
    loading: fetchStatus === 'loading',
    completingIds,
    deletingIds,
    refresh: () => dispatch(fetchTodos()),
    setFilter: (value) => dispatch(filterChanged(value)),
    setQuery: (value) => dispatch(queryChanged(value)),
    setSort: (value) => dispatch(sortChanged(value)),
  };

  return (
    <div className="min-h-screen">
      <header className="border-b border-[var(--border)] bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4 sm:px-6">
          <div>
            <h1 className="text-lg font-extrabold">TodoFlow</h1>
            <p className="text-xs text-[var(--text-secondary)]">{user?.email}</p>
          </div>
          <Button variant="secondary" size="sm" onClick={onLogout}>
            <LogOut className="h-4 w-4" />
            Log out
          </Button>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6">
        <div className="mb-6">
          <h2 className="text-2xl font-extrabold">My tasks</h2>
          <p className="mt-1 text-sm text-[var(--text-secondary)]">
            {stats.pending} open · {stats.completed} completed
          </p>
        </div>

        <div className="grid items-start gap-6 lg:grid-cols-[300px_minmax(0,1fr)]">
          <AddTodoForm
            creating={createStatus === 'loading'}
            onAdd={handleAdd}
          />
          <TodoListPanel
            todoState={todoState}
            onComplete={handleComplete}
            onDelete={setDeleteTarget}
          />
        </div>
      </main>

      <ConfirmModal
        // Modal tab open hota hai jab user ne delete karne ke liye todo select kiya ho.
        open={Boolean(deleteTarget)}
        title="Delete task?"
        description={deleteTarget ? `Delete “${deleteTarget.title}”?` : ''}
        isLoading={Boolean(deleteTarget && deletingIds[deleteTarget.id])}
        onCancel={() => setDeleteTarget(null)}
        onConfirm={handleDelete}
      />
    </div>
  );
}
