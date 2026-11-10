# TodoFlow DDD Backend — Complete Presentation Guide

> **Purpose:** Yeh guide backend ko sirf run karne ke liye nahi, balki uski
> architecture, har folder, har file, important class/function, database flow,
> authentication, security aur design decisions ko confidently explain karne
> ke liye hai.
>
> **Presentation language:** Simple English + Roman Urdu.
>
> **Important:** Real passwords, `.env` secrets, PostgreSQL password aur Firebase
> service-account key presentation ya GitHub par kabhi show na karein.

---

## Table of contents

1. [One-minute project summary](#1-one-minute-project-summary)
2. [Backend kis problem ko solve karta hai?](#2-backend-kis-problem-ko-solve-karta-hai)
3. [DDD architecture ka basic idea](#3-ddd-architecture-ka-basic-idea)
4. [Complete folder and file structure](#4-complete-folder-and-file-structure)
5. [Dependency direction — sab se important rule](#5-dependency-direction--sab-se-important-rule)
6. [Application startup flow](#6-application-startup-flow)
7. [Root and shared files](#7-root-and-shared-files)
8. [Domain layer — business ka heart](#8-domain-layer--business-ka-heart)
9. [Application layer — use-case coordination](#9-application-layer--use-case-coordination)
10. [Presentation layer — HTTP boundary](#10-presentation-layer--http-boundary)
11. [Infrastructure layer — real technical implementations](#11-infrastructure-layer--real-technical-implementations)
12. [Firestore implementation](#12-firestore-implementation)
13. [MongoDB implementation](#13-mongodb-implementation)
14. [PostgreSQL implementation](#14-postgresql-implementation)
15. [Authentication and security deep dive](#15-authentication-and-security-deep-dive)
16. [Complete request flows](#16-complete-request-flows)
17. [API endpoints and error codes](#17-api-endpoints-and-error-codes)
18. [Database structures and record shapes](#18-database-structures-and-record-shapes)
19. [Database switching](#19-database-switching)
20. [Logging system](#20-logging-system)
21. [Tests and verification](#21-tests-and-verification)
22. [Live presentation/demo plan](#22-live-presentationdemo-plan)
23. [Design decisions: why this approach?](#23-design-decisions-why-this-approach)
24. [Current limitations and production improvements](#24-current-limitations-and-production-improvements)
25. [Viva/interview questions with answers](#25-vivainterview-questions-with-answers)
26. [Final quick-revision sheet](#26-final-quick-revision-sheet)

---

## 1. One-minute project summary

### Presentation mein yeh bol sakte hain

> “TodoFlow ka backend FastAPI aur Domain-Driven Design principles use karta
> hai. Code ko Domain, Application, Presentation aur Infrastructure layers mein
> separate kiya gaya hai. Domain layer todo ke business rules rakhti hai.
> Application layer use cases coordinate karti hai. Presentation layer HTTP
> requests, validation aur status codes handle karti hai. Infrastructure layer
> Firestore, MongoDB aur PostgreSQL ki actual implementation deti hai.
>
> Terminal se `DATABASE` change karne par users aur todos dono ka database
> switch hota hai. Har database mein account separate hota hai. Password plain
> text mein save nahi hota; salted PBKDF2 hash save hota hai. Login par signed,
> database-bound token milta hai. Isi wajah se MongoDB ka token PostgreSQL ya
> Firestore mein accept nahi hota. Repository contracts ki wajah se domain aur
> application code database switch hone par change nahi hota.”

### Project ki main strengths

- Clear DDD layer boundaries.
- Same API with three databases.
- Same selected database stores both users and todos.
- Database-specific users and tokens.
- Password hashing; plain passwords are never stored.
- Owner-based todo isolation.
- Typed `.env` configuration.
- Dependency injection through FastAPI.
- Bilingual request-flow logs.
- Automated domain/security tests.

---

## 2. Backend kis problem ko solve karta hai?

Todo application technically simple CRUD lag sakti hai, lekin backend ko yeh
important problems solve karne hote hain:

1. User signup aur login.
2. Password ko safely store karna.
3. Request bhejne wale user ki identity verify karna.
4. Har todo ko correct owner ke sath associate karna.
5. User A ko User B ke todos se isolate karna.
6. Todo title aur priority validate karna.
7. Completed task ko dobara complete hone se rokna.
8. Firestore, MongoDB aur PostgreSQL ko same API ke peeche support karna.
9. Database switch karte waqt business code ko unchanged rakhna.
10. Request ka complete flow terminal logs mein visible rakhna.

### Core business statement

> An authenticated user can create, list, complete and delete only their own
> valid todos. The active database owns both that user account and those todos.

---

## 3. DDD architecture ka basic idea

DDD ka full form **Domain-Driven Design** hai. Iska focus framework ya database
par nahi, business concepts aur rules par hota hai.

TodoFlow mein important domain concepts yeh hain:

- `TodoItem`
- `TaskTitle`
- `Priority`
- Todo completion rule
- Todo ownership
- Repository contracts

### Four major layers

| Layer | Main responsibility | Simple explanation |
|---|---|---|
| Domain | Business rules and contracts | “System ke asli rules kya hain?” |
| Application | Use-case coordination | “Ek complete workflow kis order mein chalega?” |
| Presentation | HTTP input/output | “Client request ko kaise receive/respond karna hai?” |
| Infrastructure | Database/security implementation | “Data technically kahan aur kaise save hoga?” |

### Layer mein kya nahi hona chahiye?

| Layer | Is layer mein nahi hona chahiye |
|---|---|
| Domain | FastAPI, Pydantic HTTP models, MongoDB, SQL, Firestore URLs, `.env` |
| Application | HTTP status codes, SQL queries, PyMongo calls, Firestore requests |
| Presentation | SQL, database collection/table logic, password hashing |
| Infrastructure | HTTP route definitions, UI response schemas, todo business rules |

### DDD ka main benefit

Database change hone par `TodoItem.complete()` ya `TodoService.create()` change
nahi hota. Sirf concrete repository adapter change hota hai.

---

## 4. Complete folder and file structure

```text
backend/DDD/
|-- main.py
|-- .env                    # Local secrets/config; Git ignored
|-- .env.example            # Safe configuration template
|-- requirements.txt
|-- README.md
|-- ARCHITECTURE.md
|-- BACKEND_PRESENTATION_GUIDE.md
|-- serviceAccountKey.json  # Firestore credential; Git ignored
|
|-- app/
|   |-- __init__.py
|   |-- main.py
|   |-- config.py
|   |-- logging.py
|   |
|   |-- domain/
|   |   |-- __init__.py
|   |   |-- auth.py
|   |   `-- todo.py
|   |
|   |-- application/
|   |   |-- __init__.py
|   |   |-- dto.py
|   |   |-- auth_service.py
|   |   `-- todo_service.py
|   |
|   |-- presentation/
|   |   |-- __init__.py
|   |   |-- schemas.py
|   |   |-- dependencies.py
|   |   `-- routers/
|   |       |-- __init__.py
|   |       |-- auth.py
|   |       `-- todos.py
|   |
|   `-- infrastructure/
|       |-- __init__.py
|       |-- security.py
|       |-- repository_factory.py
|       |
|       |-- firestore/
|       |   |-- __init__.py
|       |   |-- auth_repository.py
|       |   `-- todo_repository.py
|       |
|       |-- mongodb/
|       |   |-- __init__.py
|       |   |-- auth_repository.py
|       |   `-- todo_repository.py
|       |
|       `-- postgresql/
|           |-- __init__.py
|           |-- auth_repository.py
|           `-- todo_repository.py
|
`-- tests/
    `-- test_domain_and_security.py
```

### Folder naming ka reason

- `domain/`: pure business language.
- `application/`: workflows/use cases.
- `presentation/`: external HTTP interface.
- `infrastructure/`: external technical systems.
- `routers/`: endpoint files grouped by API feature.
- Har database ka apna folder: database-specific code mix nahi hota.
- `auth_repository.py` aur `todo_repository.py` separate: dono different
  repository contracts implement karte hain.

### `__init__.py` files kya karti hain?

`__init__.py` Python ko batati hai ke folder ek regular Python package hai.
In files mein business logic nahi rakhi gayi. Yeh intentional hai: package
marker simple rehta hai aur import ke time hidden side effects nahi deta.

### Every file at a glance

Yeh table ensure karti hai ke project ki koi important file unexplained na rahe:

| File | What | Why / responsibility |
|---|---|---|
| `main.py` | Root Uvicorn/Python entrypoint | Beginner command ko simple rakhta hai |
| `.env` | Real local configuration | Secrets aur machine-specific URLs; Git ignored |
| `.env.example` | Safe configuration template | Required settings document karta hai |
| `requirements.txt` | Python package list | Reproducible environment setup |
| `README.md` | Backend run/structure guide | New developer onboarding |
| `ARCHITECTURE.md` | Research and placement rules | Proof ke sath layer boundaries freeze karta hai |
| `BACKEND_PRESENTATION_GUIDE.md` | Current detailed guide | Presentation, revision and viva preparation |
| `serviceAccountKey.json` | Firestore service credential | Firestore REST authorization; Git ignored |
| `app/__init__.py` | Root package marker | `app.*` imports enable karta hai |
| `app/main.py` | Composition root | FastAPI, repositories, services, routers wire karta hai |
| `app/config.py` | Typed settings | `.env`/terminal config centralize karta hai |
| `app/logging.py` | Bilingual trace logger | Request flow and timing visible karta hai |
| `app/domain/__init__.py` | Domain package marker | Domain modules ko package banata hai |
| `app/domain/auth.py` | Auth contract/data/error | DB-independent auth language |
| `app/domain/todo.py` | Todo entity/rules/contract | Core business logic |
| `app/application/__init__.py` | Application package marker | Use-case modules organize karta hai |
| `app/application/dto.py` | Input/output DTOs | Layers ke darmiyan plain data transfer |
| `app/application/auth_service.py` | Auth workflows | Repository operations coordinate karta hai |
| `app/application/todo_service.py` | Todo workflows | Domain behavior + persistence coordinate karta hai |
| `app/presentation/__init__.py` | Presentation package marker | HTTP modules organize karta hai |
| `app/presentation/schemas.py` | Pydantic HTTP models | Request/response validation contract |
| `app/presentation/dependencies.py` | Service/current-user dependencies | FastAPI DI and authentication boundary |
| `app/presentation/routers/__init__.py` | Router package marker | Endpoint modules group karta hai |
| `app/presentation/routers/auth.py` | Signup/login endpoints | HTTP auth input/output mapping |
| `app/presentation/routers/todos.py` | Todo endpoints | Protected HTTP todo workflows |
| `app/infrastructure/__init__.py` | Infrastructure package marker | Technical adapters group karta hai |
| `app/infrastructure/security.py` | Hashing/token implementation | Shared DB-independent technical security |
| `app/infrastructure/repository_factory.py` | Adapter selection/wiring | Matching auth + todo repositories guarantee karta hai |
| `app/infrastructure/firestore/__init__.py` | Firestore package marker | Firestore adapters group karta hai |
| `app/infrastructure/firestore/auth_repository.py` | Firestore auth adapter | Firestore users/password/token flow |
| `app/infrastructure/firestore/todo_repository.py` | Firestore todo adapter | Firestore todo CRUD/mapping |
| `app/infrastructure/mongodb/__init__.py` | MongoDB package marker | Mongo adapters group karta hai |
| `app/infrastructure/mongodb/auth_repository.py` | Mongo auth adapter | `users` collection auth flow |
| `app/infrastructure/mongodb/todo_repository.py` | Mongo todo adapter | `todos` collection CRUD/mapping |
| `app/infrastructure/postgresql/__init__.py` | PostgreSQL package marker | PostgreSQL adapters group karta hai |
| `app/infrastructure/postgresql/auth_repository.py` | PostgreSQL auth adapter | `users` table auth flow |
| `app/infrastructure/postgresql/todo_repository.py` | PostgreSQL todo adapter | `todos` table CRUD/mapping |
| `tests/test_domain_and_security.py` | Focused automated tests | Rules and auth security regression protection |

---

## 5. Dependency direction — sab se important rule

```text
Presentation  ---> Application ---> Domain
Infrastructure -------------------> Domain
app/main.py ---> Presentation + Application + Infrastructure
```

### Is diagram ka matlab

- Presentation application services ko call kar sakti hai.
- Application domain entities aur repository contracts ko use karti hai.
- Infrastructure domain repository contracts implement karti hai.
- Domain kisi outer layer ko import nahi karti.
- `app/main.py` composition root sab concrete objects ko connect karta hai.

### Dependency inversion

`TodoService` directly `MongoTodoRepository` par depend nahi karta. Woh abstract
`TodoRepository` contract par depend karta hai.

```text
TodoService ---> TodoRepository contract <--- MongoTodoRepository
                                    <--- FirestoreTodoRepository
                                    <--- PostgreSQLTodoRepository
```

Isi ko Dependency Inversion kehte hain: high-level workflow concrete low-level
database ke bajaye abstraction par depend karta hai.

---

## 6. Application startup flow

Jab command chalti hai:

```powershell
python -m uvicorn main:app --reload
```

toh startup steps yeh hain:

```text
1. Uvicorn root main.py import karta hai
2. root main.py app.main se app import karta hai
3. app/main.py create_app() call karta hai
4. get_settings() .env + terminal variables read karta hai
5. FastAPI object create hota hai
6. CORS middleware add hota hai
7. request logging middleware install hota hai
8. repository_factory selected DATABASE read karti hai
9. matching TodoRepository + AuthRepository bante hain
10. repositories AuthService aur TodoService mein inject hote hain
11. services app.state par store hoti hain
12. auth aur todo routers include hote hain
13. health endpoint register hota hai
14. backend requests receive karne ke liye ready hota hai
```

### Why startup wiring one place par hai?

Concrete database selection ek technical decision hai. Agar har route apna
repository create kare toh connections duplicate honge aur routes database se
tightly coupled ho jayengi. Composition root wiring ko centralized rakhta hai.

---

## 7. Root and shared files

### 7.1 `main.py` — beginner-compatible entrypoint

Path: [`main.py`](../backend/DDD/main.py)

#### What?

Root entrypoint jo do commands support karta hai:

```powershell
python -m uvicorn main:app --reload
python main.py
```

#### Why?

Professional app implementation `app/main.py` mein hai, lekin beginner ko long
module path ya package-install step yaad na rakhna pade. Root file ek thin bridge
hai.

#### Inside kya hai?

- `get_settings` import.
- `app` aur `create_app` import.
- `__all__`: public exports clear karta hai.
- `if __name__ == "__main__"`: direct Python execution handle karta hai.
- `uvicorn.run(...)`: host, port aur reload typed settings se leta hai.

#### Important explanation

`if __name__ == "__main__"` block import ke waqt execute nahi hota. Sirf
`python main.py` par chalta hai. `uvicorn main:app` mein Uvicorn exported `app`
object use karta hai.

---

### 7.2 `app/main.py` — composition root

Path: [`app/main.py`](../backend/DDD/app/main.py)

#### What?

Complete FastAPI application create aur wire karta hai.

#### Why?

Kisi ek central jagah ko pata hona chahiye ke concrete repositories kaunsi hain,
services kaise banti hain aur routes kaise include hote hain. Baqi layers ko
yeh knowledge nahi di jati.

#### `create_app(settings=None)`

What:

- FastAPI app create karta hai.
- Optional `Settings` accept karta hai.
- Middleware, repositories, services aur routers connect karta hai.

Why optional settings?

- Normal run mein cached `.env` settings use hoti hain.
- Tests mein `database="mongodb"` jaisi custom setting inject ki ja sakti hai.

How:

1. `settings or get_settings()`.
2. `FastAPI(title=settings.app_name)`.
3. CORS middleware configure.
4. Logging middleware install.
5. `create_repositories(settings)` returns two matching repositories.
6. `TodoService(todo_repository)`.
7. `AuthService(auth_repository)`.
8. Services `app.state` par save.
9. Routers include.
10. Health endpoint create.

#### `app.state` kyun?

`app.state` application lifetime ke shared configured objects store karta hai.
Routes directly globals import nahi karti. FastAPI dependency functions request
ke through app se correct service read karti hain. Is se testing aur dependency
replacement easier hoti hai.

#### Health endpoint

```http
GET /
```

Example response:

```json
{
  "status": "ok",
  "architecture": "DDD",
  "database": "postgresql"
}
```

Is endpoint se quickly verify hota hai ke backend running hai aur kaunsa
database selected hai.

---

### 7.3 `app/config.py` — typed configuration

Path: [`app/config.py`](../backend/DDD/app/config.py)

#### What?

`.env` aur terminal environment variables ko one typed `Settings` object mein
load karta hai.

#### Why?

Raw `os.environ` poore project mein use karne se:

- spelling mistakes late detect hoti hain;
- integers/booleans strings rehte hain;
- configuration scattered ho jati hai;
- testing hard hoti hai.

Typed settings startup par values convert aur validate karti hain.

#### `BASE_DIRECTORY`

Backend DDD folder ka absolute path calculate karta hai. Is se `.env` aur
relative Firebase credential path current terminal folder par depend nahi karte.

#### `Settings(BaseSettings)` fields

| Group | Fields | Purpose |
|---|---|---|
| App | `app_name`, `app_architecture` | API metadata |
| Server | `backend_host`, `backend_port`, `backend_reload` | Uvicorn settings |
| HTTP | `cors_origins` | Allowed frontend origins |
| Logging | `log_level` | Terminal verbosity |
| Auth | `auth_token_secret`, `auth_token_expire_minutes` | Signed token security |
| Selection | `database` | Active database |
| MongoDB | URI, DB, user/todo collections | Mongo connection/storage |
| PostgreSQL | `postgresql_url` | PostgreSQL connection |
| Firestore | credentials, API URL, database/collection names | Firestore REST access |

#### `model_config`

- `.env` file location define karta hai.
- UTF-8 encoding use karta hai.
- Environment names case-insensitive hain.
- Old/extra `.env` keys ignore hoti hain.
- Terminal variables `.env` ko override kar sakti hain.

#### `selected_database`

- whitespace remove karta hai;
- lowercase karta hai;
- `firebase` alias ko `firestore` banata hai;
- unsupported value par clear error deta hai.

#### `allowed_origins`

Comma-separated CORS string ko clean list mein convert karta hai.

#### `firebase_credential_file`

Relative credential path ko backend folder ke against absolute banata hai.

#### `get_settings()` and `@lru_cache`

Settings ko ek baar read karke cache karta hai. Har request par `.env` dobara
read nahi hoti. New backend process start hone par fresh settings load hoti hain.

---

### 7.4 `app/logging.py` — bilingual request tracing

Path: [`app/logging.py`](../backend/DDD/app/logging.py)

#### What?

Request start/end, layer steps, errors aur duration terminal mein print karta hai.

#### Why custom logger?

Normal access log sirf `POST /todos 201` batata hai. Learning/presentation ke
liye humein yeh bhi dekhna hai:

```text
Presentation -> Auth -> Application -> Infrastructure -> Response
```

#### Important parts

##### Named logger

`logging.getLogger("todoflow.ddd")` separate application logger banata hai.
`propagate=False` duplicate root logger output rokta hai.

##### Stream handler

Logs `stdout` par formatted time, level aur message ke sath print hote hain.

##### `_request_number`

Har request ko `#001`, `#002` jaisa sequential number deta hai.

##### `_current_request: ContextVar`

Concurrent requests ke logs ko correct request identity ke sath rakhta hai.
Global normal variable use hota toh parallel requests ek doosre ka label
overwrite kar sakti thin.

##### `log_step(area, english, roman_urdu)`

Layer ka bilingual successful/important step print karta hai.

##### `log_error(area, message)`

Safe technical error print karta hai. Password aur token callers log mein pass
nahi karte.

##### `install_request_logging(app)`

FastAPI middleware install karta hai jo:

1. request label banata hai;
2. start time save karta hai;
3. response status/duration log karta hai;
4. exception par 500 trace log karta hai;
5. finally block mein request context reset karta hai.

`OPTIONS` skip hoti hai kyun ke woh browser ki CORS preflight background
request hoti hai aur main learning flow ko noisy banati hai.

---

### 7.5 `.env.example` — configuration contract

Path: [`.env.example`](../backend/DDD/.env.example)

#### What?

Safe template jo batata hai application ko kaunse environment variables chahiye.

#### Why `.env.example` commit hoti hai lekin `.env` nahi?

- `.env.example`: variable names + fake/sample values; safe to share.
- `.env`: real connection strings/secrets; `.gitignore` mein hai.

#### Important security rule

Kabhi yeh commit/show na karein:

- Real `AUTH_TOKEN_SECRET`
- PostgreSQL password
- Remote MongoDB credentials
- `serviceAccountKey.json`

---

### 7.6 `requirements.txt` — dependency list

Path: [`requirements.txt`](../backend/DDD/requirements.txt)

| Package | Why needed? |
|---|---|
| `fastapi` | API routes, dependencies, middleware, validation integration |
| `uvicorn` | ASGI server jo FastAPI app run karta hai |
| `pydantic[email]` | Request/response validation and `EmailStr` |
| `pydantic-settings` | Typed `.env` settings |
| `firebase-admin` | Firestore service-account credentials |
| `requests` | HTTPS stack used for Firestore REST access |
| `python-dotenv` | `.env` file loading support |
| `pymongo` | MongoDB driver |
| `psycopg[binary]` | PostgreSQL driver |

---

## 8. Domain layer — business ka heart

Domain folder ka code framework-independent hai. Agar kal FastAPI ko kisi aur
framework se replace kar dein, domain rules phir bhi same reh sakte hain.

### 8.1 `app/domain/auth.py`

Path: [`app/domain/auth.py`](../backend/DDD/app/domain/auth.py)

#### File ka purpose

Authentication ka database-independent data model aur repository contract.

#### `ValidationException`

Safe authentication/input error hai jo presentation layer client ko return kar
sakti hai.

Examples:

- email already registered;
- wrong email/password;
- expired token;
- token selected database ka nahi;
- token user database mein exist nahi karta.

#### `UserData`

Frozen dataclass:

```text
uid
email
token
```

Why frozen?

Authenticated result ko accidental mutation se protect karta hai. Repository
result application layer tak consistent form mein jata hai, chahe source
Firestore, MongoDB ya PostgreSQL ho.

#### `AuthRepository(ABC)`

Abstract contract jisme three required operations hain:

| Method | Meaning |
|---|---|
| `signup(email, password, name)` | Selected DB mein account create karo |
| `login(email, password)` | Selected DB credentials verify karo |
| `authenticate(token)` | Token verify karo aur DB user existence confirm karo |

`ABC` aur `@abstractmethod` ensure karte hain ke concrete repository incomplete
na ho. Har auth adapter ko yeh three methods implement karne padte hain.

#### Presentation line

> “Domain Firebase, MongoDB ya PostgreSQL ko nahi janta. Woh sirf kehta hai ke
> mujhe signup, login aur authenticate capability chahiye.”

---

### 8.2 `app/domain/todo.py`

Path: [`app/domain/todo.py`](../backend/DDD/app/domain/todo.py)

#### File ka purpose

Todo entity, value objects, business exceptions aur storage contract.

#### Exception hierarchy

```text
DomainError
|-- InvalidTaskTitleError
|-- TaskAlreadyCompletedError
`-- TodoNotFoundError
```

Why parent `DomainError`?

Presentation layer general todo business failures ko HTTP 400 mein convert kar
sakti hai, jabke specific not-found error ko HTTP 404 diya ja sakta hai.

#### `Priority(str, Enum)`

Allowed values:

- `LOW`
- `MEDIUM`
- `HIGH`

`str` mixin ki wajah se enum API/database string values ke sath easy work karta
hai. Random priority value domain mein enter nahi kar sakti.

#### `TaskTitle` value object

Frozen dataclass jo valid title guarantee karti hai.

`__post_init__` flow:

1. `None`/empty safety.
2. leading/trailing whitespace remove.
3. minimum 3 characters.
4. maximum 120 characters.
5. frozen object ke andar cleaned value set.

Why value object?

Validation sirf route mein hoti toh database se restore ki hui entity ya future
non-HTTP use case invalid title create kar sakta tha. Domain value object har
entry path par same invariant enforce karta hai.

#### `TodoItem` entity

Fields:

| Field | Meaning |
|---|---|
| `id` | Unique UUID string |
| `title` | Validated `TaskTitle` |
| `priority` | `Priority` enum |
| `is_completed` | Current completion state |
| `created_at` | UTC creation time |
| `owner_uid` | Authenticated owner identity |
| `completed_at` | Completion UTC time or `None` |

Entity kyun?

Todo ki unique identity hoti hai aur state time ke sath change hoti hai. Isliye
yeh value object nahi, entity hai.

#### `TodoItem.create(...)`

Factory method new todo ko valid initial state mein banata hai:

- UUID generate;
- title validate;
- priority uppercase + enum validate;
- `is_completed=False`;
- UTC creation time;
- verified owner UID attach.

Factory ka benefit: code ke multiple places par initial-state logic repeat nahi
hoti.

#### `TodoItem.complete()`

Business behavior entity ke andar hai:

1. already completed ho toh `TaskAlreadyCompletedError`;
2. otherwise `is_completed=True`;
3. `completed_at=UTC now`.

Important point:

> Complete rule database query ya route mein nahi; entity mein hai. Har database
> par same rule automatically apply hota hai.

#### `TodoRepository(ABC)`

Required methods:

| Method | Purpose |
|---|---|
| `save(todo)` | New/current state persist karo |
| `get_by_id(todo_id, owner_uid)` | Sirf owner ka matching todo return karo |
| `get_by_owner(owner_uid)` | Current user ke tamam todos |
| `delete(todo_id, owner_uid)` | Sirf owned todo delete karo |

`owner_uid` contract ka part kyun hai?

Ownership filtering optional route behavior nahi, repository operation ka part
ban jati hai. Is se adapter accidentally sirf `todo_id` par operation nahi karta.

---

## 9. Application layer — use-case coordination

Application layer business rules invent nahi karti. Woh domain aur repository
operations ko correct order mein coordinate karti hai.

### 9.1 `app/application/dto.py`

Path: [`app/application/dto.py`](../backend/DDD/app/application/dto.py)

#### DTO kya hota hai?

DTO = **Data Transfer Object**. Yeh layer boundary cross karne ke liye simple
data container hota hai.

#### Input DTOs

| DTO | Fields | Used by |
|---|---|---|
| `SignupInput` | email, password, display_name | `AuthService.signup` |
| `LoginInput` | email, password | `AuthService.login` |
| `CreateTodoInput` | title, priority, owner_uid | `TodoService.create` |
| `TodoActionInput` | todo_id, owner_uid | complete/delete |

#### Output DTOs

| DTO | Purpose |
|---|---|
| `AuthOutput` | uid/email/token presentation ko dena |
| `TodoOutput` | entity ko API-friendly strings mein dena |

#### Pydantic schemas se separate kyun?

Presentation Pydantic HTTP models use karti hai. Application DTOs plain frozen
dataclasses hain. Is se application FastAPI/Pydantic par depend nahi karti.

---

### 9.2 `app/application/auth_service.py`

Path: [`app/application/auth_service.py`](../backend/DDD/app/application/auth_service.py)

#### `AuthService`

Authentication workflows coordinate karta hai without knowing selected DB.

#### Constructor

```python
AuthService(repository: AuthRepository)
```

Repository dependency inject hoti hai. Firestore/Mongo/PostgreSQL selection
service ke bahar hoti hai.

#### `signup(data)`

1. Input DTO values repository ko deta hai.
2. Repository account create/hash/token work karti hai.
3. Application bilingual completion log karti hai.
4. `AuthOutput` return hota hai.

#### `login(data)`

1. Email/password repository ko.
2. Repository credentials verify karti hai.
3. Application completion log.
4. `AuthOutput`.

#### `authenticate(token)`

Protected request ke token ko selected repository ke through verify karta hai.

#### `_to_output(...)`

Repository `UserData` ko application `AuthOutput` mein map karta hai. Yeh
mapping outer layer ko repository-specific object directly expose nahi karti.

---

### 9.3 `app/application/todo_service.py`

Path: [`app/application/todo_service.py`](../backend/DDD/app/application/todo_service.py)

#### `to_output(todo)`

Domain `TodoItem` ko serializable `TodoOutput` banata hai:

- enum to string;
- datetime to ISO string;
- missing completion time to `None`.

Domain entity ko directly API response kyun nahi banaya?

Domain ko transport/JSON format ka knowledge nahi hona chahiye. Mapping
application boundary par hoti hai.

#### `TodoService`

Four main workflows:

##### `create(data)`

```text
CreateTodoInput
 -> TodoItem.create() domain validation
 -> repository.save()
 -> log
 -> TodoOutput
```

##### `list(owner_uid)`

- repository se only owner todos;
- count log;
- each entity ko output DTO.

##### `complete(data)`

- owned todo find;
- domain `complete()` behavior;
- updated entity save;
- output return.

##### `delete(data)`

- existence/ownership verify;
- repository delete;
- log.

##### `_get_todo_or_fail(data)`

Complete aur delete ka repeated ownership/not-found check one helper mein rakhta
hai. Missing todo par `TodoNotFoundError`.

Why read before delete?

Repository delete silently zero rows/documents affect kar sakti hai. Pehle read
karne se API proper 404 return kar sakti hai aur ownership explicitly verify
hoti hai.

---

## 10. Presentation layer — HTTP boundary

Presentation layer client-facing details handle karti hai:

- URL/method;
- JSON validation;
- Bearer token extraction;
- dependency injection;
- HTTP status codes;
- response schemas.

### 10.1 `app/presentation/schemas.py`

Path: [`app/presentation/schemas.py`](../backend/DDD/app/presentation/schemas.py)

Pydantic HTTP models:

#### `SignupRequest`

- valid `EmailStr` required;
- password minimum 6;
- display name default `User`.

#### `LoginRequest`

- valid email;
- password minimum 6.

#### `AuthResponse`

- UID;
- normalized email;
- token;
- user-friendly message.

#### `CreateTodoRequest`

- title 3–120 at API edge;
- priority `LOW/MEDIUM/HIGH`, uppercase/lowercase accepted;
- default `MEDIUM`.

Domain title validation phir bhi kyun hai?

Pydantic early HTTP feedback deta hai. Domain validation business invariant
guarantee karti hai. Dono different boundaries protect karte hain.

#### `TodoResponse`

API contract define karta hai. FastAPI `response_model` ke through output shape
validate/document karta hai.

---

### 10.2 `app/presentation/dependencies.py`

Path: [`app/presentation/dependencies.py`](../backend/DDD/app/presentation/dependencies.py)

#### `CurrentUser`

Verified request identity: UID + email.

#### `HTTPBearer`

`Authorization: Bearer <token>` header parse karta hai. Missing header protected
route ko reject karta hai.

#### `get_auth_service(request)`

`request.app.state.auth_service` return karta hai.

#### `get_todo_service(request)`

`request.app.state.todo_service` return karta hai.

#### Annotated dependency aliases

```text
AuthServiceDep
TodoServiceDep
CredentialsDep
CurrentUserDep
```

Why aliases?

Routes readable rehti hain aur repeated `Annotated[..., Depends(...)]` syntax
har function mein nahi likhni padti. Type information editor/autocomplete ke liye
preserve rehti hai.

#### `current_user(...)`

Protected request security flow:

1. HTTPBearer token extract.
2. `AuthService.authenticate(token)`.
3. Selected DB token signature/database/expiry check.
4. Selected DB mein user existence check.
5. `CurrentUser` return.
6. Validation error -> HTTP 401.
7. Unexpected error -> safe generic HTTP 401 + technical log.

Critical security decision:

> `owner_uid` request body se nahi li jati. Verified token se aati hai. Client
> kisi aur UID ko body mein bhej kar ownership spoof nahi kar sakta.

---

### 10.3 `app/presentation/routers/auth.py`

Path: [`app/presentation/routers/auth.py`](../backend/DDD/app/presentation/routers/auth.py)

#### Router setup

```text
prefix = /auth
tag = Auth
```

Swagger mein auth endpoints group hote hain.

#### `POST /auth/signup`

1. `SignupRequest` validate.
2. presentation log.
3. request schema -> `SignupInput`.
4. `AuthService.signup`.
5. service output -> `AuthResponse`.
6. success status 201.
7. `ValidationException` -> HTTP 400.

#### `POST /auth/login`

1. `LoginRequest` validate.
2. service login.
3. `AuthResponse` with token.
4. invalid credentials -> HTTP 401.

Why route mein database code nahi?

Route ka kaam HTTP mapping hai. Agar route PyMongo/SQL use kare toh database
switch aur route testing difficult ho jati hai.

---

### 10.4 `app/presentation/routers/todos.py`

Path: [`app/presentation/routers/todos.py`](../backend/DDD/app/presentation/routers/todos.py)

#### Router setup

```text
prefix = /todos
tag = Todos
```

#### `GET /todos`

- `CurrentUserDep` token verify karta hai;
- verified UID service ko milti hai;
- only current user's todos return.

#### `POST /todos`

- request title/priority validate;
- verified UID attach;
- `CreateTodoInput` create;
- service call;
- success 201;
- domain error 400.

#### `PATCH /todos/{todo_id}/complete`

- path se todo ID;
- token se owner UID;
- service ownership check + domain complete rule;
- not found 404;
- already completed 400;
- success 200.

#### `DELETE /todos/{todo_id}`

- owner verify;
- delete;
- success 204 No Content;
- not found 404.

#### Why sync `def` routes?

Current MongoDB and PostgreSQL drivers synchronous hain. FastAPI normal `def`
path functions ko threadpool mein run karta hai, isliye event loop directly
block nahi hota. Future fully async drivers use hon toh routes/services async
design mein migrate ki ja sakti hain.

---

## 11. Infrastructure layer — real technical implementations

Infrastructure external details rakhti hai:

- password hashing;
- token signing;
- Firestore REST;
- PyMongo;
- Psycopg/SQL;
- concrete repository creation.

### 11.1 `app/infrastructure/security.py`

Path: [`app/infrastructure/security.py`](../backend/DDD/app/infrastructure/security.py)

#### `AuthSecurity`

What:

- email normalize;
- password hash/verify;
- signed token create/read.

Why shared?

All databases ko exactly same password/token security rules chahiye. Logic ko
three repositories mein repeat karna inconsistent aur error-prone hota.

#### `PASSWORD_ITERATIONS = 120_000`

PBKDF2 repeated SHA-256 computation use karta hai taa-ke password guessing
normal fast hash se expensive ho.

#### `hash_password(password)`

```text
random salt
 -> PBKDF2-HMAC-SHA256(password, salt, 120000)
 -> store "salt:hash"
```

Salt kyun?

Same password rakhne wale two users ke saved hashes different honge. Precomputed
rainbow tables less useful hoti hain.

#### `password_matches(...)`

- stored salt/hash split;
- entered password ka hash derive;
- `hmac.compare_digest` constant-time style comparison.

#### Token payload

Conceptually token mein yeh data hota hai:

```json
{
  "uid": "user-uuid",
  "email": "user@example.com",
  "database": "mongodb",
  "expires_at": 1234567890
}
```

#### Token structure

```text
base64url(payload).base64url(HMAC-SHA256-signature)
```

Important:

- Base64 encryption nahi hai; payload readable ho sakta hai.
- Security signature se aati hai: attacker secret ke baghair valid modification
  nahi kar sakta.
- Token mein password kabhi nahi hota.
- Secret `.env` se aata hai.

#### `create_token(uid, email)`

- UID/email/database/expiry payload;
- deterministic compact JSON;
- URL-safe Base64;
- HMAC signature;
- payload + signature return.

#### `read_token(token)`

Checks:

1. format valid;
2. signature matches;
3. selected database same;
4. token unexpired;
5. UID/email valid strings.

Database check ki wajah se MongoDB token PostgreSQL ya Firestore mein reject
hota hai.

#### Private helpers

- `_derive_password_hash`: PBKDF2 logic one place.
- `_read_payload`: decode and signature validation.
- `_sign`: HMAC signature.
- `_encode/_decode`: URL-safe Base64 and padding handling.

---

### 11.2 `app/infrastructure/repository_factory.py`

Path: [`app/infrastructure/repository_factory.py`](../backend/DDD/app/infrastructure/repository_factory.py)

#### File ka purpose

Selected database ke matching todo + auth concrete repositories create karna.

#### `create_repositories(settings)`

1. normalized `selected_database` read;
2. database-bound `AuthSecurity` create;
3. Firestore/Mongo/PostgreSQL helper select;
4. tuple return:

```text
(TodoRepository, AuthRepository)
```

Why both repositories same factory se?

Guarantee hoti hai ke users aur todos same active database use kar rahe hain.
Mongo todo + Firebase auth jaisa accidental mismatch possible nahi rehta.

#### `_create_firestore_repositories`

- Firebase service credential initialize once;
- project/database names URL-safe encode;
- Firestore documents base URL;
- authorized REST session;
- Firestore todo/auth repositories.

Firebase Admin yahan auth provider nahi hai. Sirf Firestore service-account
credentials obtain karne ke liye use hota hai.

#### `_create_mongodb_repositories`

- `MongoClient` create;
- startup `ping`;
- selected database;
- todo/user collections concrete repositories ko pass.

`ping` kyun?

Wrong URI ya stopped service ko first request ke bajaye startup par detect karta
hai.

#### `_create_postgresql_repositories`

- missing URL par clear runtime error;
- same URL auth aur todo repositories ko;
- repositories tables ensure karti hain.

---

## 12. Firestore implementation

Firestore Google Cloud document database hai. Current adapter authenticated REST
API use karta hai.

### 12.1 `firestore/auth_repository.py`

Path: [`app/infrastructure/firestore/auth_repository.py`](../backend/DDD/app/infrastructure/firestore/auth_repository.py)

#### Storage location

```text
auth_users/{sha256(normalized_email)}
```

Document fields:

```text
uid
email
display_name
password_hash
```

#### Email hash document key kyun?

- deterministic lookup: query ke baghair email se exact document path;
- normalized email uniqueness;
- raw email URL/document ID mein directly nahi;
- note: SHA-256 encryption nahi; actual email document field mein stored hai.

#### `signup`

1. email lowercase/trim;
2. `_find_user` duplicate check;
3. random UID;
4. password hash;
5. Firestore REST document conversion;
6. PATCH save;
7. signed Firestore-bound token;
8. `UserData`.

#### `login`

- email document read;
- password hash compare;
- token create.

#### `authenticate`

- token signature/database/expiry;
- email ke through user document read;
- stored UID token UID se match;
- user still exists guarantee.

#### `_to_document/_from_document`

Python dictionary aur Firestore REST `fields/stringValue` representation ke
beech conversion.

---

### 12.2 `firestore/todo_repository.py`

Path: [`app/infrastructure/firestore/todo_repository.py`](../backend/DDD/app/infrastructure/firestore/todo_repository.py)

#### Storage path

```text
users/{owner_uid}/todos/{todo_id}
```

User-specific subcollection ownership naturally group karti hai.

#### `save`

Todo URL build, entity REST document banata hai, PATCH/upsert karta hai.

#### `get_by_id`

Owner UID + todo ID path se exact document read. HTTP 404 -> `None`.

#### `get_by_owner`

- user todo collection read;
- `pageSize` use;
- `nextPageToken` loop;
- every document entity mein convert.

Pagination kyun?

Large collections API ke multiple pages mein aa sakti hain. Sirf first response
read karna incomplete list de sakta tha.

#### `delete`

Document delete; already missing document ko harmless/idempotent treat karta hai.

#### `_collection_url/_document_url`

Path components URL-safe quote karte hain.

#### `_to_document/_to_entity`

Domain entity aur Firestore fields conversion, including ISO datetime.

#### `_encode/_decode`

Firestore REST values typed wrappers use karti hain:

- `stringValue`
- `booleanValue`
- `nullValue`

Helpers Python values ko is format mein convert karte hain.

---

## 13. MongoDB implementation

MongoDB document database hai. `todoflow` database mein `users` aur `todos`
collections use hoti hain.

### 13.1 `mongodb/auth_repository.py`

Path: [`app/infrastructure/mongodb/auth_repository.py`](../backend/DDD/app/infrastructure/mongodb/auth_repository.py)

#### Constructor

`email` par unique index create karta hai. Same MongoDB database mein duplicate
email prevent hota hai.

#### User document

```json
{
  "_id": "generated-user-uuid",
  "email": "normalized@example.com",
  "display_name": "User",
  "password_hash": "salt:hash"
}
```

#### `signup`

- normalize email;
- UUID;
- hash password;
- insert document;
- `DuplicateKeyError` ko safe validation error;
- token create.

#### `login`

- email lookup;
- password match;
- MongoDB-bound token.

#### `authenticate`

- token verify;
- `_id` + email both match user document;
- deleted/nonexistent user reject.

---

### 13.2 `mongodb/todo_repository.py`

Path: [`app/infrastructure/mongodb/todo_repository.py`](../backend/DDD/app/infrastructure/mongodb/todo_repository.py)

#### Constructor

`owner_uid` index create karta hai. User ki todo list filter fast hoti hai.

#### Todo document

```json
{
  "_id": "todo-uuid",
  "title": "Task title",
  "priority": "HIGH",
  "is_completed": false,
  "created_at": "ISO datetime",
  "completed_at": null,
  "owner_uid": "user-uuid"
}
```

#### `save`

`replace_one(..., upsert=True)`:

- same ID ho toh full state replace;
- ID missing ho toh insert.

#### `get_by_id`

Filter mein `_id` **and** `owner_uid`. Sirf ID filter nahi kiya gaya, isliye
other user's task leak nahi hota.

#### `get_by_owner`

Owner filter se all documents, then each document domain entity.

#### `delete`

ID + owner filter. Ownership database operation tak preserved hai.

#### `_to_document/_to_entity`

Entity and document mapping; datetimes ISO string format mein stored/restored.

---

## 14. PostgreSQL implementation

PostgreSQL relational database hai. Two tables use hoti hain:

- `users`
- `todos`

### 14.1 `postgresql/auth_repository.py`

Path: [`app/infrastructure/postgresql/auth_repository.py`](../backend/DDD/app/infrastructure/postgresql/auth_repository.py)

#### Constructor and `_create_table`

Startup par:

```sql
CREATE TABLE IF NOT EXISTS users (...)
```

Columns:

| Column | Rule |
|---|---|
| `id` | TEXT primary key |
| `email` | unique, not null |
| `display_name` | not null |
| `password_hash` | not null |

`IF NOT EXISTS` existing data destroy nahi karta.

#### `signup`

- normalized email;
- UUID;
- hashed password;
- parameterized INSERT;
- unique violation -> safe error;
- token.

Parameterized SQL kyun?

Values query string mein concatenate nahi hoti. Psycopg values separately bind
karta hai, jo SQL injection risk reduce karta hai.

#### `login`

- email SELECT;
- `dict_row` result means `user["password_hash"]`, numeric index nahi;
- password verify;
- token create.

#### `authenticate`

Token read + `id AND email` query. Token valid hone ke bawajood deleted user
access nahi kar sakta.

#### Context manager

`with psycopg.connect(...)` successful block par transaction commit aur failure
par rollback/cleanup manage karta hai.

---

### 14.2 `postgresql/todo_repository.py`

Path: [`app/infrastructure/postgresql/todo_repository.py`](../backend/DDD/app/infrastructure/postgresql/todo_repository.py)

#### `todos` table

| Column | Type |
|---|---|
| id | TEXT primary key |
| title | TEXT not null |
| priority | TEXT not null |
| is_completed | BOOLEAN not null |
| created_at | TIMESTAMPTZ not null |
| completed_at | TIMESTAMPTZ nullable |
| owner_uid | TEXT not null |

#### `save`

PostgreSQL upsert:

```sql
INSERT ...
ON CONFLICT (id) DO UPDATE ...
```

New entity insert hoti hai; completed/changed entity update hoti hai.

#### `get_by_id`

```sql
WHERE id = %s AND owner_uid = %s
```

Ownership SQL level par enforce hoti hai.

#### `get_by_owner`

User todos `created_at DESC` order mein return.

#### `delete`

Parameterized ID + owner delete.

#### `_to_entity`

Named row columns ko domain types mein convert:

- title -> `TaskTitle`
- priority -> `Priority`
- database datetime remains typed datetime
- result -> `TodoItem`

Named rows numeric `row[0]`, `row[1]` se zyada readable aur column-order changes
ke against clearer hain.

---

## 15. Authentication and security deep dive

### 15.1 Selected-database authentication

Current system mein Firebase Authentication common provider nahi hai.

```text
DATABASE=firestore   -> Firestore users + Firestore todos
DATABASE=mongodb     -> MongoDB users + MongoDB todos
DATABASE=postgresql  -> PostgreSQL users + PostgreSQL todos
```

Same email/password three databases mein signup kar sakta hai, lekin three
different UIDs aur three different accounts bante hain.

### 15.2 Signup security flow

```text
Client email/password/name
 -> Pydantic HTTP validation
 -> SignupInput DTO
 -> AuthService
 -> selected AuthRepository
 -> normalize email
 -> duplicate email check/constraint
 -> random UID
 -> random salt + PBKDF2 hash
 -> save user in selected database
 -> create signed database-bound token
 -> AuthResponse
```

### 15.3 Login security flow

```text
Client credentials
 -> selected database user lookup
 -> saved salt:hash
 -> entered password PBKDF2
 -> constant-time comparison
 -> signed token
```

Wrong password ke response mein yeh reveal nahi kiya jata ke email exist karta
hai ya password wrong hai. Generic invalid email/password message user
enumeration information ko reduce karta hai.

### 15.4 Protected request flow

```text
Authorization: Bearer token
 -> HTTPBearer extracts token
 -> AuthService.authenticate
 -> AuthRepository.authenticate
 -> HMAC signature check
 -> expiry check
 -> database claim check
 -> selected database user existence check
 -> CurrentUser(uid, email)
 -> route/use case
```

### 15.5 Cross-database isolation

Example:

```text
MongoDB token payload database="mongodb"
PostgreSQL backend expects database="postgresql"
Result: HTTP 401
```

Even if `AUTH_TOKEN_SECRET` same ho, token database claim mismatch ki wajah se
reject hota hai.

### 15.6 Todo ownership security

Todo create request client se `owner_uid` accept nahi karti. Owner verified token
se milta hai.

Read/update/delete filters ID ke sath owner UID bhi use karte hain:

```text
todo_id matches AND owner_uid matches
```

Isko defense in depth keh sakte hain: presentation verified user deti hai aur
repository query bhi ownership enforce karti hai.

### 15.7 Token vs session storage

Backend signed token issue karta hai. Current frontend token ko JavaScript memory
mein rakhta hai, `localStorage` mein nahi. Page refresh ke baad user dobara login
karta hai.

### 15.8 Is token JWT hai?

Nahi. Yeh custom compact HMAC-signed token hai. JWT jaisa payload/signature idea
use karta hai, lekin standard three-part JWT implementation nahi hai.

Presentation mein honest answer:

> “Learning/local project ke liye simple standard-library token implementation
> use hui hai. Production mein established token library/provider, secret
> rotation, refresh tokens ya HttpOnly secure cookies consider karunga.”

---

## 16. Complete request flows

### 16.1 Create todo flow

```text
React / Swagger
  |
  | POST /todos + Bearer token + title/priority
  v
Presentation: routers/todos.py
  |
  | CurrentUserDep
  v
Presentation: dependencies.py
  |
  | AuthService.authenticate(token)
  v
Application: auth_service.py
  |
  | AuthRepository.authenticate(token)
  v
Infrastructure: selected auth_repository.py
  |
  | verified UID/email
  v
Presentation route creates CreateTodoInput
  |
  v
Application: TodoService.create
  |
  | TodoItem.create
  v
Domain: validation + UUID + UTC + owner
  |
  | TodoRepository.save
  v
Infrastructure: selected todo_repository.py
  |
  | Firestore / MongoDB / PostgreSQL
  v
TodoOutput -> TodoResponse -> HTTP 201
```

### 16.2 List todos flow

```text
GET /todos
 -> verify token/user
 -> TodoService.list(uid)
 -> repository.get_by_owner(uid)
 -> selected DB owner filter
 -> TodoItem list
 -> TodoOutput list
 -> HTTP 200
```

### 16.3 Complete todo flow

```text
PATCH /todos/{id}/complete
 -> token UID
 -> TodoActionInput(id, uid)
 -> _get_todo_or_fail
 -> repository.get_by_id(id, uid)
 -> TodoItem.complete()
 -> repository.save(updated todo)
 -> HTTP 200
```

Possible failures:

- token missing/invalid: 401;
- todo not found/not owned: 404;
- already completed: 400.

### 16.4 Delete todo flow

```text
DELETE /todos/{id}
 -> verify token
 -> verify owned todo exists
 -> repository.delete(id, uid)
 -> HTTP 204
```

### 16.5 Login flow across databases

```text
$env:DATABASE="mongodb"
 -> MongoAuthRepository
 -> Mongo users collection only

$env:DATABASE="postgresql"
 -> PostgreSQLAuthRepository
 -> PostgreSQL users table only
```

Mongo account automatically PostgreSQL account nahi hota.

---

## 17. API endpoints and error codes

### 17.1 Health

| Method | Path | Auth | Success |
|---|---|---|---|
| GET | `/` | No | 200 |

Purpose: service and selected DB check.

### 17.2 Signup

| Method | Path | Auth | Success | Common errors |
|---|---|---|---|---|
| POST | `/auth/signup` | No | 201 | 400 duplicate/validation |

Request:

```json
{
  "email": "student@example.com",
  "password": "StrongPass123",
  "display_name": "Student"
}
```

Response:

```json
{
  "uid": "generated-uuid",
  "email": "student@example.com",
  "token": "signed-token",
  "message": "User created successfully"
}
```

### 17.3 Login

| Method | Path | Auth | Success | Common errors |
|---|---|---|---|---|
| POST | `/auth/login` | No | 200 | 401 wrong credentials |

### 17.4 List todos

| Method | Path | Auth | Success |
|---|---|---|---|
| GET | `/todos` | Bearer | 200 |

### 17.5 Create todo

| Method | Path | Auth | Success | Errors |
|---|---|---|---|---|
| POST | `/todos` | Bearer | 201 | 400 invalid domain data |

Request:

```json
{
  "title": "Prepare backend presentation",
  "priority": "HIGH"
}
```

### 17.6 Complete todo

| Method | Path | Auth | Success | Errors |
|---|---|---|---|---|
| PATCH | `/todos/{todo_id}/complete` | Bearer | 200 | 404 missing; 400 already complete |

### 17.7 Delete todo

| Method | Path | Auth | Success | Errors |
|---|---|---|---|---|
| DELETE | `/todos/{todo_id}` | Bearer | 204 | 404 missing/not owned |

### HTTP status summary

| Code | Meaning in this project |
|---|---|
| 200 | Successful read/login/complete |
| 201 | New user or todo created |
| 204 | Todo deleted, no response body |
| 400 | Invalid business input, duplicate signup, already complete |
| 401 | Missing/invalid/expired/wrong-database auth |
| 404 | Owned todo not found |
| 422 | Pydantic request shape/field validation failed |
| 500 | Unexpected server failure |

---

## 18. Database structures and record shapes

### 18.1 Common logical user model

```text
uid
email
display_name
password_hash
```

Token database mein store nahi hota. Login par dynamically create hota hai.

### 18.2 Common logical todo model

```text
id
title
priority
is_completed
created_at
completed_at
owner_uid
```

### 18.3 Firestore

```text
auth_users/{email_hash}
users/{owner_uid}/todos/{todo_id}
```

Compass-style collection view nahi; Firebase Console/Firestore data tab use
karna hota hai.

### 18.4 MongoDB

```text
Database: todoflow
Collections:
  users
  todos
```

Useful Compass filters:

```json
{ "email": "codex.database.verification.20261111@example.com" }
```

```json
{ "owner_uid": "USER_UID_HERE" }
```

### 18.5 PostgreSQL

```text
Tables:
  users
  todos
```

Useful pgAdmin queries:

```sql
SELECT id, email, display_name
FROM users
ORDER BY email;
```

```sql
SELECT id, title, priority, is_completed, owner_uid, created_at
FROM todos
ORDER BY created_at DESC;
```

Passwords/hashes presentation screen par show na karein.

### 18.6 Verified demo records

Same test email se three separate accounts verify kiye gaye hain:

```text
codex.database.verification.20261111@example.com
```

| Database | User UID | Verification task |
|---|---|---|
| Firestore | `f786e823-095e-4c97-903e-8850097948f5` | Firestore database verification task |
| MongoDB | `d4a637b0-dd2e-4607-9e83-96195779c013` | MongoDB database verification task |
| PostgreSQL | `a7073d57-d75d-4942-8538-87721d95e370` | PostgreSQL database verification task |

Test password intentionally is document mein nahi likha. Public/versioned docs
mein credentials rakhna professional practice nahi hai.

---

## 19. Database switching

Backend stop karke PowerShell mein one database select karein:

### Firestore

```powershell
$env:DATABASE = "firestore"
python -m uvicorn main:app --reload
```

### MongoDB

```powershell
$env:DATABASE = "mongodb"
python -m uvicorn main:app --reload
```

### PostgreSQL

```powershell
$env:DATABASE = "postgresql"
python -m uvicorn main:app --reload
```

### Terminal environment `.env` ko kaise override karta hai?

Pydantic Settings environment value ko priority deti hai. Isliye `.env` edit
kiye baghair current terminal mein DB switch hoti hai.

### Restart kyun zaroori hai?

Repositories startup par create hoti hain aur app lifetime ke liye
`app.state` mein store hoti hain. Running process ke beech `DATABASE` change
karne se already-created objects automatically replace nahi hote.

### Switch ke baad login kyun nahi chalta?

Accounts separate hain. Firestore email PostgreSQL users table mein tab tak
nahi hoti jab tak PostgreSQL mode mein signup na ho. Old database token bhi
database claim mismatch ki wajah se reject hota hai.

---

## 20. Logging system

Example flow:

```text
03:00:30 | INFO | REQUEST | #031 POST /todos
03:00:30 | INFO | #031 POST /todos | Auth | Token is valid...
03:00:30 | INFO | #031 POST /todos | Presentation | Create todo request received.
03:00:30 | INFO | #031 POST /todos | Infrastructure | Saved todo in PostgreSQL.
03:00:30 | INFO | #031 POST /todos | Application | Todo ... created and saved.
03:00:30 | INFO | RESPONSE | #031 POST /todos | 201 Created | 93 ms
```

### Layer log order ko kaise explain karein?

Exact order operation par depend karta hai. Protected route mein auth dependency
route body se pehle chalti hai. Todo creation ke andar service database save
call ke baad application completion log karti hai. Isliye infrastructure log
application completion log se pehle aa sakta hai.

### Logs ka value

- debugging;
- performance duration;
- request correlation;
- architecture learning;
- database adapter confirmation;
- errors without intentionally logging tokens/passwords.

---

## 21. Tests and verification

### 21.1 `tests/test_domain_and_security.py`

Path: [`tests/test_domain_and_security.py`](../backend/DDD/tests/test_domain_and_security.py)

Standard-library `unittest` use hota hai; extra testing package required nahi.

#### Domain tests

1. Title trim + priority uppercase.
2. Short title rejection.
3. Completed todo cannot complete again.

#### Security tests

1. Password plain text store nahi hota and correct password verifies.
2. Token sirf correct database mein valid.
3. Modified/tampered token rejected.

Run:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

### 21.2 Compilation check

```powershell
.\.venv\Scripts\python.exe -m compileall -q app main.py tests
```

Syntax/import-compilation issues catch karta hai.

### 21.3 Dependency check

```powershell
.\.venv\Scripts\python.exe -m pip check
```

Installed package conflicts/broken requirements detect karta hai.

### 21.4 Real integration tests already performed

Har database par verify hua:

- health endpoint;
- signup;
- wrong-password rejection;
- login;
- no-token rejection;
- create task;
- list task;
- complete task;
- duplicate-complete rejection;
- delete task;
- cross-database token rejection;
- direct database record presence.

### 21.5 Test pyramid explanation

```text
Fast unit tests: domain/security rules
Integration tests: real repositories/databases
API tests: routes + dependencies + services + repositories
Frontend build: client compile integration
```

---

## 22. Live presentation/demo plan

### Recommended 25–35 minute order

#### Part 1 — Problem and architecture (3–5 min)

1. TodoFlow business problem.
2. Three databases.
3. Four DDD layers.
4. Dependency direction diagram.

Opening line:

> “Main pehle business rules ko database se independent rakhna chahta tha,
> isliye DDD layering aur repository abstraction use ki.”

#### Part 2 — Folder structure (4–5 min)

VS Code Explorer mein folders show karein:

1. `domain`
2. `application`
3. `presentation`
4. `infrastructure`
5. `app/main.py`
6. `tests`

Har folder ke liye one sentence:

- Domain: rules/contracts.
- Application: workflows.
- Presentation: HTTP.
- Infrastructure: technical adapters.
- Main: wiring.

#### Part 3 — One code path (6–8 min)

Create todo request trace karein:

1. `routers/todos.py:create_todo`
2. `dependencies.py:current_user`
3. `dto.py:CreateTodoInput`
4. `todo_service.py:create`
5. `domain/todo.py:TodoItem.create`
6. `TodoRepository.save` contract
7. one selected repository `save`

Presentation tip: Har database file line-by-line show na karein. Ek adapter detail
mein aur doosre comparison se explain karein.

#### Part 4 — Authentication/security (5–6 min)

1. Same DB stores users + todos.
2. Password hash flow.
3. Token payload/signature.
4. Database-bound token.
5. UID verified token se aati hai.

#### Part 5 — Live Swagger demo (5–7 min)

1. Backend start.
2. `GET /` active DB show.
3. `/docs` open.
4. Login.
5. Swagger **Authorize** mein Bearer token.
6. Create todo.
7. List todo.
8. Complete todo.
9. Terminal logs show.

Swagger URL:

```text
http://127.0.0.1:8000/docs
```

#### Part 6 — Database view (3–5 min)

- PostgreSQL mode: pgAdmin `users` + `todos`.
- MongoDB mode: Compass collections.
- Firestore mode: Firebase Console document paths.
- Same email ke different UIDs show karna strong demo hai.

#### Part 7 — Tests and conclusion (2–3 min)

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Conclusion:

> “Architecture ka result yeh hai ke selected database adapter change hota hai,
> lekin domain rules, use cases aur public API unchanged rehte hain.”

---

### Presentation se pehle checklist

- [ ] MongoDB service running.
- [ ] PostgreSQL service running.
- [ ] Firestore internet/service-account available.
- [ ] `.env` exists but screen par open nahi karni.
- [ ] Backend virtual environment activated.
- [ ] Frontend optional terminal ready.
- [ ] Swagger open.
- [ ] pgAdmin, Compass, Firestore tabs ready.
- [ ] Test login password privately available.
- [ ] Browser zoom readable.
- [ ] Terminal font size readable.
- [ ] Notifications off.
- [ ] Backup screenshots available if internet fails.

### Demo commands

```powershell
cd "C:\Users\Rana Khawar Ali\Desktop\Cloudpacer-Internship\backend\DDD"
.\.venv\Scripts\Activate.ps1
$env:DATABASE = "postgresql"
python -m uvicorn main:app --reload
```

Switching demo:

```powershell
# Stop previous backend with Ctrl+C first
$env:DATABASE = "mongodb"
python -m uvicorn main:app --reload
```

### If live demo fails

1. Health endpoint check.
2. Terminal first error line read.
3. Active DB verify.
4. Database service/credentials verify.
5. Explain that automated integration verification already passed.
6. Use saved database screenshots/records.

---

## 23. Design decisions: why this approach?

### 23.1 Why DDD for a todo project?

Todo domain small hai, lekin project ka learning goal architecture aur multi-DB
abstraction demonstrate karna hai. DDD layers repository switching aur rule
placement ko clearly show karti hain.

Honest nuance:

> Very small CRUD production app mein full DDD overengineering ho sakti hai.
> Yahan multiple persistence adapters aur architecture learning is separation ko
> justify karte hain.

### 23.2 Why repository pattern?

- use cases database-independent;
- consistent ownership operations;
- adapters independently replace/test;
- database-specific queries one layer mein.

### 23.3 Why auth and todo repositories separate?

Authentication aur todo persistence different contracts/responsibilities hain.
Ek huge database class Single Responsibility ko break karti aur files too long
banati.

### 23.4 Why database-specific folders?

Same technology ka related auth/todo code discoverable rehta hai:

```text
infrastructure/mongodb/auth_repository.py
infrastructure/mongodb/todo_repository.py
```

Flat six ambiguously prefixed files se folder hierarchy clearer hai.

### 23.5 Why one factory?

Database selection duplicate nahi hoti. Factory guarantee karti hai ke matching
auth + todo pair return ho.

### 23.6 Why application DTOs and presentation schemas both?

- Presentation schemas HTTP/Pydantic concern.
- Application DTOs framework-independent service boundary.
- Domain entities business behavior.

Ek model sab jagah use karna short lagta hai, lekin layers tightly couple ho
jati hain.

### 23.7 Why `app.state` + FastAPI dependencies?

- service objects startup par once configured;
- routes database construction nahi karti;
- hidden mutable module globals avoid;
- tests alternate app/settings create kar sakte hain;
- route signatures dependencies clearly show karti hain.

### 23.8 Why custom logger?

Architecture learning aur demo ke liye each layer step visible hai. Production
mein structured JSON logs/trace IDs use kiye ja sakte hain, lekin current format
beginner readable hai.

### 23.9 Why UUID strings?

- three databases mein portable;
- centralized sequence required nahi;
- client/database independent unique ID;
- Firestore/Mongo/Postgres same domain representation.

### 23.10 Why UTC timestamps?

Server/local timezone ambiguity avoid. UI later local timezone mein display
convert kar sakti hai.

### 23.11 Why table/collection creation on startup?

Local beginner setup simple hota hai. PostgreSQL tables and Mongo indexes
automatically ensure hote hain.

Production nuance: schema migrations (Alembic etc.) better hoti hain because
version history and controlled rollout milta hai.

---

## 24. Current limitations and production improvements

Limitations ko hide nahi karna; professionally explain karna chahiye.

### 24.1 Custom token format

Current: standard-library HMAC compact token.

Production improvement:

- established JWT/session library;
- secret rotation/key IDs;
- refresh-token strategy;
- revocation/logout tracking;
- HttpOnly Secure SameSite cookies when appropriate.

### 24.2 Password policy

Current HTTP minimum is 6 characters; PBKDF2 hashing exists.

Production improvement:

- stronger length policy;
- breached-password detection;
- rate limiting/lockout;
- Argon2id/bcrypt based on security policy;
- password reset and verification.

### 24.3 No email verification

Account email ownership verify nahi hoti. Production mein verification flow
add karna chahiye.

### 24.4 Firestore signup concurrency

Current adapter read-then-write duplicate check use karta hai. High-concurrency
production system atomic create/precondition or transaction use kare.

### 24.5 Database connection management

PostgreSQL currently operation per connection open karta hai. Production mein
connection pool performance improve karega. Mongo client already long-lived
collection reference ke through reuse hota hai.

### 24.6 Schema migrations

Current tables `CREATE IF NOT EXISTS`. Production evolution ke liye migration
tool/versioned scripts better hain.

### 24.7 More automated integration tests

Current core unit tests aur manual/scripted real DB integration pass hain.
Production CI mein disposable test databases/containers aur repeatable API test
suite add honi chahiye.

### 24.8 Authorization roles

Current model normal owner-based user hai. Admin/roles/permissions future
feature ho sakti hain.

### 24.9 Observability

Future:

- JSON structured logs;
- correlation ID from proxy;
- metrics;
- distributed tracing;
- centralized error reporting.

### 24.10 Old data migration

Old Firebase Auth UIDs se saved todos new database-auth UID se automatically
link nahi hote. Production migration ko explicit UID mapping/script chahiye.

---

## 25. Viva/interview questions with answers

### Q1. DDD kya hai?

DDD business concepts aur rules ko design ka center banata hai. Framework aur
database external details rehte hain.

### Q2. Domain layer mein kya hai?

Todo entity, title value object, priority enum, business errors, auth/todo
repository contracts aur database-independent user data.

### Q3. Domain mein FastAPI import kyun nahi?

Business rules framework-independent rehne chahiye. Framework change ho toh
domain code unaffected rahe.

### Q4. Application layer ka kaam kya hai?

Use cases coordinate karna: entity create, repository call, output map. Woh
database queries ya HTTP status define nahi karti.

### Q5. Presentation layer ka kaam?

Request validation, endpoints, token extraction, dependencies, HTTP error/status
mapping aur response schemas.

### Q6. Infrastructure layer ka kaam?

Repository contracts ki concrete implementation: Firestore REST, MongoDB,
PostgreSQL, password hashing aur token signing.

### Q7. Repository pattern kyun?

Use cases ko database-specific APIs se decouple karta hai. Database adapter
switch karne par service/domain unchanged rehte hain.

### Q8. `AuthRepository` interface kahan hai aur implementation kahan?

Contract `domain/auth.py`; implementations each database infrastructure folder
ke `auth_repository.py` mein.

### Q9. Dependency inversion kya hai?

High-level service concrete database ke bajaye abstraction par depend karti hai.
Concrete adapter us abstraction ko implement karta hai.

### Q10. Same email three databases mein same user kyun nahi?

Har selected database apni users storage own karta hai aur signup par new random
UID generate hoti hai. Accounts intentionally isolated hain.

### Q11. Database switch kaise hota hai?

PowerShell `DATABASE` environment variable set karke backend restart. Typed
Settings normalized value repository factory ko deti hai.

### Q12. Firebase Admin ab kis liye hai?

Firebase Authentication ke liye nahi. Firestore REST requests ke service-account
credentials obtain karne ke liye.

### Q13. Password database mein kaise store hota hai?

Random salt + PBKDF2-HMAC-SHA256 derived hash as `salt:hash`. Plain password
store nahi hota.

### Q14. Salt kyun use hota hai?

Same password ke hashes different banata hai aur precomputed attack tables ko
less effective karta hai.

### Q15. `compare_digest` kyun?

Sensitive hash/signature comparison ko timing differences ke against safer
banane ke liye.

### Q16. Token database-specific kaise hai?

Signed payload mein `database` field hoti hai. Verification active database se
compare karti hai.

### Q17. Kya token encrypted hai?

Nahi. Payload Base64-encoded hai; integrity HMAC signature se protected hai.
Sensitive password token mein nahi hota.

### Q18. Token valid ho lekin user delete ho jaye?

Each `authenticate` token verify ke baad database mein UID/email user existence
check karta hai; deleted user reject hota hai.

### Q19. User doosre user ka todo kyun nahi read kar sakta?

Owner UID verified token se aati hai aur repository queries ID ke sath owner UID
bhi filter karti hain.

### Q20. `TaskTitle` value object kyun?

Title validation ko reusable business invariant banata hai. Entity/API/database
restore sab par same rule.

### Q21. Todo ko twice complete karne par kya hota hai?

`TodoItem.complete()` `TaskAlreadyCompletedError` raise karta hai; route HTTP 400
return karti hai.

### Q22. DTO aur entity mein farq?

Entity identity/state/business behavior rakhti hai. DTO layers ke darmiyan data
carry karta hai, behavior minimal hota hai.

### Q23. Pydantic schema aur application DTO mein farq?

Pydantic schema HTTP validation/serialization ke liye. Application DTO
framework-independent use-case input/output.

### Q24. `create_app` factory kyun?

Application construction repeatable/testable hoti hai; tests alternate settings
ke sath separate FastAPI instance create kar sakte hain.

### Q25. `app.state` kyun?

Startup par configured service objects app lifetime ke liye store hote hain aur
request dependencies unko retrieve karti hain.

### Q26. CORS kya hai?

Browser security mechanism. Backend configured frontend origins ko cross-origin
API calls allow karta hai.

### Q27. PostgreSQL SQL injection kaise avoid hoti hai?

Parameterized queries `%s` placeholders + separate value tuples. User values
query text mein concatenate nahi hote.

### Q28. MongoDB indexes kya hain?

Auth email unique index duplicate account rokta hai. Todo owner UID index user
list queries improve karta hai.

### Q29. Firestore pagination kyun?

REST list response multiple pages ho sakta hai. `nextPageToken` loop complete
user list ensure karta hai.

### Q30. `ON CONFLICT` kya karta hai?

PostgreSQL todo ID already exist ho toh selected fields update; otherwise insert.
Create aur complete state save same repository method se hoti hai.

### Q31. `__init__.py` kyun?

Directories ko regular Python package banati hai. Current files intentionally
minimal hain to avoid import side effects.

### Q32. Root `main.py` aur `app/main.py` dono kyun?

`app/main.py` professional composition root; root file simple backward-compatible
Uvicorn/direct-run entrypoint.

### Q33. Logs mein request number kaise safe rehta hai?

`ContextVar` concurrent request context isolate karta hai; finally block reset.

### Q34. Current architecture ka biggest benefit?

Database adapters replace/switch hote hain without changing public API, domain
rules ya application workflows.

### Q35. Biggest production improvement kya hoga?

Established production auth/session strategy, rate limiting, migrations,
connection pooling, repeatable integration CI and secret management.

---

## 26. Final quick-revision sheet

### Five files you must remember

1. `app/main.py` — sab layers wire.
2. `domain/todo.py` — business rules.
3. `application/todo_service.py` — workflows.
4. `presentation/routers/todos.py` — HTTP endpoints.
5. `infrastructure/repository_factory.py` — selected DB adapters.

### Four layers in one line

```text
Presentation receives -> Application coordinates -> Domain decides -> Infrastructure persists
```

### Create todo in one line

```text
HTTP request -> token UID -> DTO -> service -> entity rule -> repository -> selected DB -> response
```

### Auth in one line

```text
Selected DB user + hashed password + signed database-bound token
```

### Security points

- no plain password;
- random salt;
- PBKDF2 hash;
- HMAC signature;
- token expiry;
- database binding;
- DB user existence check;
- owner UID from verified token;
- owner filter in repository.

### Database mapping

```text
Firestore:  auth_users + users/{uid}/todos
MongoDB:    users collection + todos collection
PostgreSQL: users table + todos table
```

### Start command

```powershell
$env:DATABASE = "postgresql"  # or mongodb / firestore
python -m uvicorn main:app --reload
```

### Test command

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

### Final closing statement

> “TodoFlow backend mein business rules domain ke andar protected hain,
> application workflows database-independent hain, presentation sirf HTTP
> handle karti hai, aur infrastructure three databases ki concrete adapters
> provide karti hai. Repository abstraction aur dependency injection ki wajah
> se database switch hota hai, architecture ka core change nahi hota.”

---

## Glossary

| Term | Meaning |
|---|---|
| DDD | Domain-Driven Design |
| Domain | Business concepts and rules |
| Entity | Identity + changing state + behavior object |
| Value Object | Identity-less validated value |
| DTO | Layer-to-layer data carrier |
| Repository | Persistence contract/adapter abstraction |
| Adapter | External technology ki concrete implementation |
| Dependency Injection | Required object ko outside se provide karna |
| Composition Root | Place where concrete dependencies are wired |
| Invariant | Business rule jo hamesha true rehni chahiye |
| CORS | Browser cross-origin request policy |
| PBKDF2 | Repeated password key-derivation algorithm |
| Salt | Random password-hash input |
| HMAC | Secret-key based message integrity signature |
| UUID | Portable unique identifier |
| UTC | Standard timezone-independent time basis |
| Upsert | Insert if missing, update if existing |
| Middleware | Har request/response ke around shared processing |

---

## Last advice for presentation

Code ko memorize mat karein. Har file ke liye yeh three questions yaad rakhein:

1. **What:** yeh file/class/function kya karti hai?
2. **Why:** yeh isi layer mein kyun hai?
3. **How:** request flow mein technically kaise use hoti hai?

Agar aap dependency direction, create-todo flow, auth security aur database
factory confidently explain kar lein, toh aap poore backend ki architecture
effectively present kar sakte hain.
