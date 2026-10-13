import React, { useState } from 'react';
import { AlertTriangle, CheckCircle2, CircleDot, Inbox, LayoutList, Loader2, Plus, Rows3 } from 'lucide-react';
import { useTodos } from '../hooks/useTodos';
import Navbar from './ui/Navbar';
import StatsCard from './ui/StatsCard';
import Card from './ui/Card';
import Input from './ui/Input';
import Button from './ui/Button';
import TodoItem from './TodoItem';
import { toast } from './ui/Toast';
import ConfirmModal from './ui/ConfirmModal';

export default function TodoDashboard({ onLogout, user }) {
  // ============================================================================
  // HOOKS USED IN THIS COMPONENT:
  // 1. useTodos (Custom Hook)
  // 2. useState (Built-in React Hook)
  // [Roman Urdu]: Dashboard me tasks ki state aur UI form inputs ko manage karne ke liye yeh hooks use ho rahe hain.
  // ============================================================================

  // Hook: useTodos (Custom Hook)
  // What it does: Manages fetching, caching, and CRUD mutations (add, complete, delete) for user tasks.
  // Why it is here: Keeps API calls, error handling, and state synchronization decoupled from UI rendering.
  // Roman Urdu: Hamara custom hook jo backend se tasks laata hai aur add/complete/delete karne ke functions deta hai.
  const { todos, loading: todoLoading, error: todoError, addTodo, completeTodo, removeTodo } = useTodos();

  // Hook: useState
  // What it does: Holds the task title text currently typed into the input field.
  // Why it is here: Controls the form input value so it can be validated and cleared after successful creation.
  // Roman Urdu: Naye task ka naam jo user input me type karta hai usko save karta hai taake create hone ke baad input empty ho sake.
  const [text, setText] = useState('');

  // Hook: useState
  // What it does: Holds the chosen priority level ('low', 'medium', 'high') for a new task.
  // Why it is here: Keeps the priority dropdown value synchronized with component state.
  // Roman Urdu: Task ki priority level ('low', 'medium', 'high') store karta hai jo select dropdown se chuni jaati hai.
  const [priority, setPriority] = useState('medium');

  // Hook: useState
  // What it does: Stores validation error messages specifically for the task creation form.
  // Why it is here: Renders inline error feedback directly under the task title input.
  // Roman Urdu: Agar task ka title khali ho toh input ke neechay validation error message dikhata hai.
  const [submitError, setSubmitError] = useState(null);

  // Hook: useState
  // What it does: Stores the active filter tab ('all', 'active', 'completed').
  // Why it is here: Drives client-side task filtering without triggering redundant backend requests.
  // Roman Urdu: Yeh track karta hai ke user sabhi tasks dekh raha hai ('all'), sirf baaqi bache huye ('active'), ya mukammal ('completed').
  const [filter, setFilter] = useState('all');

  // Hook: useState
  // What it does: Boolean flag indicating if task creation is actively in flight.
  // Why it is here: Shows a loading spinner and disables submit button to avoid duplicate submissions.
  // Roman Urdu: Jab naya task server par create ho raha ho tab submit button par loading spinner dikhata hai.
  const [creating, setCreating] = useState(false);

  // Hook: useState
  // What it does: Holds the ID of the specific todo item currently being marked complete.
  // Why it is here: Shows a per-item spinner on only the clicked task rather than freezing the whole list.
  // Roman Urdu: Jis specific task par click kiya gaya ho sirf uske circle button par spinner dikhata hai.
  const [completingId, setCompletingId] = useState(null);

  // Hook: useState
  // What it does: Holds the todo object chosen by the user for deletion (null when modal is closed).
  // Why it is here: Controls the ConfirmModal visibility and provides context on which task will be purged.
  // Roman Urdu: Jis task ko delete karna ho uska data rakhta hai taake delete confirmation popup modal open ho sake.
  const [deleteTarget, setDeleteTarget] = useState(null);

  // Hook: useState
  // What it does: Holds the ID of the todo actively being deleted during the delete network request.
  // Why it is here: Shows loading spinner in the ConfirmModal button and prevents double deletion clicks.
  // Roman Urdu: Jab task delete hone ki API call chal rahi ho tab delete button par loading spinner dikhata hai.
  const [deletingId, setDeletingId] = useState(null);

  const stats = {
    total: todos.length,
    pending: todos.filter((todo) => !todo.is_completed).length,
    completed: todos.filter((todo) => todo.is_completed).length,
  };

  const filteredTodos = todos.filter((todo) => {
    if (filter === 'active') return !todo.is_completed;
    if (filter === 'completed') return todo.is_completed;
    return true;
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitError(null);

    if (!text.trim()) {
      setSubmitError('Please enter a task title.');
      return;
    }

    setCreating(true);
    const result = await addTodo(text.trim(), priority);
    setCreating(false);

    if (result.success) {
      toast.success('Task created successfully.');
      setText('');
      return;
    }

    setSubmitError(result.error);
  };

  const handleComplete = async (id) => {
    setCompletingId(id);
    const result = await completeTodo(id);
    setCompletingId(null);

    if (result.success) {
      toast.success('Task completed.');
      return;
    }

    toast.error(result.error);
  };

  const handleRemove = async () => {
    if (!deleteTarget) return;

    setDeletingId(deleteTarget.id);
    const result = await removeTodo(deleteTarget.id);
    setDeletingId(null);

    if (result.success) {
      toast.success('Task deleted.');
      setDeleteTarget(null);
      return;
    }

    toast.error(result.error);
  };

  const renderTaskList = () => {
    if (todoLoading) {
      return (
        <div className="space-y-4">
          {[1, 2, 3, 4].map((item) => (
            <div key={item} className="h-16 animate-pulse rounded-sm border border-[var(--border)] bg-white" />
          ))}
        </div>
      );
    }

    if (todoError) {
      return (
        <div className="rounded-sm border-2 border-red-100 bg-red-50 p-6 text-red-700">
          <div className="flex items-start gap-4">
            <AlertTriangle className="mt-1 h-6 w-6 shrink-0" />
            <div className="space-y-1">
              <p className="font-bold">Sync Error</p>
              <p className="text-sm opacity-90">{todoError}</p>
            </div>
          </div>
        </div>
      );
    }

    if (filteredTodos.length === 0) {
      return (
        <div className="rounded-sm border-2 border-dashed border-[var(--border)] bg-white px-6 py-20 text-center">
          <div className="mx-auto mb-6 flex h-14 w-14 items-center justify-center rounded-full bg-[var(--bg-muted)] text-[var(--text-muted)]">
            <Inbox className="h-6 w-6" />
          </div>
          <p className="text-lg font-bold text-[var(--text-primary)]">Queue is empty</p>
          <p className="mt-2 text-sm font-medium text-[var(--text-secondary)]">The ledger is clear. You are caught up on all requirements.</p>
        </div>
      );
    }

    return (
      <div className="divide-y divide-[var(--border)] bg-[var(--bg-surface)] border border-[var(--border)] rounded-none shadow-sm">
        {filteredTodos.map((todo) => (
          <TodoItem
            key={todo.id}
            todo={todo}
            onComplete={handleComplete}
            onDelete={() => setDeleteTarget(todo)}
            isCompleting={completingId === todo.id}
            isDeleting={deletingId === todo.id}
          />
        ))}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-[var(--bg-main)] text-[var(--text-primary)] scanline">
      <Navbar user={user} onLogout={onLogout} />

      <main className="mx-auto max-w-5xl px-4 py-12 sm:px-6 lg:py-16">
        <header className="mb-12 flex flex-col justify-between gap-6 border-b-2 border-[var(--primary)] pb-8 sm:flex-row sm:items-end">
          <div className="space-y-2">
            <p className="text-xs font-black uppercase tracking-[0.3em] text-[var(--primary)] shadow-[0_0_5px_var(--primary)]">System Terminal // Queue</p>
            <h1 className="text-4xl font-black tracking-tighter text-[var(--text-primary)] sm:text-5xl uppercase">Task Ledger v1.0</h1>
            <p className="max-w-xl text-sm font-mono text-[var(--text-secondary)]">
              STATUS: OPERATIONAL | ENCRYPTED CONNECTION ESTABLISHED | READY FOR INPUT
            </p>
          </div >
          <div className="inline-block rounded-none border-2 border-[var(--primary)] bg-black px-4 py-2 text-sm font-black uppercase tracking-tighter text-[var(--primary)] shadow-[0_0_10px_var(--primary)]">
            {stats.pending === 0 ? 'Sectors Clear' : `${stats.pending} Pending Tasks`}
          </div >
        </header>

        <div className="mb-12 grid grid-cols-1 gap-6 md:grid-cols-3">
          <StatsCard label="Total Tasks" value={stats.total} color="slate" icon={Rows3} />
          <StatsCard label="Pending" value={stats.pending} color="blue" icon={CircleDot} />
          <StatsCard label="Completed" value={stats.completed} color="emerald" icon={CheckCircle2} />
        </div >

        <div className="grid grid-cols-1 gap-12 lg:grid-cols-[380px_1fr]">
          <div className="lg:sticky lg:top-24 h-fit">
            <Card title="Input Module" subtitle="Define system requirement">
              <form onSubmit={handleSubmit} className="space-y-6">
                <Input
                  label="Task Title"
                  placeholder="ENTER REQUIREMENT..."
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  error={submitError}
                  required
                />

                <div className="flex flex-col gap-2">
                  <label className="text-xs font-black uppercase tracking-wider text-[var(--text-secondary)]" htmlFor="priority">
                    Priority Level
                  </label>
                  <select
                    id="priority"
                    value={priority}
                    onChange={(e) => setPriority(e.target.value)}
                    className="h-12 w-full rounded-none border-2 border-[var(--border)] bg-black px-3 text-sm font-mono text-[var(--text-primary)] transition-all duration-100 focus:border-[var(--primary)] focus:outline-none"
                  >
                    <option value="low">Low Impact</option>
                    <option value="medium">Medium Impact</option>
                    <option value="high">High Impact</option>
                  </select>
                </div >

                <Button type="submit" size="lg" className="w-full py-4 text-base" isLoading={creating}>
                  <Plus className="h-5 w-5" />
                  Commit to Queue
                </Button>
              </form>
            </Card>
          </div >

          <section className="space-y-8">
            <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center border-b border-[var(--primary)] pb-4">
              <div className="space-y-1">
                <h2 className="text-xl font-black tracking-tight text-[var(--text-primary)] uppercase">Task Database</h2>
                <p className="text-xs font-mono text-[var(--text-secondary)] uppercase tracking-widest">{filteredTodos.length} entries detected</p>
              </div >

              <div className="inline-flex w-fit items-center gap-1 rounded-none border border-[var(--border)] bg-black p-1 shadow-sm">
                {['all', 'active', 'completed'].map((item) => (
                  <button
                    key={item}
                    onClick={() => setFilter(item)}
                    className={`rounded-none px-4 py-1.5 text-xs font-black uppercase transition-all duration-100 ${
                      filter === item
                        ? 'bg-[var(--primary)] text-black shadow-[0_0_10px_var(--primary)]'
                        : 'text-[var(--text-secondary)] hover:bg-[var(--bg-muted)] hover:text-[var(--text-primary)]'
                    }`}
                  >
                    {item}
                  </button>
                ))}
              </div >
            </div >

            {renderTaskList()}
          </section>
        </div >
      </main>

      <ConfirmModal
        open={Boolean(deleteTarget)}
        title="Purge Entry?"
        description="This entry will be permanently deleted from the system. Action is irreversible."
        isLoading={Boolean(deletingId)}
        onCancel={() => setDeleteTarget(null)}
        onConfirm={handleRemove}
      />
    </div >
  );
}
