import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  fetchTodos,
  createTodo,
  completeTodo,
  deleteTodo,
} from '../features/todos/todosSlice';
import {
  selectAllTodos,
  selectCreateStatus,
  selectCompletingIds,
  selectDeletingIds,
  selectTodoStats,
  selectTodosError,
  selectTodosFetchStatus,
  selectVisibleTodos,
} from '../features/todos/todosSelectors';
import {
  filterChanged,
  queryChanged,
  sortChanged,
  selectTaskFilter,
  selectTaskQuery,
  selectTaskSort,
} from '../features/taskView/taskViewSlice';
import {
  AlertTriangle,
  ArrowDownUp,
  Command,
  Inbox,
  Plus,
  RefreshCw,
  Search,
  Target,
} from 'lucide-react';
import Navbar from './ui/Navbar';
import Card from './ui/Card';
import Input from './ui/Input';
import Button from './ui/Button';
import TodoItem from './TodoItem';
import { toast } from './ui/Toast';
import ConfirmModal from './ui/ConfirmModal';

const PRIORITIES = [
  { value: 'low', label: 'Low', dot: 'bg-green-500' },
  { value: 'medium', label: 'Medium', dot: 'bg-amber-500' },
  { value: 'high', label: 'High', dot: 'bg-red-500' },
];

export default function TodoDashboard({ onLogout, user }) {
  // Step 14B: Redux hooks and selectors
  const dispatch = useDispatch();
  const todos = useSelector(selectAllTodos);
  const visibleTodos = useSelector(selectVisibleTodos);
  const stats = useSelector(selectTodoStats);
  const fetchStatus = useSelector(selectTodosFetchStatus);
  const createStatus = useSelector(selectCreateStatus);
  const completingIds = useSelector(selectCompletingIds);
  const deletingIds = useSelector(selectDeletingIds);
  const error = useSelector(selectTodosError);

  const loading = fetchStatus === 'loading';
  const creating = createStatus === 'loading';

  const filter = useSelector(selectTaskFilter);
  const query = useSelector(selectTaskQuery);
  const sort = useSelector(selectTaskSort);

  // Step 14I: Local state that remains inside component
  const [text, setText] = useState('');
  const [priority, setPriority] = useState('medium');
  const [submitError, setSubmitError] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);

  // Step 14C: Initial fetch effect
  useEffect(() => {
    if (fetchStatus === 'idle') {
      dispatch(fetchTodos());
    }
  }, [dispatch, fetchStatus]);

  // Keyboard shortcut listener
  useEffect(() => {
    const handleShortcut = (event) => {
      const target = event.target;
      const isTyping = ['INPUT', 'TEXTAREA', 'SELECT'].includes(target.tagName) || target.isContentEditable;
      if (isTyping) return;

      if (event.key === '/') {
        event.preventDefault();
        document.getElementById('task-search')?.focus();
      }
      if (event.key.toLowerCase() === 'n') {
        event.preventDefault();
        document.getElementById('new-task-title')?.focus();
      }
    };
    window.addEventListener('keydown', handleShortcut);
    return () => window.removeEventListener('keydown', handleShortcut);
  }, []);

  const progress = stats.total ? Math.round((stats.completed / stats.total) * 100) : 0;

  const today = new Intl.DateTimeFormat(undefined, {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
  }).format(new Date());

  const firstName = (user?.email || 'there').split('@')[0].split(/[._-]/)[0];
  const displayName = firstName.charAt(0).toUpperCase() + firstName.slice(1);
  const currentHour = new Date().getHours();
  const greeting = currentHour < 12 ? 'Good morning' : currentHour < 18 ? 'Good afternoon' : 'Good evening';

  // Step 14E: create handler
  const handleSubmit = async (event) => {
    event.preventDefault();
    const cleanTitle = text.trim();
    setSubmitError(null);

    if (cleanTitle.length < 3) {
      setSubmitError('Use at least 3 characters so the task is clear.');
      return;
    }
    if (cleanTitle.length > 120) {
      setSubmitError('Keep the task under 120 characters.');
      return;
    }

    try {
      await dispatch(createTodo({ title: cleanTitle, priority })).unwrap();
      setText('');
      toast.success('Task added to your plan.');
    } catch (err) {
      setSubmitError(err);
    }
  };

  // Step 14F: complete handler
  const handleComplete = async (id) => {
    try {
      await dispatch(completeTodo(id)).unwrap();
      toast.success('Nice work — task completed.');
    } catch (err) {
      toast.error(err);
    }
  };

  // Step 14G: delete handler
  const handleRemove = async () => {
    if (!deleteTarget) return;

    try {
      await dispatch(deleteTodo(deleteTarget.id)).unwrap();
      setDeleteTarget(null);
      toast.success('Task removed.');
    } catch (err) {
      toast.error(err);
    }
  };

  const renderTasks = () => {
    if (loading && !todos.length) {
      return (
        <div className="divide-y divide-[var(--border)]" aria-label="Loading tasks">
          {[1, 2, 3, 4].map((item) => (
            <div key={item} className="flex animate-pulse items-center gap-4 px-5 py-5">
              <div className="h-7 w-7 rounded-full bg-stone-200" />
              <div className="flex-1 space-y-2"><div className="h-3 w-2/3 rounded bg-stone-200" /><div className="h-2 w-1/3 rounded bg-stone-100" /></div>
            </div>
          ))}
        </div>
      );
    }

    if (error) {
      return (
        <div className="m-4 flex flex-col items-start gap-4 rounded-2xl border border-red-200 bg-red-50 p-5 sm:flex-row sm:items-center">
          <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-white text-[var(--danger)]"><AlertTriangle className="h-5 w-5" /></span>
          <div className="flex-1"><p className="font-extrabold text-red-900">We could not sync your tasks</p><p className="mt-1 text-sm text-red-700">{error}</p></div>
          {/* Step 14D: refresh button handler */}
          <Button variant="secondary" size="sm" onClick={() => dispatch(fetchTodos())}><RefreshCw className="h-3.5 w-3.5" />Try again</Button>
        </div>
      );
    }

    if (!visibleTodos.length) {
      const hasSearch = Boolean(query.trim());
      return (
        <div className="px-6 py-16 text-center">
          <span className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-[var(--bg-muted)] text-[var(--text-secondary)]"><Inbox className="h-6 w-6" /></span>
          <h3 className="mt-5 text-base font-extrabold">{hasSearch ? 'No matching tasks' : filter === 'completed' ? 'Nothing completed yet' : 'Your list is clear'}</h3>
          <p className="mx-auto mt-2 max-w-sm text-sm leading-6 text-[var(--text-secondary)]">
            {hasSearch ? 'Try a different search phrase or clear your filters.' : filter === 'completed' ? 'Complete a task and it will appear here.' : 'Add one meaningful task and start with that.'}
          </p>
        </div>
      );
    }

    return (
      <div className="divide-y divide-[var(--border)]">
        {visibleTodos.map((todo) => (
          /* Step 14H: TodoItem row props */
          <TodoItem
            key={todo.id}
            todo={todo}
            onComplete={handleComplete}
            onDelete={() => setDeleteTarget(todo)}
            isCompleting={Boolean(completingIds[todo.id])}
            isDeleting={Boolean(deletingIds[todo.id])}
          />
        ))}
      </div>
    );
  };

  return (
    <div className="min-h-screen">
      <Navbar user={user} onLogout={onLogout} />
      <main className="mx-auto max-w-7xl px-4 pb-16 pt-8 sm:px-6 sm:pt-10 lg:px-8">
        <section className="hero-panel relative mb-8 overflow-hidden rounded-[2rem] px-5 py-6 text-white sm:px-8 sm:py-8 lg:px-10">
          <div className="grid items-stretch gap-8 lg:grid-cols-[minmax(0,1fr)_340px]">
            <div className="flex flex-col justify-between">
              <div>
                <p className="font-mono text-[10px] font-medium uppercase tracking-[0.2em] text-[#aebdff]">{today}</p>
                <h1 className="mt-3 max-w-2xl text-3xl font-extrabold leading-tight tracking-[-0.045em] sm:text-4xl lg:text-[2.65rem]">{greeting}, {displayName}.</h1>
                <p className="mt-3 max-w-xl text-sm leading-6 text-white/55">Choose the work that matters, clear the noise, and give today a clean finish.</p>
              </div>
              <div className="mt-7 flex flex-wrap items-center gap-3">
                <button type="button" onClick={() => document.getElementById('new-task-title')?.focus()} className="inline-flex h-11 items-center gap-2 rounded-xl bg-white px-4 text-xs font-extrabold text-[#171917] transition hover:-translate-y-0.5 hover:bg-[#f1f3ff]">
                  <Plus className="h-4 w-4" />Add a task<kbd className="ml-1 rounded-md bg-black/5 px-1.5 py-0.5 font-mono text-[9px]">N</kbd>
                </button>
                <span className="inline-flex h-11 items-center gap-2 rounded-xl border border-white/10 bg-white/[0.06] px-4 text-xs font-bold text-white/70">
                  <span className="h-2 w-2 rounded-full bg-[#a8db9c] shadow-[0_0_0_4px_rgba(168,219,156,0.1)]" />
                  {stats.pending === 0 ? 'All clear' : stats.pending + (stats.pending === 1 ? ' task open' : ' tasks open')}
                </span>
              </div>
            </div>

            <div className="rounded-3xl border border-white/10 bg-white/[0.07] p-5 backdrop-blur-sm sm:p-6">
              <div className="flex items-end justify-between gap-4">
                <div><p className="font-mono text-[9px] uppercase tracking-[0.18em] text-white/45">Daily progress</p><p className="mt-2 text-sm font-bold text-white/85">{progress === 100 && stats.total ? 'Perfect finish' : progress >= 50 ? 'You are in motion' : 'Build some momentum'}</p></div>
                <strong className="text-4xl font-extrabold tracking-[-0.05em]">{progress}<span className="text-lg text-white/35">%</span></strong>
              </div>
              <div className="mt-5 h-2 overflow-hidden rounded-full bg-white/10"><div className="h-full rounded-full bg-[#a8db9c] transition-all duration-500" style={{ width: progress + '%' }} /></div>
              <div className="mt-5 grid grid-cols-3 divide-x divide-white/10">
                {[['All', stats.total], ['Open', stats.pending], ['Done', stats.completed]].map(([label, value]) => (
                  <div key={label} className="px-3 first:pl-0 last:pr-0"><p className="text-lg font-extrabold">{value}</p><p className="mt-0.5 text-[9px] font-bold uppercase tracking-wider text-white/35">{label}</p></div>
                ))}
              </div>
            </div>
          </div>
        </section>

        <div className="grid items-start gap-6 lg:grid-cols-[minmax(0,1fr)_360px]">
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
                    <input id="task-search" value={query} onChange={(event) => dispatch(queryChanged(event.target.value))} placeholder="Search tasks..." className="h-10 w-full rounded-xl border border-[var(--border)] bg-stone-50 pl-9 pr-10 text-xs font-semibold focus:border-[var(--primary)] focus:bg-white" />
                    <kbd className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 rounded-md border border-[var(--border)] bg-white px-1.5 py-0.5 font-mono text-[9px] text-[var(--text-muted)]">/</kbd>
                  </label>
                  <label className="relative">
                    <span className="sr-only">Sort tasks</span>
                    <ArrowDownUp className="pointer-events-none absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-[var(--text-muted)]" />
                    <select value={sort} onChange={(event) => dispatch(sortChanged(event.target.value))} className="h-10 appearance-none rounded-xl border border-[var(--border)] bg-stone-50 py-0 pl-8 pr-8 text-xs font-bold text-[var(--text-secondary)] focus:border-[var(--primary)]">
                      <option value="smart">Smart order</option>
                      <option value="newest">Newest first</option>
                      <option value="oldest">Oldest first</option>
                    </select>
                  </label>
                  {/* Step 14D: refresh button handler */}
                  <Button variant="secondary" size="icon" onClick={() => dispatch(fetchTodos())} disabled={loading} aria-label="Refresh tasks"><RefreshCw className={['h-4 w-4', loading ? 'animate-spin' : ''].join(' ')} /></Button>
                </div>
              </div>

              <div className="mt-4 flex gap-1 rounded-xl bg-[var(--bg-muted)] p-1" aria-label="Filter tasks">
                {[
                  { value: 'all', label: 'All', count: stats.total },
                  { value: 'active', label: 'Open', count: stats.pending },
                  { value: 'completed', label: 'Done', count: stats.completed },
                ].map((item) => (
                  <button key={item.value} type="button" onClick={() => dispatch(filterChanged(item.value))} aria-pressed={filter === item.value} className={['flex flex-1 items-center justify-center gap-1.5 rounded-lg px-3 py-2 text-xs font-bold transition', filter === item.value ? 'bg-white text-[var(--text-primary)] shadow-sm' : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'].join(' ')}>
                    {item.label}<span className="text-[10px] text-[var(--text-muted)]">{item.count}</span>
                  </button>
                ))}
              </div>
            </div>
            {renderTasks()}
          </section>

          <aside className="space-y-5 lg:sticky lg:top-24">
            <Card className="new-task-card" title="Add a new task" subtitle="Capture it now. Refine it later." action={<span className="flex h-9 w-9 items-center justify-center rounded-xl bg-[var(--primary-soft)] text-[var(--primary)]"><Plus className="h-4 w-4" /></span>}>
              <form onSubmit={handleSubmit} className="space-y-5">
                <Input id="new-task-title" label="What needs doing?" placeholder="e.g. Review the project brief" value={text} maxLength={121} onChange={(event) => { setText(event.target.value); if (submitError) setSubmitError(null); }} error={submitError} />
                <div>
                  <div className="mb-2 flex items-center justify-between"><label className="text-xs font-bold">Priority</label><span className="font-mono text-[9px] text-[var(--text-muted)]">{text.length}/120</span></div>
                  <div className="grid grid-cols-3 gap-2">
                    {PRIORITIES.map((item) => (
                      <button key={item.value} type="button" onClick={() => setPriority(item.value)} aria-pressed={priority === item.value} className={['flex h-10 items-center justify-center gap-2 rounded-xl border text-[11px] font-bold transition', priority === item.value ? 'border-[var(--primary)] bg-[var(--primary-soft)] text-[var(--primary)]' : 'border-[var(--border)] bg-white text-[var(--text-secondary)] hover:border-[var(--border-strong)]'].join(' ')}>
                        <span className={['h-2 w-2 rounded-full', item.dot].join(' ')} />{item.label}
                      </button>
                    ))}
                  </div>
                </div>
                <Button type="submit" size="lg" className="w-full" isLoading={creating}><Plus className="h-4 w-4" />Add to my list</Button>
              </form>
            </Card>

            <Card className="overflow-hidden">
              <div className="rounded-2xl bg-[var(--primary-soft)] p-4">
                <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-white text-[var(--primary)] shadow-sm"><Target className="h-4 w-4" /></span>
                <p className="mt-4 font-mono text-[9px] font-medium uppercase tracking-[0.16em] text-[var(--primary)]">Focus note</p>
                <h3 className="mt-2 text-sm font-extrabold">{progress === 100 && stats.total ? 'Make room for tomorrow.' : progress >= 50 ? 'Protect your momentum.' : 'Start with the smallest win.'}</h3>
                <p className="mt-1 text-xs leading-5 text-[var(--text-secondary)]">{stats.pending ? 'Pick one open task and finish it before adding more.' : 'Your list is clear. Enjoy the space you made.'}</p>
              </div>
              <div className="mt-4 flex items-center justify-between text-[10px] font-bold text-[var(--text-muted)]"><span className="flex items-center gap-1.5"><Command className="h-3.5 w-3.5" />Shortcuts</span><span><kbd className="font-mono">/</kbd> search · <kbd className="font-mono">N</kbd> new</span></div>
            </Card>
          </aside>
        </div>
      </main>

      <ConfirmModal
        open={Boolean(deleteTarget)}
        title="Delete this task?"
        description={deleteTarget ? '“' + deleteTarget.title + '” will be permanently removed from your list.' : ''}
        isLoading={Boolean(deleteTarget && deletingIds[deleteTarget.id])}
        onCancel={() => setDeleteTarget(null)}
        onConfirm={handleRemove}
      />
    </div>
  );
}
