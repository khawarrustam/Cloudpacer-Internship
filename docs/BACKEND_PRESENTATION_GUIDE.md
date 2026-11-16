# TodoFlow DDD Backend Presentation Guide

> Primary focus: folder structure, the purpose of every backend file, important
> classes/functions, call direction, and why each responsibility belongs in its
> layer. This guide is designed to answer presentation questions without opening
> every source file.

## 1. Two-minute project explanation

> TodoFlow is a FastAPI backend organized with Domain-Driven Design and Onion
> Architecture. Its four main layers are Presentation, Application, Domain, and
> Infrastructure. Presentation handles HTTP contracts, dependency injection,
> thin routes, and controllers. Application coordinates authentication, todo,
> and reminder use cases. Domain contains framework-independent business rules
> and repository ports. Infrastructure implements security, OAuth, email,
> scheduling, and persistence for Firestore, MongoDB, and PostgreSQL.
>
> `app/main.py` is the composition root. It loads configuration, creates a
> matching auth/todo repository pair for the selected database, injects those
> repositories into services, and connects routers to FastAPI. Therefore a
> database switch changes Infrastructure wiring without changing domain rules,
> application workflows, or public endpoints.

One-line summary:

```text
Presentation receives -> Application coordinates -> Domain decides -> Infrastructure performs
```

Related feature guides:

- [Google Login Integration](GOOGLE_LOGIN_INTEGRATION_GUIDE.md)
- [GitHub Login Integration](GITHUB_LOGIN_INTEGRATION_GUIDE.md)
- [Email Reminder Service](EMAIL_REMINDER_SERVICE_GUIDE.md)

## 2. Folder structure

```text
backend/DDD/
|-- main.py
|-- .env.example
|-- requirements.txt
|-- README.md
|-- ARCHITECTURE.md
`-- app/
    |-- __init__.py
    |-- main.py
    |-- config.py
    |-- logging.py
    |-- domain/
    |   |-- auth.py
    |   |-- todo.py
    |   |-- reminder.py
    |   `-- notification.py
    |-- application/
    |   |-- dto.py
    |   |-- auth_service.py
    |   |-- todo_service.py
    |   `-- reminder_service.py
    |-- presentation/
    |   |-- schemas.py
    |   |-- dependencies.py
    |   |-- controllers/
    |   |   |-- auth_controller.py
    |   |   `-- todo_controller.py
    |   `-- routers/
    |       |-- auth.py
    |       `-- todos.py
    `-- infrastructure/
        |-- security.py
        |-- github_oauth.py
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
            |-- auth_schema.py
            |-- todo_repository.py
            `-- todo_schema.py
```

| Folder | Question it answers |
|---|---|
| `presentation` | How does HTTP enter and leave the application? |
| `application` | In which order should a use case run? |
| `domain` | What is valid business behavior? |
| `infrastructure` | How is the behavior implemented with external technology? |

Only root `app/__init__.py` is retained as an explicit package marker. Nested
folders have no initialization or public export logic, so empty decorative
package files are unnecessary with modern Python namespace-package behavior.

## 3. Dependency direction

```text
presentation -> application -> domain
infrastructure ----------------> domain
app/main.py -> presentation + application + infrastructure
```

Forbidden examples:

| Layer | Must not contain |
|---|---|
| Domain | FastAPI, Pydantic, SQL, PyMongo, Firestore URLs, JWT/Resend SDKs |
| Application | HTTP status codes, database queries, provider SDK calls |
| Presentation | SQL, hashing, OAuth exchange, business decisions |
| Infrastructure | Route decorators, UI response models, use-case policy |

This is Dependency Inversion: high-level workflows depend on domain contracts;
low-level adapters implement those contracts.

## 4. Startup flow

```text
1. Uvicorn imports root main.py.
2. Root main.py imports app.main.app.
3. create_app() loads cached typed settings.
4. FastAPI, CORS, and request logging are created.
5. repository_factory reads DATABASE.
6. Matching auth and todo repositories are created.
7. AuthService and TodoService receive those repositories.
8. ReminderService receives TodoRepository and EmailSender.
9. ReminderScheduler receives ReminderService.
10. Services are stored on app.state.
11. Auth and todo routers are included.
12. FastAPI lifespan starts the background scheduler.
```

## 5. Root and shared files

### `main.py`

Purpose: preserve the simple `python -m uvicorn main:app --reload` command while
the real application lives in the `app` package. It re-exports `app` and
`create_app`; direct execution also reads typed host/port/reload settings.
It contains no business logic.

### `app/__init__.py`

Purpose: explicitly mark the root application package. It has no side effects,
database connections, or dependency wiring.

### `app/main.py`

Purpose: composition root and application ownership boundary.

Important work:

- `create_app()` obtains `Settings` and creates FastAPI;
- installs CORS and request logging;
- calls `create_repositories(settings)`;
- creates application services and external adapters;
- stores request-time services on `app.state`;
- includes routers and a health endpoint;
- defines lifespan startup/shutdown for the scheduler.

It wires business objects but does not implement repository operations or rules.

### `app/config.py`

`Settings(BaseSettings)` declares required typed environment values. Actual
runtime values come from `backend/DDD/.env` or terminal overrides.

Important properties/functions:

| Name | Purpose |
|---|---|
| `selected_database` | Normalizes database name; maps `firebase` to `firestore`; rejects unsupported values |
| `allowed_origins` | Converts comma-separated CORS text to a list |
| `firebase_credential_file` | Resolves relative credential paths from the backend root |
| `get_settings()` | Creates and caches one settings object |

Caching avoids rereading `.env` on every request. A database/configuration
change therefore requires a process restart.

### `app/logging.py`

Purpose: readable request tracing and aligned English/Roman-Urdu step logs.

| Function | Purpose |
|---|---|
| `log_step(area, english, roman_urdu)` | Records an INFO step for one layer |
| `log_error(area, message)` | Records a safe ERROR message |
| `install_request_logging(app)` | Installs request middleware |
| nested `request_logger` | Logs request number, method, path, status, and duration |

`ContextVar` keeps concurrent request numbers from mixing. Tokens and passwords
are never logged.

### `.env.example`, `requirements.txt`, `README.md`, `ARCHITECTURE.md`

- `.env.example` documents required keys with safe placeholders.
- `requirements.txt` makes Python installation reproducible.
- `README.md` provides setup, run, endpoints, and verification commands.
- `ARCHITECTURE.md` records evidence-based placement and file-size rules.

Real `.env` files and service-account secrets are ignored by Git.

## 6. Presentation layer

### `presentation/schemas.py`

Pydantic models describe only public HTTP JSON:

| Schema | Purpose |
|---|---|
| `SignupRequest` | Validates signup email/password/name |
| `LoginRequest` | Validates password-login input |
| `GoogleLoginRequest` | Accepts a Google ID-token credential |
| `GitHubLoginRequest` | Accepts a short-lived GitHub OAuth code |
| `AuthResponse` | Returns UID, email, JWT, and message |
| `CreateTodoRequest` | Validates title, priority, due date, and reminder input |
| `TodoResponse` | Defines the public todo representation |

Pydantic validates transport shape; Domain validates business invariants.

### `presentation/dependencies.py`

Purpose: request-time dependency injection and authentication.

- `get_auth_service()` reads the configured service from `request.app.state`.
- `get_todo_service()` reads the configured todo service.
- `AuthServiceDep`, `TodoServiceDep`, and `CurrentUserDep` keep route signatures
  short using `Annotated[..., Depends(...)]`.
- `current_user()` extracts the Bearer token, calls `AuthService.authenticate`,
  and returns trusted `CurrentUser(uid, email)`.

Todo ownership comes from the verified token, never from a client-supplied UID.

### `presentation/controllers/auth_controller.py`

Maps HTTP schemas to application inputs, calls `AuthService`, maps outputs to
`AuthResponse`, and translates expected `ValidationException` values to safe
HTTP 400/401 responses.

Functions: `signup_user`, `login_user`, `google_login_user`,
`github_login_user`, and shared `_auth_response`.

### `presentation/controllers/todo_controller.py`

Functions: `get_todos`, `add_todo`, `finish_todo`, and `remove_todo`.
It uses `CurrentUser` to build owner-scoped application DTOs. It does not query
a database or decide whether a todo transition is valid.

### `presentation/routers/auth.py`

| Route function | Endpoint | Controller |
|---|---|---|
| `signup` | `POST /auth/signup` | `signup_user` |
| `login` | `POST /auth/login` | `login_user` |
| `login_with_google` | `POST /auth/google` | `google_login_user` |
| `login_with_github` | `POST /auth/github` | `github_login_user` |

### `presentation/routers/todos.py`

| Route function | Endpoint | Controller |
|---|---|---|
| `list_todos` | `GET /todos` | `get_todos` |
| `create_todo` | `POST /todos` | `add_todo` |
| `complete_todo` | `PATCH /todos/{id}/complete` | `finish_todo` |
| `delete_todo` | `DELETE /todos/{id}` | `remove_todo` |

Routers declare HTTP metadata and delegate. Controllers own HTTP mapping.

## 7. Application layer

### `application/dto.py`

Immutable use-case boundary data:

| Input/output | Used by |
|---|---|
| `SignupInput`, `LoginInput` | Password auth workflows |
| `GoogleLoginInput`, `GitHubLoginInput` | Provider auth workflows |
| `AuthOutput` | Standard auth result |
| `CreateTodoInput` | Todo creation |
| `TodoActionInput` | Complete/delete actions |
| `TodoOutput` | API-friendly todo result |

DTOs are separate from Pydantic schemas because an application use case should
not depend on HTTP. They are separate from entities because they carry data but
do not own business behavior.

### `application/auth_service.py`

`AuthService(repository: AuthRepository)` coordinates:

- `signup(data)` -> `repository.signup`;
- `login(data)` -> `repository.login`;
- `login_with_google(data)` -> provider repository method;
- `login_with_github(data)` -> provider repository method;
- `authenticate(token)` -> repository token/live-user verification;
- `_to_output(...)` -> consistent `AuthOutput` mapping.

### `application/todo_service.py`

- `create()` calls `TodoItem.create`, saves, and maps output.
- `list()` retrieves the owner's todos and maps each entity.
- `complete()` loads by ID+owner, calls entity `complete()`, and saves.
- `delete()` verifies owner-scoped existence and deletes.
- `_get_todo_or_fail()` centralizes owner-safe lookup.
- `to_output()` converts an entity into `TodoOutput`.

### `application/reminder_service.py`

`process_due()` reads one due batch, checks `reminder_is_due`, builds a branded
HTML/plain-text `EmailMessage`, sends it through the `EmailSender` port, marks
the reminder sent after success, and persists the entity. `_build_message()`
escapes user title content and creates provider-independent email content.

## 8. Domain layer

### `domain/auth.py`

| Type | Rule/responsibility |
|---|---|
| `ValidationException` | Safe base error crossing outer layers |
| `EmailAddress` | Trim, lowercase, and validate account email |
| `DisplayName` | Normalize a name with safe fallback |
| `PasswordPolicy` | Enforce minimum signup length |
| `GoogleIdentity` | Trusted verified Google data |
| `GoogleAccountPolicy` | Reject subject conflicts; allow safe Gmail/Workspace linking |
| `GitHubIdentity` | Trusted GitHub ID, verified email, and name |
| `GitHubAccountPolicy` | Reject a conflicting GitHub subject |
| `UserData` | Database-independent repository auth result |
| `AuthRepository` | Abstract auth operations required by Application |

### `domain/todo.py`

| Type/method | Rule/responsibility |
|---|---|
| `Priority` | Allowed priority values |
| `TaskTitle` | 3–120 character invariant |
| `TodoItem.create` | Valid initial identity/state |
| `TodoItem.complete` | One-time completion transition |
| `TodoItem.reminder_is_due` | Incomplete, scheduled, unsent, time-due check |
| `TodoRepository` | Abstract save/read/list/due/delete operations |

The entity owns completion because every caller must obey the rule. Placing it
in a route or service would allow another caller to bypass it.

### `domain/reminder.py`

`ReminderOption` defines `NONE`, `1_MINUTE`, `1_HOUR`, `1_DAY`, `3_DAYS`, and
`CUSTOM`. `ReminderSettings.create()` validates due/custom times and calculates
the exact UTC reminder. `mark_sent()` protects one-time sent state.

### `domain/notification.py`

`EmailMessage` validates provider-neutral recipient/content data.
`EmailSender(ABC)` defines the outbound `send(message)` port.

## 9. Shared Infrastructure

### `infrastructure/security.py`

`AuthSecurity` performs technical security work:

| Method | Work |
|---|---|
| `hash_password` | Random salt + PBKDF2-HMAC-SHA256 |
| `password_matches` | Re-derivation + constant-time comparison |
| `verify_google_credential` | Signature, audience, issuer, expiry, and email verification |
| `create_token` | HS256 JWT with UID, email, database, issued/expiry times |
| `read_token` | Signature/claims/expiry/database validation |

### `infrastructure/github_oauth.py`

`GitHubOAuthClient.verify_code()` exchanges a one-time code server-side, reads
the authenticated profile and verified primary email, and returns
`GitHubIdentity`. The Client Secret and temporary access token never reach the
browser or database.

### `infrastructure/repository_factory.py`

`create_repositories(settings)` creates shared security/OAuth dependencies,
selects one database, and returns a matching `(todo_repository,
auth_repository)` pair. Helper functions connect Firestore, MongoDB, or
PostgreSQL. Returning both together prevents mixed storage such as Mongo auth
with PostgreSQL todos.

### `infrastructure/resend_email_sender.py`

`ResendEmailSender.send()` maps `EmailMessage` to the Resend SDK, supplies a
stable idempotency key, and returns the provider message ID.

### `infrastructure/reminder_scheduler.py`

- `start()` performs a recovery scan and starts the interval scheduler;
- `_process_reminders()` invokes one application batch;
- `_log_result()` logs useful non-empty summaries;
- `shutdown()` stops cleanly during FastAPI shutdown/reload.

## 10. Database adapters

### Firestore

`firestore/auth_repository.py` implements signup, password login, Google login,
GitHub login, and live-user token verification through Firestore REST. Email
hashes provide deterministic private document IDs; provider subjects use
structured queries.

`firestore/todo_repository.py` implements owner-scoped CRUD and due-reminder
queries. `firestore/todo_mapper.py` converts domain values to/from Firestore REST
field structures so persistence formatting does not clutter repository flow.

### MongoDB

`mongodb/auth_repository.py` uses a unique email index plus sparse unique
`google_sub` and `github_sub` indexes. It stores PBKDF2 hashes, links verified
providers, and confirms live users after JWT decoding.

`mongodb/todo_repository.py` uses owner indexes, `replace_one(..., upsert=True)`
for create/update persistence, owner-scoped reads/deletes, and due-reminder
filters. Mapping helpers convert documents to domain entities.

### PostgreSQL

`postgresql/auth_repository.py` uses parameterized SQL for signup, login,
provider linking, and live-user verification. `dict_row` makes columns readable.

`postgresql/auth_schema.py` safely creates/migrates the users table and partial
unique indexes for non-null provider subjects.

`postgresql/todo_repository.py` implements owner-scoped CRUD and reminder
queries. `INSERT ... ON CONFLICT (id) DO UPDATE` supports entity persistence.

`postgresql/todo_schema.py` safely creates/migrates todo reminder columns and a
partial index for incomplete, unsent scheduled reminders.

Parameterized values are never concatenated into SQL, reducing injection risk.

## 11. Complete request flows

### Signup

```text
POST /auth/signup -> SignupRequest -> signup_user -> SignupInput
 -> AuthService.signup -> selected AuthRepository.signup
 -> domain email/password/name rules -> hash -> database user
 -> database-bound JWT -> AuthResponse
```

### Password login

```text
POST /auth/login -> LoginRequest -> login_user -> LoginInput
 -> AuthService.login -> repository lookup -> password_matches
 -> database-bound JWT -> AuthResponse
```

### Google login

```text
Google ID token -> POST /auth/google -> GoogleLoginInput
 -> AuthService -> repository -> AuthSecurity verification
 -> GoogleIdentity/GoogleAccountPolicy -> find/link/create local user
 -> TodoFlow JWT
```

### GitHub login

```text
OAuth code + validated state -> POST /auth/github -> GitHubLoginInput
 -> AuthService -> repository -> GitHubOAuthClient code exchange
 -> GitHubIdentity/GitHubAccountPolicy -> find/link/create local user
 -> TodoFlow JWT
```

### Protected todo request

```text
Bearer JWT -> current_user -> AuthService.authenticate
 -> decode DB-bound JWT -> confirm live selected-DB user
 -> trusted CurrentUser -> todo controller/service/repository
```

### Reminder scan

```text
Scheduler -> ReminderService.process_due -> repository due query
 -> domain due check -> EmailSender/Resend -> mark_sent -> repository.save
```

## 12. File-to-file dependency map

```text
app/main.py
 -> config.py
 -> repository_factory.py -> selected database repositories
 -> AuthService / TodoService / ReminderService
 -> ResendEmailSender / ReminderScheduler
 -> routers

auth router -> auth controller -> AuthService -> AuthRepository
                                             -> selected DB adapter

todos router -> todo controller -> TodoService -> TodoItem/TodoRepository

ReminderScheduler -> ReminderService -> TodoRepository + EmailSender
```

## 13. Recommended 15-minute presentation

1. **Architecture overview (2 min):** show the tree and dependency direction.
2. **Startup (2 min):** explain two `main.py` files, settings, and composition.
3. **One todo request (4 min):** trace route -> controller -> service -> entity
   -> repository -> response.
4. **Authentication (3 min):** explain repository contract, DB-bound JWT, and
   Google/GitHub stable subjects.
5. **Three adapters (2 min):** compare how one port is implemented three ways.
6. **Reminders and close (2 min):** explain scheduler, Resend port, persistence,
   and the value of dependency inversion.

## 14. Viva questions and answers

### Why are there two `main.py` files?

Root `main.py` preserves a beginner-friendly command. `app/main.py` is the real
composition root. They have the same filename but different import paths and
responsibilities.

### Why use `config.py` when `.env` exists?

`.env` is raw external text. `config.py` provides typed validation, path
resolution, normalization, discoverable attributes, and cached loading.

### Why are repository interfaces in Domain?

They describe capabilities the core needs without naming a database. Outer
adapters depend inward and implement those capabilities.

### Why use both HTTP schemas and application DTOs?

Schemas are a FastAPI/Pydantic transport contract. DTOs are a framework-neutral
use-case contract. Keeping both prevents HTTP concerns from entering Application.

### Why define `TodoServiceDep = Annotated[...]` in dependencies?

It centralizes FastAPI injection syntax and keeps route parameters readable.
The alias is consumed by router annotations even if it is not called like a
normal function in the same file.

### What does a controller do in this DDD project?

It translates HTTP input into application input, calls a use case, maps output,
and translates expected errors. It contains no business rules or database SQL.

### Why is owner UID absent from create-todo input JSON?

The backend derives owner identity from a verified JWT. Trusting a client UID
would allow one user to create or modify another user's data.

### Why is completion a domain method?

It is a universal business invariant. Keeping it on `TodoItem` prevents every
controller, scheduler, or future use case from implementing it differently.

### Why does one factory return auth and todo repositories?

The project requires both concerns to use the same active database. One factory
branch makes mixed wiring impossible.

### Does Google login use Firebase Authentication?

No. Google Identity Services proves identity. The selected repository stores
the local user, and TodoFlow issues its own JWT.

### What are `google_sub` and `github_sub`?

They are stable provider account identifiers. Emails and usernames can change;
stable subjects prevent identity from depending on mutable display data.

### Why does the same provider account become three users?

Each database is an independent account boundary and creates its own local UID.
Repositories never search another database.

### Why is a GitHub Client Secret backend-only?

Browser code is public. The backend uses the secret for code exchange and never
sends it to React. Google uses a different ID-token flow here and requires only
the public Web Client ID.

### Why is JWT easier for this project?

After any login method succeeds, every protected request uses one standard
Bearer token flow. The JWT is still checked against the live selected-database
user and includes the database claim.

### Why persist reminders instead of keeping them in scheduler memory?

Persistent state survives restarts and database tools can inspect it. The
scheduler is only a trigger; the database is the source of truth.

## 15. Final answer formula

For any presentation question, answer in this order:

```text
What does it do?
When is it used?
How does it work?
Why does it belong in this layer/file?
Which file/function calls it next?
```

This formula demonstrates both code knowledge and architectural reasoning.
