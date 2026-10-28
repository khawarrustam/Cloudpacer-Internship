import React, { useState } from 'react';
import Button from '../ui/Button';
import Input from '../ui/Input';

function validateTitle(title) {
  if (title.length < 3) return 'Use at least 3 characters.';
  if (title.length > 120) return 'Use no more than 120 characters.';
  return null;
}

export default function AddTodoForm({ creating, onAdd }) {
  // Input values sirf is form ko chahiye, is liye local component state use hoti hai.
  const [title, setTitle] = useState('');
  const [priority, setPriority] = useState('medium');
  const [error, setError] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();

    // Backend call se pehle title clean aur validate hota hai.
    const cleanTitle = title.trim();
    const validationError = validateTitle(cleanTitle);

    if (validationError) {
      setError(validationError);
      return;
    }

    try {
      // Parent dashboard onAdd ke andar Redux createTodo thunk dispatch karta hai.
      await onAdd({ title: cleanTitle, priority });
      setTitle('');
      setError(null);
    } catch (requestError) {
      setError(requestError);
    }
  };

  return (
    <section className="rounded-2xl border border-[var(--border)] bg-white p-5 shadow-[var(--shadow-sm)]">
      <h3 className="font-extrabold">Add task</h3>

      <form onSubmit={handleSubmit} className="mt-4 space-y-4">
        <Input
          id="new-task-title"
          label="Title"
          placeholder="What needs to be done?"
          value={title}
          maxLength={120}
          onChange={(event) => {
            setTitle(event.target.value);
            setError(null);
          }}
          error={error}
        />

        <label className="block text-xs font-bold">
          Priority
          <select
            value={priority}
            onChange={(event) => setPriority(event.target.value)}
            className="mt-2 h-11 w-full rounded-xl border border-[var(--border)] bg-white px-3 text-sm"
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </label>

        <Button type="submit" className="w-full" isLoading={creating}>
          Add task
        </Button>
      </form>
    </section>
  );
}
