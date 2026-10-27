import React, { useState } from 'react';
import { Plus } from 'lucide-react';
import Button from '../ui/Button';
import Card from '../ui/Card';
import Input from '../ui/Input';

const PRIORITIES = [
  { value: 'low', label: 'Low', dot: 'bg-green-500' },
  { value: 'medium', label: 'Medium', dot: 'bg-amber-500' },
  { value: 'high', label: 'High', dot: 'bg-red-500' },
];

function validateTitle(title) {
  if (title.length < 3) return 'Use at least 3 characters so the task is clear.';
  if (title.length > 120) return 'Keep the task under 120 characters.';
  return null;
}

export default function AddTodoForm({ creating, onAdd }) {
  const [title, setTitle] = useState('');
  const [priority, setPriority] = useState('medium');
  const [error, setError] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();
    const cleanTitle = title.trim();
    const validationError = validateTitle(cleanTitle);

    if (validationError) {
      setError(validationError);
      return;
    }

    try {
      await onAdd({ title: cleanTitle, priority });
      setTitle('');
      setError(null);
    } catch (requestError) {
      setError(requestError);
    }
  };

  return (
    <Card
      className="new-task-card"
      title="Add a new task"
      subtitle="Capture it now. Refine it later."
      action={(
        <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-[var(--primary-soft)] text-[var(--primary)]">
          <Plus className="h-4 w-4" />
        </span>
      )}
    >
      <form onSubmit={handleSubmit} className="space-y-5">
        <Input
          id="new-task-title"
          label="What needs doing?"
          placeholder="e.g. Review the project brief"
          value={title}
          maxLength={121}
          onChange={(event) => {
            setTitle(event.target.value);
            if (error) setError(null);
          }}
          error={error}
        />

        <div>
          <div className="mb-2 flex items-center justify-between">
            <label className="text-xs font-bold">Priority</label>
            <span className="font-mono text-[9px] text-[var(--text-muted)]">{title.length}/120</span>
          </div>
          <div className="grid grid-cols-3 gap-2">
            {PRIORITIES.map((item) => (
              <button
                key={item.value}
                type="button"
                onClick={() => setPriority(item.value)}
                aria-pressed={priority === item.value}
                className={[
                  'flex h-10 items-center justify-center gap-2 rounded-xl border text-[11px] font-bold transition',
                  priority === item.value
                    ? 'border-[var(--primary)] bg-[var(--primary-soft)] text-[var(--primary)]'
                    : 'border-[var(--border)] bg-white text-[var(--text-secondary)] hover:border-[var(--border-strong)]',
                ].join(' ')}
              >
                <span className={['h-2 w-2 rounded-full', item.dot].join(' ')} />
                {item.label}
              </button>
            ))}
          </div>
        </div>

        <Button type="submit" size="lg" className="w-full" isLoading={creating}>
          <Plus className="h-4 w-4" />
          Add to my list
        </Button>
      </form>
    </Card>
  );
}
