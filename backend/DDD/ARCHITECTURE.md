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
   explains that `__init__.py` marks regular packages. Only real package
   boundaries receive this file; empty decorative folders are not added.

## 2. Placement rules

| Layer/module | What belongs here | What must not be here |
|---|---|---|
| `domain/` | Todo entity, value objects, business errors, repository contracts, auth user contract | FastAPI, Pydantic HTTP schemas, MongoDB, PostgreSQL, Firestore, environment variables |
| `application/` | Input/output DTOs and use cases that coordinate domain objects/repositories | HTTP status codes, database queries, SDK clients, environment reads |
| `infrastructure/` | Concrete repository adapters, password hashing, signed tokens, SDK/driver calls, repository factory | FastAPI routes, UI response models, todo business rules |
| `presentation/` | Pydantic request/response schemas, FastAPI dependencies, auth/todo routers, HTTP error mapping | SQL, PyMongo queries, Firestore URLs, password hashing |
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
|   |   |-- auth.py               # Auth contracts/data
|   |   `-- todo.py               # Todo rules/contracts
|   |-- application/
|   |   |-- dto.py                # Use-case boundary data
|   |   |-- auth_service.py       # Signup/login/token use cases
|   |   `-- todo_service.py       # Todo use cases
|   |-- infrastructure/
|   |   |-- security.py           # Password hash + signed DB token
|   |   |-- repository_factory.py # Selected DB adapter wiring
|   |   |-- firestore/
|   |   |   |-- auth_repository.py
|   |   |   `-- todo_repository.py
|   |   |-- mongodb/
|   |   |   |-- auth_repository.py
|   |   |   `-- todo_repository.py
|   |   `-- postgresql/
|   |       |-- auth_repository.py
|   |       `-- todo_repository.py
|   `-- presentation/
|       |-- dependencies.py       # FastAPI service/current-user injection
|       |-- schemas.py            # HTTP request/response shapes
|       `-- routers/
|           |-- auth.py
|           `-- todos.py
|-- requirements.txt
`-- tests/test_domain_and_security.py # Focused rule regression tests
```

`__init__.py` package markers are present but omitted from the tree for clarity.

## 5. Professional implementation prompt

> Restructure the TodoFlow FastAPI backend into the target tree above. Preserve
> every public endpoint, response shape, business rule, selected-database auth
> behavior, bilingual log, and useful explanation. Keep domain code free of
> frameworks and persistence imports. Keep application services limited to use-
> case coordination. Implement repository contracts only in infrastructure.
> Keep HTTP validation, dependencies, and error translation only in
> presentation. Use typed settings for `.env`. Use FastAPI dependency injection
> rather than mutable router globals. Keep one selected database for both users
> and todos; bind signed tokens to that database. Split modules only at real
> responsibility boundaries and keep code beginner-readable. Add concise
> What/When/How docstrings where a function or class crosses a layer boundary.
> Do not log passwords/tokens or commit secrets. After moving code, verify
> imports, compile all modules, inspect OpenAPI routes, run signup/login/token
> isolation tests for Firestore, MongoDB, and PostgreSQL, and run one protected
> todo API flow. Delete the old structure only after the replacement passes.

## 6. Dependency direction

```text
presentation  -> application -> domain
infrastructure ----------------> domain
app/main.py   -> presentation + application + infrastructure
domain        -> Python standard library only
```

The composition root is the only place that chooses concrete database
repositories. This keeps a database switch from changing domain, application,
or route behavior.
