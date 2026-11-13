# TodoFlow DDD Backend

A beginner-readable FastAPI backend with professional DDD boundaries. The same
selected database stores both accounts and todos.

The evidence, placement rules, and restructuring prompt are recorded in
[`ARCHITECTURE.md`](ARCHITECTURE.md).

For a complete file-by-file explanation, request flows, demo plan, limitations,
and viva preparation, read
[`BACKEND_PRESENTATION_GUIDE.md`](../../docs/BACKEND_PRESENTATION_GUIDE.md).

## Structure

```text
backend/DDD/
|-- main.py                    Beginner-compatible Uvicorn entrypoint
|-- app/
|   |-- main.py                Composition root and FastAPI app
|   |-- config.py              Typed environment settings
|   |-- logging.py             Bilingual request flow logs
|   |-- domain/                Todo/auth/reminder rules and ports
|   |-- application/           Auth, todo, and reminder use cases
|   |-- infrastructure/        Database/security/Resend implementations
|   `-- presentation/          Thin routes, controllers, dependencies, schemas
|-- ARCHITECTURE.md            Research and layer placement contract
|-- requirements.txt
`-- .env.example
```

Detailed adapter modules remain small and explicit:

```text
app/infrastructure/
|-- security.py
|-- repository_factory.py
|-- resend_email_sender.py
|-- reminder_scheduler.py
|-- firestore/
|   |-- auth_repository.py
|   |-- todo_repository.py
|   `-- todo_mapper.py
|-- mongodb/
|   |-- auth_repository.py
|   `-- todo_repository.py
`-- postgresql/
    |-- auth_repository.py
    |-- todo_repository.py
    `-- todo_schema.py
```

HTTP endpoints remain thin under `presentation/routers/`. Request mapping,
service calls, and HTTP error translation live in focused
`presentation/controllers/` modules.

## Dependency direction

```text
routers -> controllers -> application -> domain
infrastructure -------------> domain
app/main.py -> all outer layers for dependency wiring
```

- Domain contains no FastAPI, Pydantic, or database-driver imports.
- Application coordinates workflows without HTTP or database queries.
- Infrastructure implements repository contracts for external databases.
- Presentation handles HTTP validation, dependencies, and status codes.
- `app/main.py` is the API composition root that chooses concrete adapters.
- Infrastructure `ReminderScheduler` runs beside the API in one background
  thread and calls the application reminder use case.

## Install

```powershell
cd backend\DDD
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set every listed variable. `Settings` contains
types only—runtime values and safe local choices all come from `.env` or
terminal environment overrides. Inactive database fields may retain safe
local/sample values. Keep `AUTH_TOKEN_SECRET` private. Set `GOOGLE_CLIENT_ID`
to the Web OAuth client ID also used by `frontend/.env`; a client secret is not
used for this Google Identity Services flow.

For reminders, add a Resend API key and sender to `.env`:

```env
RESEND_API_KEY=re_your_key
REMINDER_EMAIL_FROM=TodoFlow <reminders@your-verified-domain.com>
REMINDER_SCAN_INTERVAL_SECONDS=30
REMINDER_BATCH_SIZE=50
```

## Select a database

Stop the backend before switching, then run one option:

```powershell
$env:DATABASE = "firestore"
python -m uvicorn main:app --reload

$env:DATABASE = "mongodb"
python -m uvicorn main:app --reload

$env:DATABASE = "postgresql"
python -m uvicorn main:app --reload
```

The command remains simple because root `main.py` delegates to the professional
`app.main` composition root.

## Email reminders

The UI supports no reminder, 1 minute, 1 hour, 1 day, 3 days, or a custom time
before the todo due date. Exact UTC reminder state is saved in the same selected
database as the todo.

Only one backend terminal is needed. FastAPI lifespan starts and stops the
background scheduler automatically:

```powershell
python -m uvicorn main:app --reload
```

The scheduler scans persistent reminders on an interval and sends through Resend.
The selected database—not scheduler memory—is the reminder source of truth, so
a restart does not lose reminders. After provider success the scheduler saves
`reminder_sent_at`; a stable Resend idempotency key makes short retries safe.
Completed or deleted todos are not emailed. This beginner setup should run one
Uvicorn application process; production multi-worker deployment needs one
dedicated scheduler or a distributed lock.

## Database-specific accounts

Firestore, MongoDB, and PostgreSQL accounts are independent. The same email may
sign up in all three databases and receives a different UID in each database.
A token issued for one database is rejected after switching to another.
Tokens are standard three-part HS256 JWTs created and verified with PyJWT.

Google login follows the same isolation rule. The backend verifies Google's ID
token and stable `sub`, then finds or creates a local user only in the active
database. Therefore the same Google account receives three different local UIDs
when first used in Firestore, MongoDB, and PostgreSQL. An existing same-email
password account in one database is linked only inside that database when
Google is authoritative for the email (Gmail or Google Workspace).

- Firestore accounts: `auth_users` collection
- MongoDB accounts: `users` collection
- PostgreSQL accounts: `users` table

Passwords are stored as salted PBKDF2 hashes, never plain text.

## Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | Health check and active database |
| `POST` | `/auth/signup` | Create account in active database |
| `POST` | `/auth/login` | Login from active database |
| `POST` | `/auth/google` | Verify Google and login/create in active database |
| `GET` | `/todos` | List current user's todos |
| `POST` | `/todos` | Create todo with optional due date/reminder |
| `PATCH` | `/todos/{id}/complete` | Complete todo |
| `DELETE` | `/todos/{id}` | Delete todo |

## URLs

- API: <http://127.0.0.1:8000>
- Swagger: <http://127.0.0.1:8000/docs>
- ReDoc: <http://127.0.0.1:8000/redoc>

## Verify the backend

```powershell
.\.venv\Scripts\python.exe -m compileall -q app main.py
.\.venv\Scripts\python.exe -m pip check
```

## Logs and comments

Request logs still show Presentation, Auth, Application, and Infrastructure in
English plus Roman Urdu. Public boundary functions use concise What/When/How
docstrings so the reason and layer responsibility stay aligned with the code.

For the complete frontend-to-database Google flow, read
[`docs/GOOGLE_LOGIN_INTEGRATION_GUIDE.md`](../../docs/GOOGLE_LOGIN_INTEGRATION_GUIDE.md).
