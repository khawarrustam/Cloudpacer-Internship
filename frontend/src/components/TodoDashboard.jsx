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
  // English: Redux hooks stay in the component so its data flow is easy to present.
  // Roman Urdu: Redux hooks component mein hain taa-ke data flow presentation mein clear rahe.
  const dispatch = useDispatch();

  // English: The selected delete target is temporary UI state, not shared app data.
  // Roman Urdu: Delete target temporary UI state hai, shared data nahi, is liye local hai.
  const [deleteTarget, setDeleteTarget] = useState(null);

  // English: This custom hook enables '/' for search and 'n' for a new task.
  // Roman Urdu: Ye custom hook '/' se search aur 'n' se new task focus karta hai.
  useKeyboardShortcuts();

  // English: Selectors read Redux state and re-render this component when values change.
  // Roman Urdu: Selectors Redux state read karte hain aur change par component re-render hota hai.
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

  // English: Fetch todos once when the dashboard first enters the idle state.
  // Roman Urdu: Dashboard pehli dafa idle ho to backend se todos load karo.
  useEffect(() => {
    if (fetchStatus === 'idle') {
      dispatch(fetchTodos());
    }
  }, [dispatch, fetchStatus]);

  // English: Each handler dispatches an async thunk; its reducer updates Redux on success.
  // Roman Urdu: Har handler async thunk dispatch karta hai; success par reducer Redux update karta hai.
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

  // English: Related list props are grouped, while Redux hooks remain visible above.
  // Roman Urdu: Related list props group hain, lekin Redux hooks upar direct visible hain.
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

      {/* English: The modal opens only after the user selects a todo to delete. */}
      {/* Roman Urdu: Modal tab khulta hai jab user delete ke liye todo select karta hai. */}
      <ConfirmModal
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
