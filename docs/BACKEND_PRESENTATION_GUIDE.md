# TodoFlow DDD Backend — Complete Presentation Guide

> **Purpose:** Yeh guide backend ko sirf run karne ke liye nahi, balki uski
> architecture, har folder, har file, important class/function, database flow,
> authentication, security aur design decisions ko confidently explain karne
> ke liye hai.
>
> **Presentation language:** Simple English + Roman Urdu.
>
> **How complete is this guide?** Is document mein file responsibilities,
> class/function signatures, inputs, outputs, call flow, database structures,
> API examples, error mapping aur ready-made viva answers included hain. Normal
> presentation preparation ke liye backend code files kholna zaroori nahi.
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
27. [Complete file answer cards](#27-complete-file-answer-cards)
28. [Complete function and method reference](#28-complete-function-and-method-reference)
29. [Exact API request/response answer bank](#29-exact-api-requestresponse-answer-bank)
30. [Three-database comparison answer bank](#30-three-database-comparison-answer-bank)
31. [Advanced viva questions with ready answers](#31-advanced-viva-questions-with-ready-answers)

---

## Is guide ko code kholay baghair kaise use karein?

### Agar presentation 5 minutes mein hai

Yeh order read karein:

1. Section 1 ka one-minute summary.
2. Section 3 ki four-layer table.
3. Section 6 ka startup flow.
4. Section 16.1 ka create-todo flow.
5. Section 26 ki quick-revision sheet.
6. Section 31 ke advanced viva answers.

### Agar teacher kisi file ka naam poochay

Section 27 mein us file ka **What / Input / Output / Why / Ready answer** card
dekhein. Answer ka recommended order yeh hai:

```text
What -> When -> How -> Why this layer -> Failure or security behavior
```

Example:

> “`todo_service.py` application layer mein todo use cases coordinate karti
> hai. Route se DTO leti hai, domain entity par rule apply karti hai, repository
> contract ko call karti hai aur API-friendly output return karti hai. Is file
> mein SQL ya Mongo query nahi hoti, isliye workflow database-independent hai.”

### Agar teacher kisi function ka naam poochay

Section 28 mein exact signature, input, return value, calls aur possible error
dekhein. Function ka code memorize karne ki zarurat nahi; uska contract aur
flow explain karein.

### Agar API demo ya JSON poochi jaye

Section 29 se exact header, request, response aur error body use karein.

### Agar databases ka difference poocha jaye

Section 30 ki comparison tables use karein. Wahan same operation Firestore,
MongoDB aur PostgreSQL mein side-by-side explain hai.

### Golden answer formula

Har technical jawab ko is formula mein dein:

```text
Purpose + layer + input + important steps + output + reason/security
```

Is formula se answer short bhi rehta hai aur professional bhi lagta hai.

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

Class: `TodoDomainTests(unittest.TestCase)`

| Test method | Exact proof |
|---|---|
| `test_create_trims_title_and_normalizes_priority` | `"  Learn DDD  "` becomes `"Learn DDD"`, `high` becomes `HIGH`, new todo incomplete |
| `test_short_title_is_rejected` | One-character title raises `InvalidTaskTitleError` |
| `test_completed_todo_cannot_complete_again` | Second `complete()` raises `TaskAlreadyCompletedError` |

#### Security tests

Class: `AuthSecurityTests(unittest.TestCase)`

`setUp()` same test secret ke sath separate PostgreSQL and MongoDB
`AuthSecurity` objects banata hai; expiry five minutes rakhta hai.

| Test method | Exact proof |
|---|---|
| `test_password_is_hashed_and_can_be_verified` | Saved value plain password contain nahi karti; correct password true and wrong false |
| `test_token_is_valid_only_for_its_database` | PostgreSQL token PostgreSQL mein valid but Mongo security object rejects |
| `test_modified_token_is_rejected` | Token ka last character change karne par signature validation fails |

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

## 27. Complete file answer cards

Yeh section file kholay baghair har file ka direct answer deta hai. “Input” ka
matlab file ko kya milta hai; “output/side effect” ka matlab woh kya return ya
change karti hai.

### 27.1 Root and shared files

| File | What is inside? | Input | Output / side effect | Why separate? |
|---|---|---|---|---|
| `main.py` | `app`, `create_app`, direct-run Uvicorn block | Uvicorn import ya `python main.py` | FastAPI server start/export | Beginner ko simple command milti hai; real wiring `app/main.py` mein rehti hai |
| `app/main.py` | `create_app()` and exported `app` | Optional `Settings` | Complete wired FastAPI application | Yeh composition root hai; concrete dependencies sirf ek jagah connect hoti hain |
| `app/config.py` | `Settings`, three computed properties, `get_settings()` | `.env` + terminal environment | Validated typed configuration | Scattered environment access aur string-conversion errors avoid hoti hain |
| `app/logging.py` | Named logger, request context, middleware, log helpers | Request plus layer messages | Bilingual correlated terminal logs | Business flow visible hota hai without log code duplicate kiye |
| `.env` | Real local values | Developer secrets/URLs | Runtime configuration | Machine-specific aur secret; Git ignored |
| `.env.example` | Safe sample variables | None | Setup contract/documentation | New developer ko required variable names milte hain without secrets |
| `requirements.txt` | Python dependencies | `pip install -r` | Reproducible environment | Required libraries ek documented list mein rehti hain |
| `README.md` | Run and usage instructions | Reader | Quick onboarding | Daily setup detail architecture guide se separate rehti hai |
| `ARCHITECTURE.md` | Layer placement rules | Developer decisions | Structure standard | Batata hai kya kis layer mein hona chahiye aur kya nahi |

Ready answer:

> “Root `main.py` sirf entrypoint hai. `app/main.py` composition root hai.
> `config.py` external configuration ko typed object banati hai aur `logging.py`
> complete request ko request ID ke sath trace karti hai.”

### 27.2 Domain files

| File | Important objects | Exact responsibility | Is file mein kya nahi hai? |
|---|---|---|---|
| `app/domain/auth.py` | `ValidationException`, `UserData`, `AuthRepository` | Authentication ki database-independent language aur contract | Password hashing, token algorithm, HTTP codes, database queries |
| `app/domain/todo.py` | Domain errors, `Priority`, `TaskTitle`, `TodoItem`, `TodoRepository` | Todo rules, entity behavior and persistence contract | FastAPI, Pydantic, SQL, MongoDB, Firestore |

Ready answer:

> “Domain business ka center hai. `TaskTitle` valid title guarantee karta hai,
> `TodoItem.complete()` one-time completion rule enforce karta hai, aur
> repository ABCs batati hain application ko storage se kaunse operations
> chahiye. Domain ko actual database ka pata nahi.”

### 27.3 Application files

| File | Important objects | Receives | Returns | Why application layer? |
|---|---|---|---|---|
| `app/application/dto.py` | Six frozen dataclasses | Plain validated values | Framework-independent input/output objects | HTTP schemas aur domain entities ko directly couple nahi karta |
| `app/application/auth_service.py` | `AuthService` | Signup/login DTO or token | `AuthOutput` | Auth workflow coordinate karta hai; implementation repository ke peeche hai |
| `app/application/todo_service.py` | `to_output`, `TodoService` | Create/action DTO or owner UID | `TodoOutput`, list, or `None` | Domain behavior aur persistence ko correct order mein chalata hai |

Ready answer:

> “Application layer rules invent nahi karti. Woh route se input leti hai,
> domain behavior call karti hai, repository abstraction se persistence karwati
> hai aur output DTO return karti hai.”

### 27.4 Presentation files

| File | Important objects | Main job | Why presentation layer? |
|---|---|---|---|
| `app/presentation/schemas.py` | Five Pydantic models | HTTP JSON validate/serialize | Client contract framework-specific hota hai |
| `app/presentation/dependencies.py` | `CurrentUser`, service providers, Bearer auth | Configured services aur verified user inject karna | Routes short rehti hain; auth repeat nahi hota |
| `app/presentation/routers/auth.py` | Signup and login routes | HTTP body -> DTO -> service -> response | HTTP status/error mapping yahan belong karti hai |
| `app/presentation/routers/todos.py` | Four protected todo routes | Path/body/user -> todo use case | Endpoint-specific status codes and response models yahan hain |

Ready answer:

> “Presentation external HTTP boundary hai. Pydantic request validate karta
> hai, dependencies Bearer token aur services provide karti hain, routers DTO
> banati hain aur domain/application errors ko HTTP status mein translate karti
> hain.”

### 27.5 Shared infrastructure files

| File | Important objects | Main job | Why infrastructure? |
|---|---|---|---|
| `app/infrastructure/security.py` | `AuthSecurity` | Password hash/compare and signed database-bound token | Cryptography technical implementation hai, business workflow nahi |
| `app/infrastructure/repository_factory.py` | `create_repositories` + three helpers | Selected database ke matching auth and todo adapters banana | Concrete driver selection outermost wiring concern hai |

Ready answer:

> “Security class same hashing/token policy three databases ko deti hai.
> Factory `DATABASE` read karke matching pair return karti hai, isliye auth aur
> todos kabhi accidentally different databases use nahi karte.”

### 27.6 Firestore adapter files

| File | Stores | Important implementation detail | Returns domain/application-friendly data kaise? |
|---|---|---|---|
| `firestore/auth_repository.py` | `FirestoreAuthRepository`; `auth_users/{sha256(email)}` | Authorized REST session, email-derived document ID, hashed password | REST fields dictionary ko `UserData` mein map karta hai |
| `firestore/todo_repository.py` | `users/{uid}/todos/{todo_id}` | Per-user subcollection, pagination, REST typed values | Firestore document ko `TodoItem` mein restore karta hai |

Ready answer:

> “Firestore adapter Admin credentials se authorized REST session banata hai.
> Auth document normalized email ke SHA-256 key par hai; todos user UID ke neeche
> subcollection mein hain. Mapping helpers Firestore `stringValue`,
> `booleanValue`, `nullValue` ko Python/domain values mein convert karte hain.”

### 27.7 MongoDB adapter files

| File | Stores | Index | Important operation |
|---|---|---|---|
| `mongodb/auth_repository.py` | `users` documents | Unique `email` | `insert_one`, `find_one`; duplicate key safe validation error |
| `mongodb/todo_repository.py` | `todos` documents | `owner_uid` | `replace_one(..., upsert=True)` and owner-filtered read/delete |

Ready answer:

> “Mongo auth collection email uniqueness enforce karti hai. Todo collection
> owner index use karti hai. `_id` UUID string hai aur every sensitive todo query
> mein `_id` ke sath `owner_uid` bhi filter hota hai.”

### 27.8 PostgreSQL adapter files

| File | Table | Important SQL | Safety/readability |
|---|---|---|---|
| `postgresql/auth_repository.py` | `users` | `CREATE TABLE`, parameterized `INSERT/SELECT` | Unique email, context-managed transaction, `dict_row` |
| `postgresql/todo_repository.py` | `todos` | `INSERT ... ON CONFLICT`, owner-filtered `SELECT/DELETE` | `%s` parameters, typed timestamps/booleans, named rows |

Ready answer:

> “PostgreSQL adapters startup par missing tables safely create karti hain.
> Values SQL string mein concatenate nahi hoti; `%s` parameters use hote hain.
> Todo save upsert hai aur reads/deletes owner UID se protected hain.”

### 27.9 `__init__.py` files

Har package folder ka `__init__.py` intentionally almost empty hai.

- Python ko regular package signal karta hai.
- `app.*` imports reliable banata hai.
- Business logic hide nahi karta.
- Import time par database connection ya side effect start nahi karta.

Ready answer:

> “`__init__.py` package marker hai. Is project mein minimal rakhi gayi hai taa-ke
> imports predictable hon aur hidden startup side effects na hon.”

---

## 28. Complete function and method reference

### 28.1 Startup, configuration and logging

| Signature/name | Input | Exact work | Return / effect |
|---|---|---|---|
| `create_app(settings=None)` | Optional `Settings` | FastAPI, CORS, logs, repository pair, services, routers and health wire | `FastAPI` object |
| `health_check()` | No explicit input | Active architecture/database report | `{"status":"ok", ...}` |
| `Settings.selected_database` | `database` field | Trim, lowercase, `firebase -> firestore`, allowed set check | Normalized DB name or `ValueError` |
| `Settings.allowed_origins` | Comma-separated string | Split, trim, empty values remove | `list[str]` |
| `Settings.firebase_credential_file` | Relative/absolute setting | Relative path backend root se resolve | Absolute `Path` |
| `get_settings()` | Environment + `.env` | One validated cached settings object build | `Settings` |
| `log_step(area, english, roman_urdu)` | Layer and two messages | Current request label attach, INFO print | Terminal log |
| `log_error(area, message)` | Safe technical text | Current request label attach, ERROR print | Terminal log |
| `install_request_logging(app)` | FastAPI app | Middleware register, request ID/timing/status/exception trace | App middleware side effect |
| nested `request_logger(request, call_next)` | One HTTP request + next handler | Context set, duration measure, response/exception log, context reset | Response or re-raised exception |

Important startup fact: module ke end par `app = create_app()` hai. Isliye
`uvicorn main:app` import karte hi settings validate aur selected database
connect hota hai. Bad URL/password ho toh server request receive karne se pehle
startup fail hota hai.

### 28.2 Domain auth reference

| Object/method | Input | Return | Meaning |
|---|---|---|---|
| `ValidationException(message)` | Safe user-facing reason | Exception | Auth/input failure jo route map kar sakti hai |
| `UserData(uid,email,token)` | Three strings | Frozen domain data | Repository ka database-independent auth result |
| `AuthRepository.signup(email,password,name)` | Raw signup values | `UserData` | Selected DB account create contract |
| `AuthRepository.login(email,password)` | Credentials | `UserData` | Credential verification contract |
| `AuthRepository.authenticate(token)` | Bearer token | `UserData` | Token + current DB user existence contract |

ABC methods implementation nahi detin. Agar concrete repository required method
implement na kare toh class valid adapter nahi ban sakti.

### 28.3 Domain todo reference

| Object/method | Input | Work | Return/error |
|---|---|---|---|
| `TaskTitle(value)` | Any title string | Trim; length 3–120 enforce | Frozen value or `InvalidTaskTitleError` |
| `TodoItem.create(title,priority,owner_uid)` | Plain values | UUID, valid title/priority, UTC creation, incomplete state | New `TodoItem` |
| `TodoItem.complete()` | Existing entity | Already-complete guard; state true; UTC completion time | `None` or `TaskAlreadyCompletedError` |
| `TodoRepository.save(todo)` | Entity | Create/update contract | `None` |
| `get_by_id(todo_id,owner_uid)` | ID + verified owner | Owned entity lookup contract | `TodoItem` or `None` |
| `get_by_owner(owner_uid)` | Verified owner | User list contract | `list[TodoItem]` |
| `delete(todo_id,owner_uid)` | ID + verified owner | Owned delete contract | `None` |

`Priority(priority.upper())` ki wajah se service/domain creation lowercase
priority ko uppercase enum mein normalize kar sakti hai. Database se restore
karte waqt stored value already `LOW`, `MEDIUM`, ya `HIGH` honi chahiye.

### 28.4 Application DTO reference

| DTO | Exact fields | Created by | Consumed by |
|---|---|---|---|
| `SignupInput` | `email,password,display_name` | Signup route | `AuthService.signup` |
| `LoginInput` | `email,password` | Login route | `AuthService.login` |
| `CreateTodoInput` | `title,priority,owner_uid` | Create route | `TodoService.create` |
| `TodoActionInput` | `todo_id,owner_uid` | Complete/delete route | Corresponding service method |
| `AuthOutput` | `uid,email,token` | `AuthService` | Auth route |
| `TodoOutput` | Seven todo fields as API-safe primitives | `to_output` | Todo route/response model |

All DTOs `frozen=True` hain. Creation ke baad accidental field mutation nahi
hoti; workflow input/output predictable rehta hai.

### 28.5 Application service reference

| Method | Calls in order | Return | Main failure source |
|---|---|---|---|
| `AuthService.signup(data)` | repository `signup` -> log -> map | `AuthOutput` | Adapter `ValidationException` |
| `AuthService.login(data)` | repository `login` -> log -> map | `AuthOutput` | Wrong credentials/DB failure |
| `AuthService.authenticate(token)` | repository `authenticate` -> map | `AuthOutput` | Invalid/expired/wrong-DB/deleted user |
| `AuthService._to_output(...)` | Construct DTO | `AuthOutput` | None for valid strings |
| `to_output(todo)` | Enum/value/datetime primitive mapping | `TodoOutput` | Invalid entity data should already be impossible |
| `TodoService.create(data)` | `TodoItem.create` -> `save` -> log -> map | `TodoOutput` | Domain validation or DB error |
| `TodoService.list(owner_uid)` | `get_by_owner` -> log count -> map all | `list[TodoOutput]` | DB error |
| `TodoService.complete(data)` | owned lookup -> entity `complete` -> save -> log | `TodoOutput` | Not found or already complete |
| `TodoService.delete(data)` | owned lookup -> repository delete -> log | `None` | Not found or DB error |
| `_get_todo_or_fail(data)` | `get_by_id(id,owner)` | `TodoItem` | Raises `TodoNotFoundError` |

### 28.6 Presentation dependency reference

| Name | Source | Return/use |
|---|---|---|
| `bearer = HTTPBearer()` | `Authorization: Bearer ...` header | Credentials extraction; missing/malformed auth request reject |
| `get_auth_service(request)` | `request.app.state.auth_service` | Configured `AuthService` |
| `get_todo_service(request)` | `request.app.state.todo_service` | Configured `TodoService` |
| `current_user(credentials,auth_service)` | Bearer token + auth service | `CurrentUser(uid,email)` or HTTP 401 |
| `AuthServiceDep` etc. | `Annotated[..., Depends(...)]` | Reusable short route type/dependency |

`CurrentUser.uid` request body se nahi aati. Verified token aur selected
database user lookup se aati hai; isi value ko route todo `owner_uid` banati hai.

### 28.7 Router function reference

| Function | HTTP contract | DTO/service call | Success | Mapped error |
|---|---|---|---|---|
| `signup` | `POST /auth/signup` | `SignupInput -> AuthService.signup` | 201 `AuthResponse` | `ValidationException -> 400` |
| `login` | `POST /auth/login` | `LoginInput -> AuthService.login` | 200 `AuthResponse` | `ValidationException -> 401` |
| `list_todos` | `GET /todos` | `user.uid -> TodoService.list` | 200 array | Auth dependency 401 |
| `create_todo` | `POST /todos` | `CreateTodoInput -> TodoService.create` | 201 todo | `DomainError -> 400` |
| `complete_todo` | `PATCH /todos/{id}/complete` | `TodoActionInput -> complete` | 200 todo | Not found 404; other domain 400 |
| `delete_todo` | `DELETE /todos/{id}` | `TodoActionInput -> delete` | 204 empty | Not found 404 |

### 28.8 Security method reference

| Method | Important steps | Return/failure |
|---|---|---|
| `AuthSecurity(secret,database,minutes)` | Secret bytes; active DB; minutes to seconds | Configured shared security object |
| `normalize_email(email)` | `strip().lower()` | Canonical email |
| `hash_password(password)` | 16-byte random salt as 32 hex chars; PBKDF2-HMAC-SHA256 120,000 rounds | `salt:hash` |
| `password_matches(password,saved_hash)` | Split salt/hash, derive again, `compare_digest` | Boolean; malformed value -> `False` |
| `create_token(uid,email)` | JSON payload -> compact/sorted bytes -> URL-safe Base64 -> HMAC signature | `payload.signature` token |
| `read_token(token)` | Signature, JSON, active database, expiry and string fields validate | `(uid,email)` or `ValidationException` |
| `_derive_password_hash` | PBKDF2 calculation | Hex hash |
| `_read_payload` | Split/decode/compare/parse | Payload dict or safe invalid-session error |
| `_sign` | HMAC-SHA256 over encoded payload | Signature bytes |
| `_encode/_decode` | URL-safe Base64, padding restore | String/bytes conversion |

Token payload exactly four fields rakhta hai: `uid`, `email`, `database`, and
`expires_at`. Password, password hash aur display name token mein nahi hote.

### 28.9 Repository factory reference

| Function | Connection work | Returns |
|---|---|---|
| `create_repositories(settings)` | Shared `AuthSecurity` create; selected DB branch | `(TodoRepository, AuthRepository)` in this exact order |
| `_create_firestore_repositories` | Firebase app once initialize; project/document URL; one authorized session | Firestore todo + auth adapters |
| `_create_mongodb_repositories` | `MongoClient`, 5-second selection timeout, `ping`, database/collections | Mongo todo + auth adapters |
| `_create_postgresql_repositories` | URL required check; both repository constructors | PostgreSQL todo + auth adapters |

Factory todo repository pehle aur auth repository second return karti hai.
`app/main.py` bhi isi order mein unpack karta hai. Dono same `Settings` aur same
active database se bante hain.

### 28.10 Database adapter method reference

All adapters same contracts implement karte hain, lekin technical operation
different hai:

| Contract method | Firestore | MongoDB | PostgreSQL |
|---|---|---|---|
| Auth `signup` | Hashed-email document PATCH | `insert_one` | Parameterized `INSERT` |
| Auth `login` | Document GET by hashed email | `find_one(email)` | `SELECT ... WHERE email=%s` |
| Auth `authenticate` | Token then document/UID check | Token then `_id+email` query | Token then `id+email` query |
| Todo `save` | Document PATCH/upsert | `replace_one(upsert=True)` | `INSERT ... ON CONFLICT DO UPDATE` |
| Todo `get_by_id` | Owner path + todo document | `_id+owner_uid` filter | `id+owner_uid` WHERE |
| Todo `get_by_owner` | Paginated user subcollection | `find(owner_uid)` | WHERE owner, newest first |
| Todo `delete` | Document DELETE | `delete_one(id+owner)` | DELETE WHERE id+owner |

Private mapping helpers ka purpose:

- Firestore `_to_document/_to_entity`: REST typed fields and entity conversion.
- Firestore `_collection_url/_document_url`: safe encoded document paths.
- Firestore auth `_user_url`: normalized email ka SHA-256 document key.
- Mongo `_to_document/_to_entity`: document and domain mapping.
- PostgreSQL `_to_entity`: named row and domain mapping.
- PostgreSQL `_create_table`: missing schema create, existing data preserve.

---

## 29. Exact API request/response answer bank

### 29.1 Common request rules

Base URL in local development:

```text
http://127.0.0.1:8000
```

JSON requests use:

```http
Content-Type: application/json
```

Protected todo requests additionally use:

```http
Authorization: Bearer YOUR_LOGIN_TOKEN
```

`owner_uid` client request body mein nahi bhejta. Backend verified Bearer token
se current user nikal kar owner set karta hai.

### 29.2 Health check

Request:

```http
GET /
```

Response `200 OK`:

```json
{
  "status": "ok",
  "architecture": "DDD",
  "database": "mongodb"
}
```

Database value active process ke hisaab se `firestore`, `mongodb`, ya
`postgresql` hogi.

### 29.3 Signup

Request:

```http
POST /auth/signup
Content-Type: application/json
```

```json
{
  "email": "student@example.com",
  "password": "StrongPass123",
  "display_name": "Rana"
}
```

Response `201 Created`:

```json
{
  "uid": "a-database-specific-uuid",
  "email": "student@example.com",
  "token": "encoded-payload.encoded-signature",
  "message": "User created successfully"
}
```

Rules:

- Email Pydantic `EmailStr` format pass kare.
- Password minimum 6 characters.
- Missing display name ka default `User`.
- Spaces-only display name repository mein `User` ban jata hai.
- Email trim/lowercase hone ke baad selected DB mein unique hai.

Duplicate response example `400 Bad Request`:

```json
{
  "detail": "This email is already registered in MongoDB."
}
```

Database name adapter ke mutabiq change hota hai.

### 29.4 Login

Request:

```http
POST /auth/login
Content-Type: application/json
```

```json
{
  "email": "student@example.com",
  "password": "StrongPass123"
}
```

Response `200 OK`:

```json
{
  "uid": "same-selected-database-user-uuid",
  "email": "student@example.com",
  "token": "new-signed-token",
  "message": "Login successful"
}
```

Wrong password response `401 Unauthorized`:

```json
{
  "detail": "Invalid PostgreSQL email or password."
}
```

Login har call par new expiry wala token create karta hai. Token database table
ya collection mein save nahi hota.

### 29.5 List todos

Request:

```http
GET /todos
Authorization: Bearer YOUR_LOGIN_TOKEN
```

Empty response `200 OK`:

```json
[]
```

Response with data:

```json
[
  {
    "id": "todo-uuid",
    "title": "Prepare backend presentation",
    "priority": "HIGH",
    "is_completed": false,
    "created_at": "2026-11-11T04:00:00+00:00",
    "completed_at": null,
    "owner_uid": "verified-user-uuid"
  }
]
```

PostgreSQL newest-first explicitly sort karta hai. Current MongoDB aur Firestore
adapters explicit common sort guarantee nahi karti; API contract ko ordering
par depend nahi karna chahiye.

### 29.6 Create todo

Request:

```http
POST /todos
Authorization: Bearer YOUR_LOGIN_TOKEN
Content-Type: application/json
```

```json
{
  "title": "  Prepare backend presentation  ",
  "priority": "high"
}
```

Response `201 Created`:

```json
{
  "id": "new-todo-uuid",
  "title": "Prepare backend presentation",
  "priority": "HIGH",
  "is_completed": false,
  "created_at": "2026-11-11T04:00:00+00:00",
  "completed_at": null,
  "owner_uid": "verified-user-uuid"
}
```

Notice:

- Domain title ke outer spaces remove karta hai.
- Lowercase priority uppercase enum ban jati hai.
- UUID and timestamps server generate karta hai.
- New todo always incomplete hota hai.
- Owner verified token se aata hai.

### 29.7 Complete todo

Request:

```http
PATCH /todos/TODO_ID/complete
Authorization: Bearer YOUR_LOGIN_TOKEN
```

Response `200 OK`:

```json
{
  "id": "TODO_ID",
  "title": "Prepare backend presentation",
  "priority": "HIGH",
  "is_completed": true,
  "created_at": "2026-11-11T04:00:00+00:00",
  "completed_at": "2026-11-11T04:15:00+00:00",
  "owner_uid": "verified-user-uuid"
}
```

Same todo dobara complete karne par `400`:

```json
{
  "detail": "Todo is already completed."
}
```

Missing ya doosre user ka todo `404`:

```json
{
  "detail": "Todo was not found for this user."
}
```

Same 404 information disclosure rokta hai: caller ko yeh nahi bataya jata ke
ID kisi aur user ke paas exist karti hai ya bilkul exist nahi karti.

### 29.8 Delete todo

Request:

```http
DELETE /todos/TODO_ID
Authorization: Bearer YOUR_LOGIN_TOKEN
```

Success:

```text
204 No Content
empty response body
```

Service pehle owned todo read karti hai. Isliye missing/not-owned task par
silent success ke bajaye meaningful `404` milta hai.

### 29.9 Authentication failures

Missing/malformed Bearer header:

```text
401 Unauthorized
WWW-Authenticate: Bearer
```

```json
{
  "detail": "Not authenticated"
}
```

Expired token:

```json
{
  "detail": "Session expired. Please log in again."
}
```

Wrong-database token, for example Mongo token while PostgreSQL active:

```json
{
  "detail": "Please log in or sign up in the postgresql database."
}
```

Valid signature but deleted database user:

```json
{
  "detail": "PostgreSQL user no longer exists."
}
```

### 29.10 Pydantic `422` validation error

Invalid email, short password, short/long title, ya unsupported priority route
function tak pohanchne se pehle reject hoti hai. Typical shape:

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "password"],
      "msg": "String should have at least 6 characters",
      "input": "123"
    }
  ]
}
```

Exact `type`/message installed Pydantic version ke sath slightly change ho
sakti hai, lekin status `422` aur `detail` list FastAPI validation pattern hai.

---

## 30. Three-database comparison answer bank

### 30.1 One-screen comparison

| Question | Firestore | MongoDB | PostgreSQL |
|---|---|---|---|
| Database style | Cloud document DB | Document DB | Relational SQL DB |
| User storage | `auth_users` collection | `users` collection | `users` table |
| Todo storage | Per-user subcollection | Shared `todos` collection | Shared `todos` table |
| User primary identity | `uid` field; document ID = email hash | `_id` = user UUID | `id` primary key |
| Todo primary identity | Todo document ID + `id` field | `_id` = todo UUID | `id` primary key |
| Email uniqueness | Deterministic hashed document path + pre-check | Unique email index | UNIQUE email constraint |
| Owner isolation | UID embedded in document path | `owner_uid` filter | `owner_uid` WHERE condition |
| Todo upsert | REST PATCH | `replace_one(...,upsert=True)` | `ON CONFLICT (id) DO UPDATE` |
| User list performance | Per-user path, paginated | Owner index | Filter; current code has no explicit owner index |
| Data types | REST typed wrappers | JSON-like document values | SQL typed columns |
| Viewing tool | Firebase Console | MongoDB Compass | pgAdmin 4 |

### 30.2 User record comparison

Logical values same hain:

```text
uid + normalized email + display name + password hash
```

Physical difference:

```text
Firestore: document fields use stringValue wrappers
MongoDB:    _id stores UID; other values normal document fields
PostgreSQL: id/email/display_name/password_hash columns
```

Token kisi database mein stored nahi hota.

### 30.3 Todo record comparison

Logical values same hain:

```text
id, title, priority, is_completed,
created_at, completed_at, owner_uid
```

Datetime storage:

- Firestore adapter: ISO string inside REST `stringValue`.
- MongoDB adapter: ISO string.
- PostgreSQL adapter: native `TIMESTAMPTZ`.

Boolean storage:

- Firestore: `booleanValue`.
- MongoDB: native document boolean.
- PostgreSQL: native `BOOLEAN`.

### 30.4 Connection and startup comparison

| Database | Startup behavior |
|---|---|
| Firestore | Service-account certificate load; Firebase app once initialize; authorized REST session create |
| MongoDB | Client create; maximum server-selection wait 5 seconds; startup `ping`; indexes ensure |
| PostgreSQL | URL required; repository constructors connect and `CREATE TABLE IF NOT EXISTS` run |

Isliye wrong credentials/URL/database service usually startup par fail hota hai,
na ke first random user request par.

### 30.5 Same email different user kyun?

Example:

```text
rajputkhawarali@gmail.com in Firestore  -> UID A
rajputkhawarali@gmail.com in MongoDB    -> UID B
rajputkhawarali@gmail.com in PostgreSQL -> UID C
```

Reason:

1. Factory ek selected database ka auth adapter choose karti hai.
2. Signup duplicate check sirf us selected DB mein hota hai.
3. New UUID us DB ke account ke liye create hoti hai.
4. Password hash bhi usi DB mein save hota hai.
5. Token payload active database name se sign hota hai.

Isliye Firebase/Firestore signup MongoDB login automatically create nahi karta.
Database switch ke baad user ko us database mein separately signup/login karna
hota hai.

### 30.6 Same service code kaise reuse hota hai?

```text
TodoService -> TodoRepository contract
                    ^
                    |
        Firestore / MongoDB / PostgreSQL adapter
```

`TodoService` sirf `save`, `get_by_id`, `get_by_owner`, `delete` jaanti hai.
Actual PATCH, PyMongo call, ya SQL adapter ke andar hai. Isi ko dependency
inversion aur polymorphism kehte hain.

### 30.7 Database select karne ka decision

| Need | Better fit |
|---|---|
| Firebase ecosystem and managed cloud documents | Firestore |
| Flexible JSON-like documents and Compass exploration | MongoDB |
| Strong relational constraints, SQL queries, reporting | PostgreSQL |

Project ka purpose “winner database” choose karna nahi; same domain/application
architecture ke peeche adapters demonstrate karna hai.

### 30.8 Current consistency differences jo honestly batani chahiye

- PostgreSQL list `created_at DESC` order guarantee karti hai; other two current
  adapters explicit sort nahi karti.
- MongoDB owner index banata hai; PostgreSQL current `owner_uid` index create
  nahi karta.
- PostgreSQL current todos table mein users foreign key nahi hai.
- Firestore auth signup check-then-write hai; high concurrency mein atomic
  create/transaction stronger hoti.
- Yeh limitations architecture ko invalidate nahi kartin; production hardening
  items hain.

---

## 31. Advanced viva questions with ready answers

### Q36. User `owner_uid` body mein doosre user ki bhej de toh?

Create schema mein `owner_uid` field hai hi nahi. Route verified
`CurrentUser.uid` se `CreateTodoInput.owner_uid` banati hai. Client ownership
choose nahi kar sakta.

### Q37. Invalid token route tak pohanchta hai?

Protected route dependencies pehle resolve hoti hain. `current_user` token
verify na kare toh route function execute nahi hota aur response 401 hota hai.

### Q38. Pydantic aur domain dono title validate kyun karte hain?

Pydantic HTTP client ko early 422 feedback deta hai. Domain invariant ensure
karta hai ke entity kisi bhi entry point—HTTP, script, future worker, ya DB
restore—se invalid na bane. Yeh duplication nahi, two boundaries ki protection
hai.

### Q39. Lowercase `high` ka kya hota hai?

HTTP schema explicitly lowercase/uppercase variants allow karti hai.
`TodoItem.create` `priority.upper()` karke `Priority.HIGH` banata hai; response
aur storage canonical uppercase use karte hain.

### Q40. Display name response mein kyun nahi aata?

Current `AuthOutput` public auth needs ke liye only UID, normalized email aur
token rakhta hai. Display name account record mein stored hai but current UI/API
contract expose nahi karta. Future profile endpoint add kiya ja sakta hai.

### Q41. Password hashing auth repository mein kyun call hoti hai?

Repository account persistence workflow own karti hai, lekin algorithm shared
`AuthSecurity` infrastructure service provide karti hai. Is se three adapters
same policy use karte hain aur hashing duplicate nahi hoti.

### Q42. `AuthSecurity` domain mein kyun nahi?

PBKDF2, HMAC, Base64 aur system time technical implementation details hain.
Domain sirf auth operation ka contract define karta hai; cryptographic adapter
infrastructure concern hai.

### Q43. Token JWT kyun nahi hai?

Learning project compact custom HMAC token use karta hai to signing/database
binding clearly demonstrate ho. Production mein established JWT/OAuth/session
library better review, key rotation and ecosystem support de sakti hai.

### Q44. Kya Base64 token data secure/chhupa deta hai?

Nahi. Base64 encoding readable/reversible hai. HMAC data ko encrypt nahi karta;
sirf unauthorized modification detect karta hai. Isliye payload mein password
ya secret nahi rakha.

### Q45. Token logout/revocation kaise hoti hai?

Current token expiry tak cryptographically valid reh sakta hai, lekin every
request par database user existence check hota hai, so deleted user reject hota
hai. Per-token blacklist, session table, password-change revocation aur explicit
logout current implementation mein nahi; production improvement hai.

### Q46. Other user's existing todo ko 404 kyun milta hai, 403 kyun nahi?

Repository `id + owner_uid` together query karti hai. Non-owner ke liye result
“not found” hota hai. Yeh resource existence leak nahi karta, so 404 reasonable
security behavior hai.

### Q47. `save()` create aur update dono kyun karta hai?

Service ko persistence mechanism ka difference nahi pata hona chahiye. New todo
aur completed todo same entity hain; adapter upsert semantics se current entity
state persist karta hai.

### Q48. Delete se pehle read kyun hota hai?

Delete operations zero affected records par often silently succeed karti hain.
Pre-read ownership verify karta hai aur missing/not-owned case ko consistent 404
banata hai. Trade-off extra DB call hai.

### Q49. Routes normal `def` hain, `async def` kyun nahi?

Current PyMongo, Psycopg usage and Firestore `requests`-style session blocking
APIs hain. FastAPI sync route functions ko worker thread mein chala sakta hai,
isliye event loop directly block nahi hota. Full async scale ke liye async DB
drivers/adapters choose karne honge.

### Q50. `app.state` global variables se better kaise hai?

Dependencies request ke app instance se configured services leti hain. Multiple
app instances different settings/fakes use kar sakti hain, aur routes concrete
module globals se tightly coupled nahi hoti.

### Q51. Database switch running server ke andar live kyun nahi hota?

Settings `lru_cache` se startup par load hoti hain; repositories/connections bhi
startup par create hote hain. Environment change existing process ko rewire nahi
karta. Server restart clean consistent repository pair banata hai.

### Q52. `DATABASE=firebase` chalega?

Haan. `selected_database` beginner-friendly `firebase` alias ko canonical
`firestore` banata hai. Health response aur token canonical `firestore` value
use karte hain.

### Q53. Factory same database mein auth aur todos kaise guarantee karti hai?

One `database = settings.selected_database` branch one shared `AuthSecurity`
aur matching todo/auth adapter pair return karti hai. Separate independent
factory calls nahi, isliye mixed Mongo-auth/Postgres-todo configuration current
design mein possible nahi.

### Q54. `firebase-admin` use hone ka matlab Firebase Auth use ho rahi hai?

Nahi. Firebase Admin service-account credential aur authorized Firestore access
ke liye use hota hai. Signup/login records custom `auth_users` collection mein
selected-database repository manage karti hai.

### Q55. Firestore email ko SHA-256 key kyun, encryption kyun nahi?

Deterministic key exact document lookup aur normalized-email uniqueness deti
hai. SHA-256 one-way hash hai, encryption nahi. Actual email document field mein
stored hai, so hash privacy/anonymity guarantee nahi.

### Q56. MongoDB `_id` ObjectId kyun nahi?

Cross-database consistency ke liye application UUID strings generate karti hai.
Same entity identity format Firestore, MongoDB, PostgreSQL aur API mein portable
rehta hai.

### Q57. PostgreSQL foreign key kyun nahi hai?

Current beginner-friendly schema ownership string se enforce karta hai and
service/auth flow valid UID provide karti hai. Production relational design
`todos.owner_uid REFERENCES users(id)` plus index and deletion policy add kar
sakta hai.

### Q58. PostgreSQL context manager kya guarantee karta hai?

Connection block success par transaction commit, exception par rollback, aur
block exit par connection cleanup manage karta hai. Manual commit/close code
repeat nahi hota.

### Q59. Infrastructure DB error todo route mein kya ban sakta hai?

Expected domain/auth errors explicitly map hote hain. Unexpected unhandled
connection/programming error middleware log ke sath 500 banega. Production mein
central exception handler aur sanitized error monitoring add karni chahiye.

### Q60. Current list ordering all databases mein same hai?

Nahi. PostgreSQL explicit newest-first hai; MongoDB/Firestore current adapter
natural/API order use karti hain. Consistent product requirement ho toh
repository contract mein ordering define karke all adapters implement karenge.

### Q61. `@lru_cache` ka downside kya hai?

Process ke andar changed `.env` automatically reload nahi hoti. Benefit stable
single settings object and fewer reads hai. Development switch ke baad process
restart expected hai; tests cache clear ya explicit settings inject kar sakti
hain.

### Q62. `ContextVar` simple global request ID se better kyun hai?

Concurrent requests same process/thread execution context overlap kar sakti
hain. `ContextVar` har async context ka label isolate karta hai; `finally` reset
next request ko old label inherit karne se rokta hai.

### Q63. Project truly database-independent hai?

Domain and application selected database se independent hain; API contract bhi
same hai. Complete system external capabilities se totally independent nahi—
infrastructure adapters intentionally database-specific hain. Correct claim
“business logic and use cases are storage-independent” hai.

### Q64. Professional production mein sab se pehle kya improve karenge?

Established auth/session mechanism, secret manager, rate limiting, migrations,
connection pooling, database indexes/foreign keys, consistent ordering,
central error handling, integration CI and observability. Priority deployment
risk aur expected scale par depend karegi.

### Q65. Ek sentence mein poora backend kaise explain karenge?

> “FastAPI presentation verified request ko application use case tak bhejti
> hai, domain business rule decide karta hai, selected infrastructure adapter
> same database mein user/todo persist karta hai, aur result database-independent
> response ban kar client ko milta hai.”

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
