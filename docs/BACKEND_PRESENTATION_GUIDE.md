# TodoFlow DDD Backend — Files, Folders and Functions Guide

> **Main focus:** Project ka folder structure, har file ke andar kya hai,
> kaunse classes/functions use ho rahe hain, woh kis ko call karte hain aur us
> file ko us layer mein kyun rakha gaya hai.
>
> **Presentation language:** Simple English + Roman Urdu.
>
> Is guide ko read karne ke baad normal presentation ke liye code files kholne
> ki zarurat nahi honi chahiye.

---

## Table of contents

1. [Two-minute project explanation](#1-two-minute-project-explanation)
2. [Complete folder structure](#2-complete-folder-structure)
3. [Four layers and dependency direction](#3-four-layers-and-dependency-direction)
4. [Application startup flow](#4-application-startup-flow)
5. [Root and shared files](#5-root-and-shared-files)
6. [Domain files](#6-domain-files)
7. [Application files](#7-application-files)
8. [Presentation files](#8-presentation-files)
9. [Shared infrastructure files](#9-shared-infrastructure-files)
10. [Firestore files](#10-firestore-files)
11. [MongoDB files](#11-mongodb-files)
12. [PostgreSQL files](#12-postgresql-files)
13. [Complete request flows](#13-complete-request-flows)
14. [File-to-file dependency map](#14-file-to-file-dependency-map)
15. [All important functions quick sheet](#15-all-important-functions-quick-sheet)
16. [Presentation order](#16-presentation-order)
17. [File-focused viva questions](#17-file-focused-viva-questions)

---

## 1. Two-minute project explanation

Presentation mein yeh bol sakte hain:

> “TodoFlow backend FastAPI aur Domain-Driven Design structure use karta hai.
> Backend ka root package `app` hai. Is ke andar Domain, Application,
> Presentation aur Infrastructure folders hain.
>
> Domain folder business entities, validation rules aur repository contracts
> rakhta hai. Application folder signup, login aur todo workflows coordinate
> karta hai. Presentation folder HTTP request/response schemas, authentication
> dependencies aur API routes rakhta hai. Infrastructure folder password/token
> security aur Firestore, MongoDB, PostgreSQL ki concrete repository
> implementations rakhta hai.
>
> `app/main.py` composition root hai. Yeh configuration read karta hai,
> selected database ke auth aur todo repositories banata hai, un repositories
> ko services mein inject karta hai aur routers ko FastAPI application ke sath
> connect karta hai. Is structure ki wajah se database change hota hai lekin
> domain rules, application services aur public routes change nahi hotin.”

Project ko one line mein:

```text
Presentation receives -> Application coordinates -> Domain decides -> Infrastructure saves
```

---

## 2. Complete folder structure

```text
backend/DDD/
|-- main.py
|-- .env
|-- .env.example
|-- requirements.txt
|-- README.md
|-- ARCHITECTURE.md
|-- serviceAccountKey.json
|
`-- app/
    |-- __init__.py
    |-- main.py
    |-- config.py
    |-- logging.py
    |
    |-- domain/
    |   |-- auth.py
    |   `-- todo.py
    |
    |-- application/
    |   |-- dto.py
    |   |-- auth_service.py
    |   `-- todo_service.py
    |
    |-- presentation/
    |   |-- schemas.py
    |   |-- dependencies.py
    |   `-- routers/
    |       |-- auth.py
    |       `-- todos.py
    |
    `-- infrastructure/
        |-- security.py
        |-- repository_factory.py
        |
        |-- firestore/
        |   |-- auth_repository.py
        |   `-- todo_repository.py
        |
        |-- mongodb/
        |   |-- auth_repository.py
        |   `-- todo_repository.py
        |
        `-- postgresql/
            |-- auth_repository.py
            `-- todo_repository.py
```

### Folder names ka simple meaning

| Folder | Simple meaning | Is mein kya hota hai? |
|---|---|---|
| `domain` | Business ka heart | Entity, value object, business errors, repository contracts |
| `application` | Workflow coordinator | Input/output DTOs and use-case services |
| `presentation` | HTTP boundary | Pydantic schemas, dependencies and routes |
| `infrastructure` | Technical implementation | Security, database factory and DB adapters |
| `routers` | Endpoint grouping | Auth endpoints and todo endpoints separate files |
| `firestore` | Firestore adapter | Firestore auth and todo persistence |
| `mongodb` | MongoDB adapter | Mongo auth and todo persistence |
| `postgresql` | PostgreSQL adapter | SQL auth and todo persistence |

### Sirf root `app/__init__.py` kyun hai?

- `app/__init__.py` root `app` ko explicit Python package banati hai.
- Nested folders mein package initialization ya exports nahi hain.
- Python 3 un nested folders ko namespace packages ke through import kar leta
  hai.
- Isliye empty decorative `__init__.py` files remove ki gayi hain.

---

## 3. Four layers and dependency direction

### Layer responsibility

| Layer | Main question | Project examples |
|---|---|---|
| Domain | Business rule kya hai? | `TodoItem`, `TaskTitle`, repository ABCs |
| Application | Workflow kis order mein chalega? | `AuthService`, `TodoService` |
| Presentation | HTTP input/output kya hai? | Schemas, dependencies, routers |
| Infrastructure | Technically kaise implement hoga? | PBKDF2, HMAC, Firestore, MongoDB, SQL |

### Dependency diagram

```text
Presentation --------> Application --------> Domain
      |                       |                  ^
      |                       |                  |
      `-----------------------|------ Infrastructure

app/main.py wires all outer objects together.
```

More exact diagram:

```text
auth.py route
    -> AuthService
        -> AuthRepository contract
            <- FirestoreAuthRepository
            <- MongoAuthRepository
            <- PostgreSQLAuthRepository

todos.py route
    -> TodoService
        -> TodoItem business rules
        -> TodoRepository contract
            <- FirestoreTodoRepository
            <- MongoTodoRepository
            <- PostgreSQLTodoRepository
```

### Kis layer mein kya nahi hona chahiye?

| Layer | Yahan nahi hona chahiye |
|---|---|
| Domain | FastAPI, Pydantic HTTP schema, SQL, PyMongo, Firestore URL |
| Application | HTTP status codes and database queries |
| Presentation | Password hashing, SQL and business entity rules |
| Infrastructure | API route definitions and frontend response models |

Ready answer:

> “High-level application services concrete database par depend nahi kartin.
> Woh domain repository contract par depend karti hain. Infrastructure adapters
> us contract ko implement karte hain. Isi ko dependency inversion kehte hain.”

---

## 4. Application startup flow

Command:

```powershell
python -m uvicorn main:app --reload
```

Exact flow:

```text
1. Uvicorn root main.py import karta hai
2. root main.py app.main se app import karta hai
3. app/main.py ke end par create_app() call hota hai
4. get_settings() .env and terminal variables read karta hai
5. FastAPI application create hoti hai
6. CORS middleware add hota hai
7. request logging middleware add hota hai
8. repository_factory active DATABASE read karti hai
9. matching todo + auth repositories create hoti hain
10. repositories TodoService and AuthService mein inject hoti hain
11. services app.state par store hoti hain
12. auth_router and todo_router include hote hain
13. health_check route register hota hai
14. server requests ke liye ready hota hai
```

Important line:

```text
Configuration -> Repository Factory -> Repositories -> Services -> Routes
```

---

## 5. Root and shared files

### 5.1 `main.py` — simple entrypoint

Path: [`backend/DDD/main.py`](../backend/DDD/main.py)

Purpose:

- Beginner-friendly `uvicorn main:app` command support karta hai.
- Actual application ko `app/main.py` se re-export karta hai.
- `python main.py` direct command bhi support karta hai.

File ke important parts:

| Part | Kya karta hai? | Kyun hai? |
|---|---|---|
| `from app.config import get_settings` | Server settings leta hai | Host, port, reload hard-code nahi hote |
| `from app.main import app, create_app` | Real app import/re-export | Root file thin rehti hai |
| `__all__ = ["app", "create_app"]` | Public exports declare | File ka public interface clear hota hai |
| `if __name__ == "__main__"` | Direct execution detect | Import ke waqt server dobara start nahi hota |
| `uvicorn.run(...)` | Server run | Typed host/port/reload use karta hai |

Ready answer:

> “Root `main.py` business logic nahi rakhti. Yeh sirf beginner-compatible
> bridge hai jo real FastAPI app ko export karti hai.”

### 5.2 `app/__init__.py` — root package marker

Path: [`backend/DDD/app/__init__.py`](../backend/DDD/app/__init__.py)

Is file mein sirf package docstring hai. Koi business logic, import side effect
ya database connection nahi hai.

Purpose:

- `app` ko explicit regular Python package banana.
- `from app...` imports ko clear rakhna.

### 5.3 `app/main.py` — composition root

Path: [`backend/DDD/app/main.py`](../backend/DDD/app/main.py)

Main function:

```python
create_app(settings: Settings | None = None) -> FastAPI
```

Function ka complete work:

| Order | Statement/operation | Reason |
|---|---|---|
| 1 | `settings or get_settings()` | Explicit settings ya cached `.env` settings |
| 2 | `FastAPI(title=settings.app_name)` | Application object create |
| 3 | `CORSMiddleware` | Frontend origins allow |
| 4 | `install_request_logging(app)` | Request ID and timing logs |
| 5 | `create_repositories(settings)` | Selected database adapters |
| 6 | `TodoService(todo_repository)` | Todo dependency injection |
| 7 | `AuthService(auth_repository)` | Auth dependency injection |
| 8 | services on `app.state` | Request dependencies ko shared instances |
| 9 | `include_router(...)` | Auth/todo endpoints mount |
| 10 | nested `health_check()` | API and selected DB status |
| 11 | `return app` | Fully configured application |

Nested function:

```python
health_check() -> dict[str, str]
```

Return fields:

```text
status + architecture + selected database
```

Module end:

```python
app = create_app()
```

Is line ki wajah se Uvicorn import ke waqt complete application ready hoti hai.

### 5.4 `app/config.py` — typed settings

Path: [`backend/DDD/app/config.py`](../backend/DDD/app/config.py)

Top-level value:

```python
BASE_DIRECTORY
```

Backend folder ka absolute path banata hai. `.env` aur Firebase key current
terminal folder ke bajaye correct backend folder se resolve hoti hain.

Main class:

```python
Settings(BaseSettings)
```

Settings groups:

| Group | Fields |
|---|---|
| App | `app_name`, `app_architecture` |
| Server | `backend_host`, `backend_port`, `backend_reload` |
| Browser | `cors_origins` |
| Logs | `log_level` |
| Database selection | `database` |
| Auth | `auth_token_secret`, `auth_token_expire_minutes` |
| MongoDB | URI, database, todo/user collection names |
| PostgreSQL | `postgresql_url` |
| Firestore | credential path, API URL, database and collection names, page size |

Important configuration rule:

- `Settings` fields types declare karti hai; hard-coded runtime defaults nahi.
- Har actual value `.env` ya terminal environment variable se aati hai.
- Missing variable startup par Pydantic validation error deti hai.
- Terminal variable same-name `.env` value ko override kar sakti hai.

Properties/functions:

| Name | Input/source | Work | Return |
|---|---|---|---|
| `selected_database` | `self.database` | Trim/lowercase; `firebase` alias -> `firestore`; supported value check | DB name or `ValueError` |
| `allowed_origins` | Comma-separated CORS string | Split and trim | `list[str]` |
| `firebase_credential_file` | Credential path | Relative path backend root se resolve | Absolute `Path` |
| `get_settings()` | `.env` + environment | `Settings()` create and cache | One `Settings` object |

`@lru_cache` ka reason:

- `.env` every request par read nahi hoti.
- Process ke andar configuration stable rehti hai.
- Database switch ke baad server restart zaroori hota hai.

### 5.5 `app/logging.py` — bilingual request logger

Path: [`backend/DDD/app/logging.py`](../backend/DDD/app/logging.py)

Important module values:

| Name | Purpose |
|---|---|
| `logger` | Named `todoflow.ddd` logger |
| `_request_number` | `#001`, `#002` counter |
| `_current_request` | Concurrent request ka `ContextVar` label |

Functions:

| Function | Parameters | Kya karta hai? |
|---|---|---|
| `log_step(area, english, roman_urdu)` | Layer + two messages | Request number ke sath INFO log |
| `log_error(area, message)` | Layer + safe error | Request number ke sath ERROR log |
| `install_request_logging(app)` | FastAPI app | Middleware register karta hai |
| nested `request_logger(request, call_next)` | Request + next handler | Start/end, status, duration, exception and context reset |

`OPTIONS` requests kyun skip hoti hain?

Browser CORS preflight background request hoti hai. Skip karne se learning logs
clean rehte hain.

`ContextVar` kyun?

Parallel requests ka label mix nahi hota. `finally` mein reset hone se next
request old ID inherit nahi karti.

### 5.6 `.env.example`

Path: [`backend/DDD/.env.example`](../backend/DDD/.env.example)

Is file mein safe sample configuration hai:

- selected `DATABASE`;
- auth token secret sample;
- MongoDB URI and collection names;
- PostgreSQL URL format;
- Firestore credential path and collection names.

Every listed key required hai because `config.py` mein runtime defaults nahi
rakhe gaye. Inactive database fields safe sample/local values rakh sakte hain.

`.env.example` commit hoti hai; real `.env` secrets ke sath Git ignored rehti
hai.

### 5.7 `requirements.txt`

Path: [`backend/DDD/requirements.txt`](../backend/DDD/requirements.txt)

| Package | Project mein kaam |
|---|---|
| `fastapi` | API, middleware, dependencies |
| `uvicorn` | ASGI server |
| `pydantic[email]` | HTTP validation and email validation |
| `pydantic-settings` | Typed `.env` settings |
| `firebase-admin` | Firestore service-account credential |
| `requests` | Firestore REST HTTP stack |
| `python-dotenv` | `.env` loading support |
| `pymongo` | MongoDB driver |
| `psycopg[binary]` | PostgreSQL driver |

---

## 6. Domain files

Domain layer framework aur database se independent hai.

### 6.1 `domain/auth.py`

Path: [`backend/DDD/app/domain/auth.py`](../backend/DDD/app/domain/auth.py)

#### `ValidationException`

Safe authentication/input error. Infrastructure is exception ko raise kar sakti
hai aur presentation usay HTTP 400/401 mein map karti hai.

#### `UserData`

Frozen dataclass:

```text
uid + email + token
```

Repository se application service ko database-independent auth result deti hai.

#### `AuthRepository(ABC)`

Authentication contract:

| Method | Parameters | Return | Required behavior |
|---|---|---|---|
| `signup` | email, password, name | `UserData` | Selected DB mein account create |
| `login` | email, password | `UserData` | Credentials verify |
| `authenticate` | token | `UserData` | Token and live DB user verify |

ABC ka purpose:

- Application ko Firestore/Mongo/SQL ka pata nahi hota.
- Three concrete auth repositories same methods implement karti hain.

### 6.2 `domain/todo.py`

Path: [`backend/DDD/app/domain/todo.py`](../backend/DDD/app/domain/todo.py)

#### Domain errors

| Class | Kab raise hoti hai? |
|---|---|
| `DomainError` | Parent business error |
| `InvalidTaskTitleError` | Title length 3–120 ke bahar |
| `TaskAlreadyCompletedError` | Completed todo dobara complete ho |
| `TodoNotFoundError` | Current owner ka todo na mile |

#### `Priority(str, Enum)`

Allowed values:

```text
LOW, MEDIUM, HIGH
```

#### `TaskTitle`

Frozen value object with one field: `value`.

Method:

```python
__post_init__() -> None
```

Work:

1. Title trim.
2. Minimum 3 characters.
3. Maximum 120 characters.
4. Clean value object mein store.

Why value object?

Har valid `TodoItem` ke paas valid title guarantee hoti hai.

#### `TodoItem`

Main entity fields:

```text
id
title: TaskTitle
priority: Priority
is_completed
created_at
owner_uid
completed_at
```

Methods:

| Method | Input | Work | Return/error |
|---|---|---|---|
| `create(title, priority, owner_uid)` | Plain values | UUID, title validation, uppercase priority, UTC time, incomplete state | New `TodoItem` |
| `complete()` | Existing entity | Already-complete check; status true; UTC completion time | `None` or `TaskAlreadyCompletedError` |

Business rule entity ke andar kyun?

Route, service ya database change ho tab bhi completion rule same rehta hai.

#### `TodoRepository(ABC)`

| Method | Parameters | Return |
|---|---|---|
| `save` | `TodoItem` | `None` |
| `get_by_id` | todo ID + owner UID | `TodoItem | None` |
| `get_by_owner` | owner UID | `list[TodoItem]` |
| `delete` | todo ID + owner UID | `None` |

Owner UID contract ka part hai, isliye infrastructure queries ownership ko
database operation tak carry karti hain.

---

## 7. Application files

Application layer use cases ko coordinate karti hai. Is mein HTTP status aur
database query nahi hoti.

### 7.1 `application/dto.py`

Path: [`backend/DDD/app/application/dto.py`](../backend/DDD/app/application/dto.py)

DTO = Data Transfer Object.

Input DTOs:

| Class | Fields | Kis function ko jati hai? |
|---|---|---|
| `SignupInput` | email, password, display_name | `AuthService.signup` |
| `LoginInput` | email, password | `AuthService.login` |
| `CreateTodoInput` | title, priority, owner_uid | `TodoService.create` |
| `TodoActionInput` | todo_id, owner_uid | Complete/delete |

Output DTOs:

| Class | Fields | Kahan jati hai? |
|---|---|---|
| `AuthOutput` | uid, email, token | Auth route |
| `TodoOutput` | Seven API-friendly todo fields | Todo routes |

All DTOs `frozen=True` hain, so creation ke baad accidentally mutate nahi hotin.

Presentation schemas se separate kyun?

```text
Presentation schema = HTTP JSON contract
Application DTO     = use-case input/output contract
Domain entity       = identity + state + business behavior
```

### 7.2 `application/auth_service.py`

Path: [`backend/DDD/app/application/auth_service.py`](../backend/DDD/app/application/auth_service.py)

Main class:

```python
AuthService(repository: AuthRepository)
```

Constructor repository abstraction receive karta hai.

| Method | Input | Calls | Return |
|---|---|---|---|
| `signup(data)` | `SignupInput` | `repository.signup(...)`, log, `_to_output` | `AuthOutput` |
| `login(data)` | `LoginInput` | `repository.login(...)`, log, `_to_output` | `AuthOutput` |
| `authenticate(token)` | Token string | `repository.authenticate(token)`, `_to_output` | `AuthOutput` |
| `_to_output(uid,email,token)` | Three strings | `AuthOutput(...)` | `AuthOutput` |

Service hashing/database work kyun nahi karti?

Woh details infrastructure repository ki responsibility hain. Service sirf
workflow order jaanti hai.

### 7.3 `application/todo_service.py`

Path: [`backend/DDD/app/application/todo_service.py`](../backend/DDD/app/application/todo_service.py)

#### `to_output(todo)`

`TodoItem` ko `TodoOutput` mein map karta hai:

- `TaskTitle` -> string;
- `Priority` -> string;
- datetime -> ISO string;
- missing completion time -> `None`.

#### `TodoService(repository: TodoRepository)`

| Method | Input | Exact call order | Return |
|---|---|---|---|
| `create` | `CreateTodoInput` | `TodoItem.create` -> `save` -> log -> `to_output` | `TodoOutput` |
| `list` | owner UID | `get_by_owner` -> log count -> map outputs | `list[TodoOutput]` |
| `complete` | `TodoActionInput` | `_get_todo_or_fail` -> entity `complete` -> `save` -> log | `TodoOutput` |
| `delete` | `TodoActionInput` | `_get_todo_or_fail` -> repository `delete` -> log | `None` |
| `_get_todo_or_fail` | `TodoActionInput` | `get_by_id(id, owner)` | Entity or `TodoNotFoundError` |

`_get_todo_or_fail` helper kyun?

Complete aur delete dono mein same ID + owner existence check duplicate nahi
hota.

---

## 8. Presentation files

Presentation layer FastAPI-specific HTTP boundary hai.

### 8.1 `presentation/schemas.py`

Path: [`backend/DDD/app/presentation/schemas.py`](../backend/DDD/app/presentation/schemas.py)

| Pydantic class | Fields/rules | Used by |
|---|---|---|
| `SignupRequest` | Valid email, password min 6, display name default User | Signup route input |
| `LoginRequest` | Valid email, password min 6 | Login route input |
| `AuthResponse` | uid, email, token, message | Signup/login output |
| `CreateTodoRequest` | Title 3–120; six upper/lower priority literals; default MEDIUM | Create route input |
| `TodoResponse` | Complete public todo shape | Todo route output |

Important:

```text
Pydantic validates HTTP.
Domain validates business invariants.
```

### 8.2 `presentation/dependencies.py`

Path: [`backend/DDD/app/presentation/dependencies.py`](../backend/DDD/app/presentation/dependencies.py)

#### `CurrentUser`

Frozen dataclass with `uid` and `email`. Protected routes ko verified identity
deti hai.

#### `bearer = HTTPBearer()`

`Authorization: Bearer <token>` header parse karta hai.

#### Service provider functions

| Function | Reads | Return |
|---|---|---|
| `get_auth_service(request)` | `request.app.state.auth_service` | `AuthService` |
| `get_todo_service(request)` | `request.app.state.todo_service` | `TodoService` |

#### Dependency aliases

```text
AuthServiceDep
TodoServiceDep
CredentialsDep
CurrentUserDep
```

Aliases `Annotated + Depends` use karke route signatures short rakhti hain.

#### `current_user(credentials, auth_service)`

Flow:

```text
Bearer credentials
 -> AuthService.authenticate
 -> selected AuthRepository.authenticate
 -> CurrentUser(uid, email)
```

Error mapping:

- Expected `ValidationException` -> HTTP 401.
- Unexpected error -> safe generic HTTP 401; technical detail log mein.

Security point:

Owner UID request body se trust nahi hoti. Verified token se aati hai.

### 8.3 `presentation/routers/auth.py`

Path: [`backend/DDD/app/presentation/routers/auth.py`](../backend/DDD/app/presentation/routers/auth.py)

Router:

```python
APIRouter(prefix="/auth", tags=["Auth"])
```

Functions:

| Route function | HTTP | Mapping | Success | Error |
|---|---|---|---|---|
| `signup` | `POST /auth/signup` | `SignupRequest -> SignupInput -> AuthService.signup -> AuthResponse` | 201 | Validation -> 400 |
| `login` | `POST /auth/login` | `LoginRequest -> LoginInput -> AuthService.login -> AuthResponse` | 200 | Validation -> 401 |

Route ka kaam:

1. HTTP request receive.
2. Presentation log.
3. Request schema ko application DTO mein map.
4. Service call.
5. Application output ko response schema mein map.
6. Known error ko HTTP exception mein map.

### 8.4 `presentation/routers/todos.py`

Path: [`backend/DDD/app/presentation/routers/todos.py`](../backend/DDD/app/presentation/routers/todos.py)

Router:

```python
APIRouter(prefix="/todos", tags=["Todos"])
```

Functions:

| Function | HTTP | Service call | Success/error |
|---|---|---|---|
| `list_todos` | `GET /todos` | `todo_service.list(user.uid)` | 200 list |
| `create_todo` | `POST /todos` | `todo_service.create(CreateTodoInput(...))` | 201; domain error 400 |
| `complete_todo` | `PATCH /todos/{id}/complete` | `todo_service.complete(TodoActionInput(...))` | 200; missing 404; rule error 400 |
| `delete_todo` | `DELETE /todos/{id}` | `todo_service.delete(TodoActionInput(...))` | 204; missing 404 |

Important mapping:

```text
todo_id    <- URL path
owner_uid  <- verified CurrentUser
title      <- validated request body
priority   <- validated request body
```

---

## 9. Shared infrastructure files

### 9.1 `infrastructure/security.py`

Path: [`backend/DDD/app/infrastructure/security.py`](../backend/DDD/app/infrastructure/security.py)

Main class:

```python
AuthSecurity(secret, database, token_expire_minutes)
```

Constructor stores:

- secret as bytes;
- active database name;
- expiry minutes converted to seconds.

Methods:

| Method | Input | Work | Return |
|---|---|---|---|
| `normalize_email` | Email | Trim + lowercase | Clean email |
| `hash_password` | Password | Random salt + PBKDF2-HMAC-SHA256 | `salt:hash` |
| `password_matches` | Password + saved hash | Derive again + `compare_digest` | Boolean |
| `create_token` | UID + email | JSON payload + Base64 + HMAC signature | Signed token |
| `read_token` | Token | Signature, DB, expiry and fields check | `(uid, email)` |
| `_derive_password_hash` | Password + salt | 120,000 PBKDF2 rounds | Hex hash |
| `_read_payload` | Token | Split, signature verify, JSON decode | Payload dict |
| `_sign` | Encoded payload | HMAC-SHA256 | Signature bytes |
| `_encode` | Bytes | URL-safe Base64 without padding | String |
| `_decode` | String | Padding restore + Base64 decode | Bytes |

Token payload:

```text
uid + email + database + expires_at
```

Password/token logic infrastructure mein kyun?

PBKDF2, HMAC, Base64 and system time technical implementation details hain.

### 9.2 `infrastructure/repository_factory.py`

Path: [`backend/DDD/app/infrastructure/repository_factory.py`](../backend/DDD/app/infrastructure/repository_factory.py)

Main function:

```python
create_repositories(settings) -> tuple[TodoRepository, AuthRepository]
```

Flow:

1. `settings.selected_database` read.
2. Shared `AuthSecurity` create.
3. Active DB branch choose.
4. Matching todo + auth pair return.

Database helper functions:

| Function | Kya connect/create karti hai? |
|---|---|
| `_create_firestore_repositories` | Firebase credentials, project URL, `AuthorizedSession`, Firestore repos |
| `_create_mongodb_repositories` | `MongoClient`, startup ping, database, collections, Mongo repos |
| `_create_postgresql_repositories` | URL check and PostgreSQL repos |

Return order:

```text
(todo_repository, auth_repository)
```

Matching pair kyun important hai?

Selected database users aur todos dono own karti hai. Mixed Mongo auth +
PostgreSQL todo wiring possible nahi hoti.

---

## 10. Firestore files

### 10.1 `firestore/auth_repository.py`

Path: [`backend/DDD/app/infrastructure/firestore/auth_repository.py`](../backend/DDD/app/infrastructure/firestore/auth_repository.py)

Class:

```python
FirestoreAuthRepository(AuthRepository)
```

Constructor receives:

```text
AuthorizedSession + auth users URL + AuthSecurity
```

Storage path:

```text
auth_users/{sha256(normalized_email)}
```

Methods:

| Method | Important calls/work | Return |
|---|---|---|
| `signup` | Normalize -> `_find_user` -> UUID -> hash -> PATCH -> token | `UserData` |
| `login` | Normalize -> `_find_user` -> password compare -> token | `UserData` |
| `authenticate` | `read_token` -> `_find_user` -> UID match | `UserData` |
| `_find_user` | Authorized GET; 404 -> None | User dict or None |
| `_user_url` | SHA-256 normalized email | Document URL |
| `_to_document` | Python dict -> Firestore `stringValue` fields | REST document |
| `_from_document` | Firestore fields -> plain dict | User dict |

Email hash document ID kyun?

- Direct deterministic lookup.
- Normalized email uniqueness.
- Raw email URL path mein directly nahi.

### 10.2 `firestore/todo_repository.py`

Path: [`backend/DDD/app/infrastructure/firestore/todo_repository.py`](../backend/DDD/app/infrastructure/firestore/todo_repository.py)

Class:

```python
FirestoreTodoRepository(TodoRepository)
```

Storage path:

```text
users/{owner_uid}/todos/{todo_id}
```

Methods:

| Method | Work |
|---|---|
| `save` | Entity -> REST document -> PATCH/upsert |
| `get_by_id` | Owner path + ID GET; 404 -> None; document -> entity |
| `get_by_owner` | User subcollection pages loop; all documents -> entities |
| `delete` | Owner path + ID DELETE; missing delete harmless |
| `_collection_url` | URL-encode user collection, owner and todo collection |
| `_document_url` | Collection URL + encoded todo ID |
| `_to_document` | Entity fields -> typed REST fields |
| `_to_entity` | REST fields -> `TaskTitle`, `Priority`, `TodoItem` |
| `_encode` | Python None/bool/string -> Firestore typed wrapper |
| `_decode` | Firestore typed wrapper -> Python value |

Pagination loop:

```text
GET page -> documents add -> nextPageToken?
    yes: next page
    no: return all
```

---

## 11. MongoDB files

### 11.1 `mongodb/auth_repository.py`

Path: [`backend/DDD/app/infrastructure/mongodb/auth_repository.py`](../backend/DDD/app/infrastructure/mongodb/auth_repository.py)

Class:

```python
MongoAuthRepository(AuthRepository)
```

Constructor:

- Mongo `Collection` receive.
- `email` unique index create.
- Shared `AuthSecurity` store.

Methods:

| Method | Work |
|---|---|
| `signup` | Normalize -> UUID -> hash -> `insert_one` -> token |
| `login` | `find_one(email)` -> password compare -> token |
| `authenticate` | Token read -> `find_one(_id + email)` -> live user check |

User document:

```text
_id = user UUID
email
display_name
password_hash
```

### 11.2 `mongodb/todo_repository.py`

Path: [`backend/DDD/app/infrastructure/mongodb/todo_repository.py`](../backend/DDD/app/infrastructure/mongodb/todo_repository.py)

Class:

```python
MongoTodoRepository(TodoRepository)
```

Constructor `owner_uid` index create karta hai.

Methods:

| Method | Mongo operation | Security/mapping |
|---|---|---|
| `save` | `replace_one(..., upsert=True)` | Create or replace same ID |
| `get_by_id` | `find_one({_id, owner_uid})` | ID + owner both required |
| `get_by_owner` | `find({owner_uid})` | Only current user list |
| `delete` | `delete_one({_id, owner_uid})` | Cross-user delete blocked |
| `_to_document` | Entity -> Mongo document | Datetimes ISO strings |
| `_to_entity` | Mongo document -> entity | Domain types restore |

Todo document:

```text
_id
title
priority
is_completed
created_at
completed_at
owner_uid
```

---

## 12. PostgreSQL files

### 12.1 `postgresql/auth_repository.py`

Path: [`backend/DDD/app/infrastructure/postgresql/auth_repository.py`](../backend/DDD/app/infrastructure/postgresql/auth_repository.py)

Class:

```python
PostgreSQLAuthRepository(AuthRepository)
```

Constructor:

1. Connection URL store.
2. `AuthSecurity` store.
3. `_create_table()` call.

Methods:

| Method | SQL/work | Return |
|---|---|---|
| `signup` | Parameterized `INSERT users`; unique violation map; token | `UserData` |
| `login` | `SELECT ... WHERE email=%s`; password compare; token | `UserData` |
| `authenticate` | Token read; `SELECT id WHERE id AND email` | `UserData` |
| `_create_table` | `CREATE TABLE IF NOT EXISTS users` | None |

Users table:

```text
id TEXT PRIMARY KEY
email TEXT UNIQUE NOT NULL
display_name TEXT NOT NULL
password_hash TEXT NOT NULL
```

`dict_row` login query mein readable `user["password_hash"]` access deti hai.

### 12.2 `postgresql/todo_repository.py`

Path: [`backend/DDD/app/infrastructure/postgresql/todo_repository.py`](../backend/DDD/app/infrastructure/postgresql/todo_repository.py)

Class:

```python
PostgreSQLTodoRepository(TodoRepository)
```

Constructor URL store karke `_create_table()` call karta hai.

Methods:

| Method | SQL/work |
|---|---|
| `save` | `INSERT ... ON CONFLICT (id) DO UPDATE` |
| `get_by_id` | `SELECT ... WHERE id=%s AND owner_uid=%s` |
| `get_by_owner` | Owner SELECT + `ORDER BY created_at DESC` |
| `delete` | `DELETE WHERE id=%s AND owner_uid=%s` |
| `_create_table` | `CREATE TABLE IF NOT EXISTS todos` |
| `_to_entity` | Named SQL row -> domain `TodoItem` |

Todos table:

```text
id TEXT PRIMARY KEY
title TEXT NOT NULL
priority TEXT NOT NULL
is_completed BOOLEAN NOT NULL
created_at TIMESTAMPTZ NOT NULL
completed_at TIMESTAMPTZ NULL
owner_uid TEXT NOT NULL
```

Parameterized `%s` values kyun?

User values query string mein concatenate nahi hoti; SQL injection risk reduce
hota hai.

---

## 13. Complete request flows

### 13.1 Signup flow

```text
POST /auth/signup
 -> SignupRequest validates JSON
 -> auth.signup route creates SignupInput
 -> AuthService.signup
 -> selected AuthRepository.signup
 -> normalize email
 -> hash password
 -> selected database user record
 -> create database-bound token
 -> UserData
 -> AuthOutput
 -> AuthResponse
```

### 13.2 Login flow

```text
POST /auth/login
 -> LoginRequest
 -> LoginInput
 -> AuthService.login
 -> selected repository finds user
 -> password_matches
 -> create_token
 -> AuthResponse
```

### 13.3 Protected request authentication flow

```text
Authorization Bearer token
 -> HTTPBearer
 -> current_user dependency
 -> AuthService.authenticate
 -> selected repository.authenticate
 -> AuthSecurity.read_token
 -> live database user lookup
 -> CurrentUser(uid, email)
 -> route executes
```

### 13.4 Create todo flow

```text
POST /todos
 -> CreateTodoRequest
 -> CurrentUser dependency
 -> CreateTodoInput(title, priority, user.uid)
 -> TodoService.create
 -> TodoItem.create
 -> domain validation + UUID + UTC time
 -> selected TodoRepository.save
 -> TodoOutput
 -> TodoResponse
```

### 13.5 List todos flow

```text
GET /todos
 -> verified user.uid
 -> TodoService.list
 -> repository.get_by_owner(uid)
 -> list[TodoItem]
 -> each to_output
 -> list[TodoResponse]
```

### 13.6 Complete todo flow

```text
PATCH /todos/{id}/complete
 -> verified user.uid
 -> TodoActionInput(id, uid)
 -> TodoService._get_todo_or_fail
 -> repository.get_by_id(id, uid)
 -> TodoItem.complete
 -> repository.save(updated entity)
 -> TodoResponse
```

### 13.7 Delete todo flow

```text
DELETE /todos/{id}
 -> verified user.uid
 -> TodoActionInput(id, uid)
 -> TodoService._get_todo_or_fail
 -> repository.delete(id, uid)
 -> 204 No Content
```

---

## 14. File-to-file dependency map

### Startup dependencies

```text
main.py
 -> app/config.py
 -> app/main.py
      -> application/auth_service.py
      -> application/todo_service.py
      -> infrastructure/repository_factory.py
      -> logging.py
      -> presentation/routers/auth.py
      -> presentation/routers/todos.py
```

### Auth dependencies

```text
presentation/routers/auth.py
 -> presentation/schemas.py
 -> presentation/dependencies.py
 -> application/dto.py
 -> application/auth_service.py
 -> domain/auth.py contract
 -> selected infrastructure auth_repository.py
 -> infrastructure/security.py
```

### Todo dependencies

```text
presentation/routers/todos.py
 -> presentation/schemas.py
 -> presentation/dependencies.py
 -> application/dto.py
 -> application/todo_service.py
 -> domain/todo.py entity + contract
 -> selected infrastructure todo_repository.py
```

### Database selection dependencies

```text
config.Settings.selected_database
 -> repository_factory.create_repositories
      -> Firestore pair
      OR MongoDB pair
      OR PostgreSQL pair
```

### Logger usage

```text
Presentation -> log_step
Application  -> log_step
Infrastructure -> log_step/log_error
Middleware -> request start/end/status/time
```

---

## 15. All important functions quick sheet

### Root/shared

| Function/property | File | One-line job |
|---|---|---|
| `create_app` | `app/main.py` | Complete FastAPI app wire |
| `health_check` | `app/main.py` | Health and active DB return |
| `selected_database` | `config.py` | Supported DB normalize/check |
| `allowed_origins` | `config.py` | CORS string -> list |
| `firebase_credential_file` | `config.py` | Credential path absolute |
| `get_settings` | `config.py` | Cached typed settings |
| `log_step` | `logging.py` | Bilingual INFO step |
| `log_error` | `logging.py` | Safe ERROR log |
| `install_request_logging` | `logging.py` | Middleware install |
| `request_logger` | `logging.py` | Request ID/status/time trace |

### Domain/application

| Function/method | File | One-line job |
|---|---|---|
| `TaskTitle.__post_init__` | `domain/todo.py` | Title invariant |
| `TodoItem.create` | `domain/todo.py` | New valid todo |
| `TodoItem.complete` | `domain/todo.py` | One-time completion |
| `AuthService.signup` | `auth_service.py` | Signup workflow |
| `AuthService.login` | `auth_service.py` | Login workflow |
| `AuthService.authenticate` | `auth_service.py` | Token workflow |
| `AuthService._to_output` | `auth_service.py` | User result mapping |
| `to_output` | `todo_service.py` | Entity -> output DTO |
| `TodoService.create` | `todo_service.py` | Create workflow |
| `TodoService.list` | `todo_service.py` | Owner list workflow |
| `TodoService.complete` | `todo_service.py` | Complete workflow |
| `TodoService.delete` | `todo_service.py` | Delete workflow |
| `_get_todo_or_fail` | `todo_service.py` | Shared ownership lookup |

### Presentation

| Function | File | One-line job |
|---|---|---|
| `get_auth_service` | `dependencies.py` | App state -> AuthService |
| `get_todo_service` | `dependencies.py` | App state -> TodoService |
| `current_user` | `dependencies.py` | Bearer token -> verified user |
| `signup` | `routers/auth.py` | Signup HTTP endpoint |
| `login` | `routers/auth.py` | Login HTTP endpoint |
| `list_todos` | `routers/todos.py` | Todo list endpoint |
| `create_todo` | `routers/todos.py` | Todo creation endpoint |
| `complete_todo` | `routers/todos.py` | Completion endpoint |
| `delete_todo` | `routers/todos.py` | Deletion endpoint |

### Infrastructure

| Function/method | File | One-line job |
|---|---|---|
| `normalize_email` | `security.py` | Canonical email |
| `hash_password` | `security.py` | Salted PBKDF2 hash |
| `password_matches` | `security.py` | Safe password compare |
| `create_token` | `security.py` | Signed DB-bound token |
| `read_token` | `security.py` | Token validation |
| `_derive_password_hash` | `security.py` | PBKDF2 calculation |
| `_read_payload` | `security.py` | Token parse/signature check |
| `_sign` | `security.py` | HMAC signature |
| `_encode/_decode` | `security.py` | URL-safe Base64 |
| `create_repositories` | `repository_factory.py` | Selected adapter pair |
| `_create_firestore_repositories` | `repository_factory.py` | Firestore wiring |
| `_create_mongodb_repositories` | `repository_factory.py` | Mongo wiring |
| `_create_postgresql_repositories` | `repository_factory.py` | PostgreSQL wiring |

### Repository contract methods

```text
AuthRepository:
  signup, login, authenticate

TodoRepository:
  save, get_by_id, get_by_owner, delete
```

Every database adapter in methods ko apni technology se implement karta hai.

---

## 16. Presentation order

### Recommended 15–20 minute order

#### Part 1 — Structure overview (2 minutes)

1. Complete folder tree show.
2. Four layers name.
3. One-line dependency direction.

Say:

> “Structure ka goal business code ko HTTP aur database details se separate
> rakhna hai.”

#### Part 2 — Startup files (3 minutes)

Explain:

1. root `main.py`;
2. `app/main.py`;
3. `config.py`;
4. `repository_factory.py`.

Flow:

```text
settings -> repositories -> services -> app.state -> routers
```

#### Part 3 — One todo request (4 minutes)

Create flow explain:

```text
CreateTodoRequest
 -> CreateTodoInput
 -> TodoService
 -> TodoItem
 -> TodoRepository
 -> selected DB adapter
 -> TodoOutput
 -> TodoResponse
```

#### Part 4 — Authentication files (3 minutes)

Explain:

1. `domain/auth.py` contract;
2. `AuthService` workflow;
3. `dependencies.current_user`;
4. `AuthSecurity`;
5. one selected auth repository.

#### Part 5 — Three adapters (3 minutes)

Same methods compare:

```text
save:
  Firestore -> PATCH
  MongoDB   -> replace_one(upsert)
  PostgreSQL -> INSERT ON CONFLICT
```

#### Part 6 — Close (1 minute)

> “Routes and services same rehti hain. Factory sirf concrete database adapter
> change karti hai. Isi liye structure maintainable and database-independent
> hai.”

---

## 17. File-focused viva questions

### Q1. Root `main.py` aur `app/main.py` dono kyun?

Root file simple Uvicorn/direct-run bridge hai. `app/main.py` real composition
root hai jahan complete application wire hoti hai.

### Q2. Composition root kya hai?

Woh central place jahan concrete repositories, services, middleware and routers
connect hote hain. Is project mein `app/main.py` composition root hai.

### Q3. `config.py` alag kyun?

External configuration one typed place par rehti hai. Baqi files raw environment
variables directly read nahi kartin.

### Q4. `get_settings()` cache kyun hoti hai?

`.env` every request par read nahi hoti aur process ke andar stable settings
object use hota hai.

### Q5. `logging.py` mein `ContextVar` kyun?

Concurrent requests ke log labels mix hone se bachata hai.

### Q6. Domain mein repository interfaces kyun hain?

Woh business/application ko required persistence language deti hain without
concrete database dependency.

### Q7. `TaskTitle` separate class kyun?

Title validation reusable invariant ban jati hai. Invalid title ke sath entity
create/restore nahi hoti.

### Q8. Completion rule `TodoService` ke bajaye entity mein kyun?

Already-completed todo ko rokna business behavior hai. Entity ke andar rakhne se
har entry point same rule follow karta hai.

### Q9. DTO aur entity mein difference?

DTO layers ke darmiyan data carry karta hai. Entity identity, state and business
behavior rakhti hai.

### Q10. Presentation request/response schema aur application DTO dono kyun?

Schemas HTTP/Pydantic contract hain. Application DTOs framework-independent
use-case contract hain.

### Q11. `app.state` kyun?

Startup par ready services app instance par store hoti hain. Dependencies same
configured services request routes ko deti hain.

### Q12. `current_user` function kya karti hai?

Bearer token leti hai, `AuthService.authenticate` call karti hai aur verified
UID/email ka `CurrentUser` return karti hai.

### Q13. Client owner UID kyun nahi bhejta?

Client value spoof kar sakta hai. Owner UID verified token se milti hai.

### Q14. Route directly repository kyun call nahi karti?

Route HTTP concern rakhti hai; service complete use-case order coordinate karti
hai. Direct call layers ko tightly couple kar deta.

### Q15. `repository_factory.py` ka main kaam?

Active `DATABASE` ke according matching todo and auth concrete adapters create
karna.

### Q16. Same factory auth aur todos dono kyun return karti hai?

Guarantee hoti hai ke user account aur uske todos same selected database use
kar rahe hain.

### Q17. `AuthSecurity` separate kyun?

Three auth repositories same hashing/token rules reuse karti hain. Algorithm
duplicate nahi hota.

### Q18. Firestore `_to_document` and `_to_entity` kyun?

Firestore REST typed field format aur domain entity ka structure different hai;
mapping helpers conversion isolate karti hain.

### Q19. MongoDB `replace_one(..., upsert=True)` kyun?

Same repository `save` method new todo insert aur completed todo update dono
handle karti hai.

### Q20. PostgreSQL `ON CONFLICT` kyun?

ID missing ho toh insert, existing ho toh state update. Yeh SQL upsert hai.

### Q21. Repository query mein owner UID kyun?

ID ke sath owner match cross-user read/update/delete ko block karta hai.

### Q22. Firestore todo path user UID ke neeche kyun?

Todos naturally owner ke under group hote hain aur path itself ownership scope
provide karta hai.

### Q23. MongoDB indexes kahan bante hain?

`MongoAuthRepository` email unique index aur `MongoTodoRepository` owner UID
index constructor mein create karti hain.

### Q24. PostgreSQL tables kahan create hoti hain?

Auth and todo repository constructors apni `_create_table()` methods call karti
hain.

### Q25. Nested empty `__init__.py` files kyun delete ki?

Un mein exports ya initialization nahi thi. Root `app/__init__.py` explicit
package marker hai; Python 3 nested folders ko namespace packages ke through
import karta hai.

### Final answer formula

Kisi bhi file ka answer is order mein dein:

```text
File kis layer mein hai
 -> file ka purpose
 -> important class/function
 -> input
 -> kis ko call karti hai
 -> return/output
 -> yahan rakhne ka reason
```

Example:

> “`todo_service.py` application layer mein hai. Is mein `TodoService` create,
> list, complete and delete workflows coordinate karti hai. Yeh input DTO leti
> hai, domain entity behavior call karti hai, `TodoRepository` contract ke
> through persistence karwati hai aur `TodoOutput` return karti hai. Is file
> mein HTTP ya database-specific code nahi hai.”
