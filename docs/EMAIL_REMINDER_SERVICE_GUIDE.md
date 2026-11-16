# TodoFlow Email Reminder Service Guide

## 1. Feature overview

A user may give a todo a due date and request an email reminder:

- 1 minute before;
- 1 hour before;
- 1 day before;
- 3 days before; or
- at a custom date and time before the due date.

The selected database stores the complete reminder state. A background
APScheduler job scans due reminders and sends branded email through Resend.

```text
UI selection -> domain validation -> selected database
             -> background scan -> Resend -> mark as sent
```

Only the backend terminal is required for the API and scheduler. APScheduler
runs in a background thread inside the same application process.

## 2. DDD placement

### Domain

`app/domain/reminder.py` contains `ReminderOption` and `ReminderSettings`.
These rules are independent of FastAPI, databases, APScheduler, and Resend:

- a reminder requires a due date;
- the due date must be in the future;
- the calculated reminder must occur before the due date;
- the reminder must still be in the future when the todo is created;
- a custom reminder must be before the due date;
- a sent reminder cannot be marked as sent again.

`app/domain/todo.py` owns todo state and `reminder_is_due()`. Completed todos
are never considered due for notification.

`app/domain/notification.py` defines the provider-neutral `EmailMessage` value
and `EmailSender` port. The domain does not import the Resend SDK.

### Application

`TodoService.create()` coordinates todo creation and asks domain factories to
validate the reminder. `ReminderService.process_due()` coordinates one batch:

1. read due reminders from the repository;
2. recheck the domain rule;
3. build plain-text and HTML messages;
4. call `EmailSender.send()`;
5. mark the reminder sent only after provider success;
6. save the updated todo.

### Presentation

`CreateTodoRequest` validates the HTTP data shape. The thin todo route delegates
to `todo_controller.add_todo`, which creates `CreateTodoInput` using the
authenticated user's UID and email. The client cannot choose another owner.

### Infrastructure

| File | Technical responsibility |
|---|---|
| `reminder_scheduler.py` | Starts, scans, and shuts down APScheduler |
| `resend_email_sender.py` | Converts `EmailMessage` into a Resend request |
| Database todo repositories | Store reminder fields and query due reminders |
| PostgreSQL `todo_schema.py` | Safely creates/migrates reminder columns and index |

## 3. Todo creation flow

The frontend submits fields equivalent to:

```json
{
  "title": "Prepare the presentation",
  "priority": "HIGH",
  "due_at": "2026-11-16T15:00:00.000Z",
  "reminder_option": "1_HOUR",
  "custom_reminder_at": null
}
```

The flow is:

```text
AddTodoForm
 -> todosSlice async thunk
 -> todoApi.create
 -> POST /todos with Bearer JWT
 -> CreateTodoRequest
 -> todo_controller.add_todo
 -> CreateTodoInput
 -> TodoService.create
 -> TodoItem.create
 -> ReminderSettings.create
 -> selected TodoRepository.save
 -> TodoResponse
```

All browser dates are sent as ISO timestamps. The backend normalizes reminder
calculations to UTC so database and scheduler comparisons are consistent.

## 4. Reminder calculation

For a due time `D`, the domain calculates:

| Option | Calculation |
|---|---|
| `NONE` | No reminder timestamp |
| `1_MINUTE` | `D - 1 minute` |
| `1_HOUR` | `D - 1 hour` |
| `1_DAY` | `D - 1 day` |
| `3_DAYS` | `D - 3 days` |
| `CUSTOM` | Use the validated custom timestamp |

Example: if a todo is due at 5:00 PM and `1_HOUR` is selected, `reminder_at`
is 4:00 PM. If the current time is already 4:30 PM, creation is rejected
because that reminder would be in the past.

## 5. Persisted fields

Every database stores the same logical state:

```text
due_at
reminder_at
reminder_email
reminder_sent_at
reminder_option
```

- MongoDB stores these fields in the todo document.
- PostgreSQL stores them in typed `TIMESTAMPTZ`/`TEXT` columns and uses a
  partial index for incomplete, unsent reminders.
- Firestore maps them to REST document fields through `todo_mapper.py`.

Because reminder state is persistent, restarting the API does not lose pending
reminders.

## 6. Scheduler lifecycle

FastAPI's lifespan starts `ReminderScheduler` after application wiring and
shuts it down cleanly during reload or termination.

```text
FastAPI startup
 -> immediate recovery scan
 -> interval job starts
 -> API continues serving requests in the same process
 -> each interval calls ReminderService.process_due()
```

Important scheduler settings:

- `max_instances=1` prevents overlapping scans;
- `coalesce=True` combines missed intervals into one recovery run;
- a misfire grace period tolerates short delays;
- an immediate startup scan recovers reminders that became due during downtime.

This is an application-level scheduled job rather than an operating-system cron
entry. Run one Uvicorn application process for the beginner/local setup. A
production multi-worker deployment requires one dedicated scheduler or a
distributed lock so multiple processes do not scan the same reminders.

## 7. Due reminder send flow

```text
Scheduler interval fires
 -> ReminderService.process_due
 -> repository.get_due_reminders(now, limit)
 -> TodoItem.reminder_is_due(now)
 -> build EmailMessage
 -> ResendEmailSender.send
 -> provider success
 -> ReminderSettings.mark_sent
 -> repository.save
 -> reminder_sent_at persists
```

The query returns only incomplete todos whose reminder is due and not yet sent.
The domain checks again so the business rule remains protected even if another
repository implementation is added later.

## 8. Email content

`ReminderService._build_message()` creates both HTML and plain-text forms. The
HTML email includes TodoFlow branding, an escaped task title, readable due
date, priority badge, and concise callout. Inline CSS is used because email
clients do not consistently support external stylesheets.

User-controlled title text is HTML-escaped before insertion into the template.

## 9. Resend adapter and duplicate protection

`ResendEmailSender` implements the domain `EmailSender` contract. It receives
provider-independent content and maps it to Resend's API.

Each reminder uses a stable idempotency key derived from the reminder event,
todo ID, and reminder timestamp. A short retry therefore refers to the same
email event instead of intentionally creating a duplicate.

Success behavior:

```text
Resend accepts email -> provider ID is logged -> reminder_sent_at is saved
```

Failure behavior:

```text
Resend/network failure -> safe error is logged -> sent state remains empty
                       -> next scheduler scan may retry
```

A completed todo fails the domain due check, and a deleted todo is absent from
the repository query, so neither receives an email.

## 10. Environment configuration

Real values belong only in ignored `backend/DDD/.env`:

```env
RESEND_API_KEY=re_your_key
REMINDER_EMAIL_FROM=TodoFlow <onboarding@resend.dev>
REMINDER_SCAN_INTERVAL_SECONDS=30
REMINDER_BATCH_SIZE=50
```

| Setting | Purpose |
|---|---|
| `RESEND_API_KEY` | Authenticates the provider request |
| `REMINDER_EMAIL_FROM` | Sets the visible sender |
| `REMINDER_SCAN_INTERVAL_SECONDS` | Controls scan frequency |
| `REMINDER_BATCH_SIZE` | Limits work performed by one scan |

`onboarding@resend.dev` is suitable for provider testing. Sending to arbitrary
real recipients requires a verified sender domain in Resend.

## 11. Manual test

```powershell
cd backend\DDD
.\.venv\Scripts\Activate.ps1
python -m uvicorn main:app --reload
```

1. Sign in to TodoFlow.
2. Choose a due time 5–10 minutes in the future.
3. Choose a custom reminder 2–3 minutes in the future but before the due time.
4. Save the todo and verify the displayed schedule.
5. Keep the backend running.
6. At reminder time, inspect the terminal and Resend dashboard/inbox.
7. Verify that `reminder_sent_at` is populated in the selected database.

## 12. Common errors

- **Due date must be in the future:** Choose a due date after the current clock.
- **Reminder must be before the due date:** Move the custom reminder earlier.
- **This reminder falls in the past:** The selected offset is larger than the
  remaining time; choose a later due date or a custom reminder.
- **Provider shows sent but inbox is empty:** Check spam, recipient address,
  Resend delivery logs, and sender-domain verification.
- **Scheduler starts again during reload:** Expected in development; the old
  application shuts down its scheduler and the reloaded process starts a new
  one. Persistent state prevents reminder loss.

## 13. Presentation answer

> The UI sends a due date and reminder choice. The presentation layer validates
> the HTTP shape, the application layer coordinates creation, and the domain
> calculates the UTC reminder time while enforcing all time rules. The active
> database persists the reminder with the todo. FastAPI starts an APScheduler
> background job in the same process. Each scan asks the application service
> for due reminders, sends provider-neutral messages through the Resend adapter,
> and persists `reminder_sent_at` only after success. The same workflow works
> with Firestore, MongoDB, and PostgreSQL because only repository adapters vary.
