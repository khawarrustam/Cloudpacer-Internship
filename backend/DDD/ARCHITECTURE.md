# TodoFlow DDD Structure — Research, Rules, and Implementation Prompt

This document is the evidence-based contract for the backend structure. Code
must not be moved between layers unless the placement rules below support it.

## 1. Research evidence

1. [FastAPI: Bigger Applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
   recommends a Python `app` package, small router modules, a dependencies
   module, and a simple main module that includes routers.
2. [FastAPI: Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
   documents dependency injection for shared services, authentication, and
   database-related resources. This supports request-time service injection
   instead of mutable route globals.
3. [FastAPI: Settings and Environment Variables](https://fastapi.tiangolo.com/advanced/settings/)
   recommends typed Pydantic settings in a separate config module and loading
   secrets/configuration from environment variables or `.env`.
4. [Microsoft: Designing a DDD-oriented service](https://learn.microsoft.com/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/ddd-oriented-microservice)
   defines the domain layer as business concepts/rules with no persistence
   details, the application layer as use-case coordination without business
   state, and infrastructure as the implementation of persistence details.
5. [Python Packaging Guide: src vs flat layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)
   explains that a `src` layout normally requires installing the project before
   imports work. TodoFlow is a small application run directly with Uvicorn, so
   the official FastAPI-style `app/` package keeps the beginner command simple.
6. [Python packages documentation](https://docs.python.org/3/tutorial/modules.html#packages)
   explains that `__init__.py` marks a regular package. TodoFlow keeps it only
   at the root `app` boundary; nested folders use Python 3 namespace-package
   behavior because they contain no package initialization or public exports.
7. [APScheduler user guide](https://apscheduler.readthedocs.io/en/3.x/userguide.html)
   documents `BackgroundScheduler` for work beside an existing application,
   plus `max_instances`, coalescing, misfire handling and clean shutdown.
8. [Resend idempotency keys](https://resend.com/changelog/idempotency-keys)
   documents safe duplicate protection for retried email requests. TodoFlow
   uses a stable key made from reminder event, todo ID, and reminder timestamp.

## 2. Placement rules

| Layer/module | What belongs here | What must not be here |
|---|---|---|
| `domain/` | Todo/auth/reminder rules, email/repository ports, value objects and business errors | FastAPI, Pydantic HTTP schemas, Resend/JWT SDKs, database drivers, environment variables |
| `application/` | Input/output DTOs and auth/todo/reminder use cases | HTTP status codes, database queries, Resend SDK, environment reads |
| `infrastructure/` | Repository adapters, schema/mappers, hashing, Google/JWT, Resend and scheduler adapters | HTTP routes, UI response models, business decisions |
| `presentation/` | Pydantic schemas, dependencies, thin routes, controllers and HTTP error mapping | SQL, PyMongo, Firestore URLs, hashing, email provider calls |
| `config.py` | Typed environment settings and selected-database normalization | Repository creation, API routes, business rules |
| `logging.py` | Existing request and bilingual step logging | Domain decisions or persistence logic |
| `app/main.py` | Composition root: create FastAPI, wire repositories/services, middleware, routers, health endpoint | Database CRUD implementation or business rules |
| root `main.py` | Backward-compatible beginner entrypoint | Application logic |

## 3. File-size and simplicity rule

The project-specific target is approximately **180 lines or fewer per code
module**. This is not a blind hard limit: a file is split only when it has a
second clear responsibility. Database auth and todo persistence implement two
different repository contracts, so they use separate modules. Tiny one-function
files and a generic `utils.py` are deliberately avoided.

Comments use this aligned meaning:

- **What:** what the class/function does.
- **When:** when the application calls it.
- **How:** the short mechanism or reason needed to understand it.

Comments must explain decisions and boundaries, not repeat obvious Python
syntax. Existing English/Roman Urdu logs remain intact.

## 4. Target structure

```text
backend/DDD/
|-- main.py                       # Beginner-compatible entrypoint
|-- ARCHITECTURE.md               # This evidence and placement contract
|-- app/
|   |-- main.py                   # FastAPI composition root
|   |-- config.py                 # Typed .env settings
|   |-- logging.py                # Existing bilingual request logs
|   |-- domain/
|   |   |-- auth.py               # Auth rules/contracts
|   |   |-- reminder.py           # Reminder date rules/value object
|   |   |-- notification.py       # Email message + sender port
|   |   `-- todo.py               # Todo entity/repository contract
|   |-- application/
|   |   |-- dto.py                # Use-case boundary data
|   |   |-- auth_service.py       # Signup/password/Google/token use cases
|   |   |-- todo_service.py       # Todo use cases
|   |   `-- reminder_service.py   # Due email reminder use case
|   |-- infrastructure/
|   |   |-- security.py           # Password + Google token + app JWT
|   |   |-- repository_factory.py # Selected DB adapter wiring
|   |   |-- resend_email_sender.py# EmailSender adapter
|   |   |-- reminder_scheduler.py # APScheduler background adapter
|   |   |-- firestore/
|   |   |   |-- auth_repository.py
|   |   |   |-- todo_repository.py
|   |   |   `-- todo_mapper.py
|   |   |-- mongodb/
|   |   |   |-- auth_repository.py
|   |   |   `-- todo_repository.py
|   |   `-- postgresql/
|   |       |-- auth_repository.py
|   |       |-- todo_repository.py
|   |       `-- todo_schema.py
|   |-- presentation/
|   |   |-- dependencies.py       # FastAPI service/current-user injection
|   |   |-- schemas.py            # HTTP request/response shapes
|   |   |-- controllers/          # Mapping/service calls/error translation
|   |   |   |-- auth_controller.py
|   |   |   `-- todo_controller.py
|   |   `-- routers/              # URL/decorator/dependency declarations
|   |       |-- auth.py
|   |       `-- todos.py
`-- requirements.txt
```

Only `app/__init__.py` is retained as the explicit root package marker. Empty
nested package markers are intentionally omitted.

## 5. Professional implementation prompt

> Restructure the TodoFlow FastAPI backend into the target tree above. Preserve
> every public endpoint, response shape, business rule, selected-database auth
> behavior, bilingual log, and useful explanation. Keep domain code free of
> frameworks and persistence imports. Keep application services limited to use-
> case coordination. Implement repository contracts only in infrastructure.
> Keep HTTP validation, dependencies, and error translation only in
> presentation. Use typed settings for `.env`. Use FastAPI dependency injection
> rather than mutable router globals. Keep one selected database for both users
> and todos; bind JWT access tokens to that database. Split modules only at real
> responsibility boundaries and keep code beginner-readable. Add concise
> What/When/How docstrings where a function or class crosses a layer boundary.
> Do not log passwords/tokens or commit secrets. After moving code, verify
> imports, compile all modules, inspect OpenAPI routes, run signup, password
> login, Google login, and token-isolation tests for Firestore, MongoDB, and
> PostgreSQL, and run one protected
> todo API flow. Delete the old structure only after the replacement passes.

## 6. Dependency direction

```text
presentation  -> application -> domain
infrastructure ----------------> domain
app/main.py   -> presentation + application + infrastructure
domain        -> Python standard library only
```

The API composition root wires the selected repository, application reminder
service, Resend adapter and background scheduler. This keeps a database switch
from changing domain, application, route, or reminder behavior.
