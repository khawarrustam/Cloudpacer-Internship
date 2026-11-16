# TodoFlow Architecture: DDD/Onion and MVC

This workspace contains one TodoFlow product implemented with two architectural
styles:

- `backend/DDD`: FastAPI with Domain-Driven Design and Onion boundaries;
- `backend/MVC`: the earlier Model-View-Controller implementation.

Both implement todo workflows. The DDD backend additionally supports switching
authentication and todo persistence together among Firestore, MongoDB, and
PostgreSQL.

## 1. The DDD mental model

Domain-Driven Design organizes software around business concepts and rules,
not around a framework or database.

A database-first design asks: “How do I insert a todo document?” A domain-first
design asks: “What makes a valid todo, and which state changes are allowed?”

TodoFlow domain examples:

- a title must contain 3–120 characters;
- priority is `LOW`, `MEDIUM`, or `HIGH`;
- every todo has an owner;
- a completed todo cannot be completed twice;
- reminder dates must be valid relative to the due date and current time;
- provider-account conflicts must not silently take over an existing user.

These rules remain valid regardless of whether persistence uses Firestore,
MongoDB, or PostgreSQL.

## 2. Onion Architecture and dependency direction

```text
                       Presentation
                 HTTP routes/controllers/schemas
                              |
                              v
                        Application
                      use-case workflow
                              |
                              v
                           Domain
               entities, values, rules, ports

Infrastructure implements Domain ports and is wired at the outer boundary.
```

The rule is:

```text
presentation -> application -> domain
infrastructure ----------------> domain
app/main.py -> all outer layers for composition
```

Inner layers never import outer layers. Therefore:

- Domain imports no FastAPI, Pydantic, database driver, Resend, or OAuth SDK.
- Application uses domain contracts without knowing the selected database.
- Infrastructure implements ports using external technologies.
- Presentation converts HTTP input/output and delegates use cases.
- The composition root selects and connects concrete objects.

## 3. Complete create-todo flow

```text
React sends POST /todos with Bearer JWT
 -> FastAPI validates CreateTodoRequest
 -> current_user verifies the JWT through AuthService
 -> todos router calls todo_controller.add_todo
 -> controller creates CreateTodoInput
 -> TodoService.create coordinates the use case
 -> TodoItem.create enforces domain rules
 -> ReminderSettings.create validates/calculates reminder state
 -> selected TodoRepository.save persists the entity
 -> TodoOutput becomes TodoResponse
 -> HTTP 201 is returned
```

No route contains SQL, MongoDB queries, or Firestore REST code.

## 4. DDD concepts mapped to TodoFlow

| Concept | Meaning | TodoFlow example |
|---|---|---|
| Entity/Aggregate | Identity plus protected state transitions | `TodoItem` |
| Value Object | Valid immutable value | `TaskTitle`, `EmailAddress`, `ReminderSettings` |
| Domain Policy | Decision spanning identity/state values | `GoogleAccountPolicy`, `GitHubAccountPolicy` |
| Repository Port | Storage capability required by the domain/application | `TodoRepository`, `AuthRepository` |
| Application Service | Coordinates one use case | `TodoService`, `AuthService`, `ReminderService` |
| DTO | Data crossing an application boundary | `CreateTodoInput`, `AuthOutput` |
| Adapter | Concrete implementation of a port | Firestore/MongoDB/PostgreSQL repositories |
| Composition Root | Creates and wires concrete dependencies | `app/main.py` |

## 5. Domain layer

Location: `backend/DDD/app/domain/`

### `todo.py`

- `TaskTitle` normalizes and validates title length.
- `Priority` restricts accepted priorities.
- `TodoItem.create()` creates valid initial state.
- `TodoItem.complete()` enforces one-time completion.
- `TodoItem.reminder_is_due()` protects reminder eligibility.
- `TodoRepository` defines persistence operations without implementation.

Once a `TaskTitle` exists, callers know it is valid. Once `TodoItem.complete()`
succeeds, the entity itself guarantees the completion invariant rather than
relying on every controller to remember the rule.

### `auth.py`

- `EmailAddress`, `DisplayName`, and `PasswordPolicy` validate account values.
- `GoogleIdentity` and `GitHubIdentity` represent verified provider data.
- provider policies reject conflicting stable account subjects;
- `UserData` is the repository result shape;
- `AuthRepository` defines signup, login, provider login, and authentication.

Hashing, token verification, and OAuth HTTP calls are not domain rules, so they
remain in Infrastructure.

### `reminder.py` and `notification.py`

- `ReminderSettings` validates and calculates schedules.
- `EmailMessage` is provider-independent notification content.
- `EmailSender` is the outbound email port implemented by Resend.

## 6. Application layer

Location: `backend/DDD/app/application/`

Application services define workflow order but do not contain HTTP responses or
database queries.

- `AuthService`: signup, password login, Google login, GitHub login, JWT check.
- `TodoService`: create, list, complete, and delete owner-scoped todos.
- `ReminderService`: find a due batch, send email, and persist success.
- `dto.py`: immutable inputs/outputs shared with Presentation.

Example:

```text
TodoService.complete
 -> repository.get_by_id(todo_id, owner_uid)
 -> TodoItem.complete()
 -> repository.save(todo)
 -> TodoOutput
```

The service knows the required steps but not whether the repository speaks SQL,
MongoDB, or Firestore REST.

## 7. Infrastructure layer

Location: `backend/DDD/app/infrastructure/`

### Shared adapters

| File | Responsibility |
|---|---|
| `security.py` | PBKDF2 password hashes, Google token verification, DB-bound JWTs |
| `github_oauth.py` | GitHub code exchange and verified profile retrieval |
| `repository_factory.py` | Builds a matching auth/todo repository pair |
| `resend_email_sender.py` | Implements `EmailSender` with Resend |
| `reminder_scheduler.py` | Runs APScheduler beside FastAPI |

### Persistence adapters

- Firestore repositories use an authorized REST session and explicit mappers.
- MongoDB repositories use PyMongo collections and unique/owner indexes.
- PostgreSQL repositories use Psycopg parameterized SQL and focused schema
  modules for safe table creation/migration.

Every database implements the same domain contracts. Switching `DATABASE`
changes the adapter pair without changing Domain, Application, or routes.

Authentication and todos always use the same selected database. JWT payloads
contain the database name, so a token from one database is rejected after a
switch.

## 8. Presentation layer

Location: `backend/DDD/app/presentation/`

- `schemas.py` defines Pydantic HTTP request/response models.
- `dependencies.py` injects services and verifies Bearer tokens.
- controllers map schemas to application DTOs and translate safe exceptions.
- routers declare URLs, HTTP methods, response models, and dependencies.

The controller exists so a route stays declarative:

```text
route: URL + method + response type + dependency
controller: HTTP mapping + service call + error translation
application: workflow
domain: business decision
infrastructure: technical implementation
```

## 9. Composition root and startup

Root `backend/DDD/main.py` is a beginner-compatible Uvicorn entrypoint.
`backend/DDD/app/main.py` is the real composition root.

Startup sequence:

```text
1. Load typed Settings from .env/environment.
2. Create FastAPI and middleware.
3. repository_factory reads DATABASE.
4. Build matching auth and todo repositories.
5. Inject them into AuthService and TodoService.
6. Build ReminderService, Resend adapter, and scheduler.
7. Store services in app.state for dependencies.
8. Include auth and todo routers.
9. FastAPI lifespan starts the reminder scheduler.
```

Centralized wiring makes object ownership and database selection explicit.

## 10. MVC comparison

Traditional MVC groups code as Model, View, and Controller. It is effective for
small CRUD systems, but controllers can gradually absorb validation, workflow,
authentication, and database operations.

| Concern | DDD/Onion backend | Traditional MVC backend |
|---|---|---|
| Business rules | Protected in domain values/entities | Often helper/controller checks |
| Database access | Repository adapters behind ports | Controller/model tied to Firestore |
| Workflow | Application services | Controller |
| HTTP mapping | Thin routers/controllers | Controller |
| Database switching | Replace factory-selected adapter | Rewrite concrete persistence calls |
| Unit testing | Domain/services can use fakes | Often requires framework/database setup |
| Initial file count | Higher | Lower |
| Best fit | Growing rule-heavy systems | Small and stable CRUD applications |

## 11. SOLID principles

| Principle | Application in TodoFlow DDD |
|---|---|
| Single Responsibility | Each layer answers one kind of question |
| Open/Closed | New adapters extend persistence without rewriting domain rules |
| Liskov Substitution | All repositories can replace the matching port |
| Interface Segregation | Ports expose only operations used by the application |
| Dependency Inversion | High-level use cases depend on abstractions, not drivers |

## 12. Authentication architecture

Password, Google, and GitHub methods all end with a local user and TodoFlow JWT:

```text
provider/password proof
 -> selected AuthRepository
 -> active-database user
 -> AuthSecurity.create_token
 -> JWT containing uid, email, database, iat, exp
```

Provider stable IDs (`google_sub`, `github_sub`) are preferred over mutable
display names. Verified matching emails may link login methods inside one
database according to domain policy. The same provider account still receives
separate local UIDs across the three databases.

## 13. Reminder architecture

```text
Todo reminder state in selected DB
 -> APScheduler interval
 -> ReminderService
 -> EmailSender port
 -> Resend adapter
 -> mark reminder_sent_at after success
```

Persistent state enables restart recovery. A stable idempotency key protects
short provider retries. Local development should use one Uvicorn process;
multi-process production requires one scheduler leader or distributed lock.

## 14. Choosing an architecture

Choose simple MVC when the application is small, rules are minimal, persistence
will not change, and rapid delivery matters more than long-term isolation.

Choose DDD/Onion when business invariants are important, multiple adapters are
required, workflows are growing, core logic needs isolated tests, or the system
will be maintained by a team over time.

DDD is not automatically superior. Its extra boundaries are valuable only when
the problem justifies them.

## 15. Run the projects

DDD backend:

```powershell
cd backend\DDD
.\.venv\Scripts\Activate.ps1
$env:DATABASE = "postgresql"  # firestore, mongodb, or postgresql
python -m uvicorn main:app --reload
```

MVC backend:

```powershell
cd backend\MVC
.\.venv\Scripts\Activate.ps1
python -m uvicorn main:app --reload --port 8001
```

DDD Swagger: `http://127.0.0.1:8000/docs`

MVC Swagger: `http://127.0.0.1:8001/docs`
