import { useState } from 'react';
import { BellRing, CalendarClock, MailCheck } from 'lucide-react';
import Button from '../ui/Button';
import Input from '../ui/Input';

const REMINDER_OPTIONS = [
  ['NONE', 'No reminder'],
  ['1_MINUTE', '1 minute before'],
  ['1_HOUR', '1 hour before'],
  ['1_DAY', '1 day before'],
  ['3_DAYS', '3 days before'],
  ['CUSTOM', 'Custom time'],
];

const REMINDER_OFFSETS = {
  '1_MINUTE': 60 * 1000,
  '1_HOUR': 60 * 60 * 1000,
  '1_DAY': 24 * 60 * 60 * 1000,
  '3_DAYS': 3 * 24 * 60 * 60 * 1000,
};

function validateTitle(title) {
  // English: Client validation gives quick feedback before an API request is sent.
  // Roman Urdu: Client validation API request se pehle foran feedback deti hai.
  if (title.length < 3) return 'Use at least 3 characters.';
  if (title.length > 120) return 'Use no more than 120 characters.';
  return null;
}

function getReminderDate(dueAt, option, customReminderAt) {
  if (!dueAt || option === 'NONE') return null;
  if (option === 'CUSTOM') {
    return customReminderAt ? new Date(customReminderAt) : null;
  }
  return new Date(new Date(dueAt).getTime() - REMINDER_OFFSETS[option]);
}

function formatReminderPreview(date) {
  if (!date || Number.isNaN(date.getTime())) return null;
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date);
}

export default function AddTodoForm({ creating, onAdd }) {
  // English: Only this form needs these input values, so they use local state.
  // Roman Urdu: Input values sirf is form ko chahiye, is liye local state use hoti hai.
  const [title, setTitle] = useState('');
  const [priority, setPriority] = useState('medium');
  const [dueAt, setDueAt] = useState('');
  const [reminderOption, setReminderOption] = useState('NONE');
  const [customReminderAt, setCustomReminderAt] = useState('');
  const [errors, setErrors] = useState({});

  const reminderDate = getReminderDate(
    dueAt,
    reminderOption,
    customReminderAt,
  );
  const reminderPreview = formatReminderPreview(reminderDate);
  const reminderPreviewIsValid = Boolean(
    reminderDate
    && reminderDate > new Date()
    && (!dueAt || reminderDate < new Date(dueAt)),
  );

  const handleSubmit = async (event) => {
    event.preventDefault();

    // English: Trim and validate the title before calling the parent function.
    // Roman Urdu: Parent function call karne se pehle title clean aur validate hota hai.
    const cleanTitle = title.trim();
    const nextErrors = {};
    const titleError = validateTitle(cleanTitle);
    const currentTime = new Date();

    if (titleError) nextErrors.title = titleError;
    if (dueAt && new Date(dueAt) <= currentTime) {
      nextErrors.dueAt = 'Due date must be in the future.';
    }
    if (reminderOption !== 'NONE' && !dueAt) {
      nextErrors.reminder = 'Select a due date before adding a reminder.';
    }
    if (reminderOption === 'CUSTOM' && !customReminderAt) {
      nextErrors.customReminder = 'Select a custom reminder date and time.';
    } else if (reminderDate && reminderDate <= currentTime) {
      nextErrors.customReminder = reminderOption === 'CUSTOM'
        ? 'Reminder time must be in the future.'
        : 'This reminder falls in the past. Choose a later due date.';
    } else if (reminderDate && dueAt && reminderDate >= new Date(dueAt)) {
      nextErrors.customReminder = 'Reminder must be before the due date.';
    }

    if (Object.keys(nextErrors).length > 0) {
      setErrors(nextErrors);
      return;
    }

    try {
      // English: The parent onAdd function dispatches the Redux createTodo thunk.
      // Roman Urdu: Parent ka onAdd Redux createTodo thunk dispatch karta hai.
      await onAdd({
        title: cleanTitle,
        priority,
        due_at: dueAt ? new Date(dueAt).toISOString() : null,
        reminder_option: reminderOption,
        custom_reminder_at: customReminderAt
          ? new Date(customReminderAt).toISOString()
          : null,
      });
      setTitle('');
      setDueAt('');
      setReminderOption('NONE');
      setCustomReminderAt('');
      setErrors({});
    } catch (requestError) {
      setErrors({
        submit: requestError?.message || String(requestError),
      });
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
            setErrors({});
          }}
          error={errors.title}
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

        <label className="block text-xs font-bold">
          Due date and time (optional)
          <input
            type="datetime-local"
            value={dueAt}
            onChange={(event) => {
              const value = event.target.value;
              setDueAt(value);
              if (!value) {
                setReminderOption('NONE');
                setCustomReminderAt('');
              }
              setErrors({});
            }}
            aria-invalid={Boolean(errors.dueAt)}
            className={`mt-2 h-11 w-full rounded-xl border bg-white px-3 text-sm transition focus:ring-4 focus:ring-blue-500/10 ${
              errors.dueAt
                ? 'border-red-400 focus:border-red-500'
                : 'border-[var(--border)] focus:border-[var(--primary)]'
            }`}
          />
          {errors.dueAt && (
            <span className="mt-2 block text-xs font-semibold text-[var(--danger)]">
              {errors.dueAt}
            </span>
          )}
        </label>

        <div className="rounded-2xl border border-blue-100 bg-gradient-to-br from-blue-50/80 to-white p-4">
          <div className="flex items-start gap-3">
            <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-blue-600 text-white shadow-sm">
              <BellRing className="h-5 w-5" aria-hidden="true" />
            </span>
            <div>
              <p className="text-sm font-extrabold">Email reminder</p>
              <p className="mt-1 text-xs leading-5 text-[var(--text-secondary)]">
                Get a reminder email before this task is due.
              </p>
            </div>
          </div>

          <div className="mt-4 space-y-3">
            <label className="block text-xs font-bold" htmlFor="reminder-option">
              Remind me
            </label>
            <select
              id="reminder-option"
              value={reminderOption}
              disabled={!dueAt}
              onChange={(event) => {
                setReminderOption(event.target.value);
                if (event.target.value !== 'CUSTOM') setCustomReminderAt('');
                setErrors({});
              }}
              className="h-11 w-full rounded-xl border border-blue-200 bg-white px-3 text-sm font-semibold text-[var(--text-primary)] transition focus:border-[var(--primary)] focus:ring-4 focus:ring-blue-500/10 disabled:cursor-not-allowed disabled:bg-stone-100 disabled:text-[var(--text-muted)]"
            >
              {REMINDER_OPTIONS.map(([value, label]) => (
                <option key={value} value={value}>{label}</option>
              ))}
            </select>

            {!dueAt && (
              <p className="flex items-center gap-2 rounded-xl bg-white/80 px-3 py-2 text-xs text-[var(--text-secondary)]">
                <CalendarClock className="h-4 w-4 text-blue-600" aria-hidden="true" />
                Add a due date to enable email reminders.
              </p>
            )}

            {reminderOption === 'CUSTOM' && (
              <label className="block text-xs font-bold">
                Reminder date and time
                <input
                  type="datetime-local"
                  value={customReminderAt}
                  onChange={(event) => {
                    setCustomReminderAt(event.target.value);
                    setErrors({});
                  }}
                  aria-invalid={Boolean(errors.customReminder)}
                  className={`mt-2 h-11 w-full rounded-xl border bg-white px-3 text-sm transition focus:ring-4 focus:ring-blue-500/10 ${
                    errors.customReminder
                      ? 'border-red-400 focus:border-red-500'
                      : 'border-blue-200 focus:border-[var(--primary)]'
                  }`}
                />
              </label>
            )}

            {(errors.reminder || errors.customReminder) && (
              <p className="text-xs font-semibold text-[var(--danger)]">
                {errors.reminder || errors.customReminder}
              </p>
            )}

            {reminderOption !== 'NONE'
              && reminderPreview
              && reminderPreviewIsValid
              && !errors.customReminder && (
              <div className="flex items-start gap-2 rounded-xl border border-emerald-100 bg-emerald-50 px-3 py-2.5 text-emerald-800">
                <MailCheck className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
                <div>
                  <p className="text-xs font-bold">Email scheduled</p>
                  <p className="mt-0.5 text-xs">{reminderPreview}</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {errors.submit && (
          <p className="rounded-xl bg-red-50 px-3 py-2 text-xs font-semibold text-[var(--danger)]">
            {errors.submit}
          </p>
        )}

        <Button type="submit" className="w-full" isLoading={creating}>
          Add task
        </Button>
      </form>
    </section>
  );
}
