# 🏛️ Architectural Masterclass: Domain-Driven Design (DDD / Onion) vs Model-View-Controller (MVC)

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg?style=for-the-badge&logo=fastapi&logoColor=white)
![Firebase](https://img.shields.io/badge/Firebase_Firestore-FFCA28.svg?style=for-the-badge&logo=firebase&logoColor=black)
![Architecture](https://img.shields.io/badge/Architecture-DDD%20vs%20MVC-blueviolet.svg?style=for-the-badge)
![Status](https://img.shields.io/badge/Production-Ready-success.svg?style=for-the-badge)

<p align="center">
  <b>Ek Hi Problem, Do Mukhtalif Architectures: Production-Grade Comparison & Deep Dive</b><br>
  <i>Written for Full-Stack Engineers & Backend Architects (In Fluent Roman Urdu & Technical English)</i>
</p>

</div>

---

> [!NOTE]
> **Yeh Repository Kis Cheez Ke Baare Mein Hai?**  
> Is workspace mein humne ek hi **TodoFlow Application** ko do mukhtalif software engineering patterns ke sath build kiya hai:
> 1. [`backend/DDD/`](../backend/DDD/) ➔ **Domain-Driven Design (DDD) + Onion Architecture** (Port `8000`)
> 2. [`backend/MVC/`](../backend/MVC/) ➔ **Traditional Model-View-Controller (MVC)** (Port `8001`)
> 
> Dono services same business requirements follow karti hain. MVC Firebase Auth/Firestore use karta hai; DDD mein authentication aur todos dono ko terminal se **Firestore, MongoDB, ya PostgreSQL** par switch kiya ja sakta hai.

---

## 📑 Table of Contents

1. [🧠 What is DDD? (The Core Mental Model)](#1--what-is-ddd-the-core-mental-model)
2. [🧅 What is Onion Architecture & The Golden Rule](#2--what-is-onion-architecture--the-golden-rule)
3. [⚡ How Everything Connects (The Full Flow Diagram)](#3--how-everything-connects-the-full-flow-diagram)
4. [🔗 DDD / Onion Concept Mapping Table](#4--ddd--onion-concept-mapping-table)
5. [🔍 Layer-by-Layer & File-by-File Breakdown (Current Codebase)](#5--layer-by-layer--file-by-file-breakdown-current-codebase)
   - [Layer 1: Domain (`app/domain/` — The Heart ❤️)](#layer-1-domain-appdomain--the-heart-️)
   - [Layer 2: Application (`app/application/` — The Orchestrator 🎯)](#layer-2-application-appapplication--the-orchestrator-)
   - [Layer 3: Infrastructure (`app/infrastructure/` — The Adapters 🔧)](#layer-3-infrastructure-appinfrastructure--the-adapters-)
   - [Layer 4: Presentation (`app/presentation/` — The Gateway 🌐)](#layer-4-presentation-apppresentation--the-gateway-)
   - [Composition Root (`main.py` & Dependency Wiring)](#composition-root-mainpy--dependency-wiring)
   - [Terminal Logger (`app/logging.py` — Bilingual Traceability 📋)](#terminal-logger-apploggingpy--bilingual-traceability-)
   - [🏢 Enterprise Scale: Yeh layers mazeed kya kya kar sakti hain? (What, When, How)](#-enterprise-scale-yeh-layers-mazeed-kya-kya-kar-sakti-hain-what-when-how)
6. [🎮 Traditional MVC Architecture Deep Dive (`backend/MVC/`)](#6--traditional-mvc-architecture-deep-dive-backendmvc)
7. [⚖️ SOLID Principles: DDD vs MVC Ka Muqabla](#7-️-solid-principles-ddd-vs-mvc-ka-muqabla)
8. [📬 Request & Response Flows (Step-by-Step Traces)](#8--request--response-flows-step-by-step-traces)
9. [📊 Pros & Cons (Faide aur Nuqsanat)](#9--pros--cons-faide-aur-nuqsanat)
10. [📋 Detailed Side-by-Side Comparison Matrix](#10--detailed-side-by-side-comparison-matrix)
11. [🎯 Final Verdict: Kab Konsa Architecture Chunein?](#11--final-verdict-kab-konsa-architecture-chunein)
12. [🚀 How to Run Both Projects](#12--how-to-run-both-projects)

---

## 1. 🧠 What is DDD? (The Core Mental Model)

**DDD (Domain-Driven Design)** ka matlab hai ke aap apna system **Business Problem aur Domain Rules** ke gird design karte hain, frameworks ya database ke gird nahi.

Think of it this way:

> ❌ **Without DDD (Database-Centric / Traditional CRUD):**  
> *"Hamare paas Firestore mein ek `todos` collection hai, chalo controllers mein direct insert, update, aur delete queries likh dete hain."*
>
> ✅ **With DDD (Domain-Centric / Behavior-Driven):**  
> *"Hamare business mein ek **Todo** ke sakht rules hain: title minimum 3 aur maximum 120 characters ka hona chahiye, priority `LOW`/`MEDIUM`/`HIGH` honi chahiye, har todo ka ek `owner_uid` lazmi hona chahiye, aur agar ek baar task complete ho jaye toh wo **dobara complete nahi ho sakta**. Pehle hum code likh kar **in rules ko 100% guarantee aur encapsulate** karenge. Database (Firestore, MongoDB, ya PostgreSQL) baad mein adapter ke zariye plug hoga."*

**Key Takeaway:** Aapke business rules ek mukammal azad jagah rehte hain (**Domain Layer**). Unhe is baat se koi matlab nahi ke aap Firebase Firestore, PostgreSQL, ya MongoDB use kar rahe hain.

---

## 2. 🧅 What is Onion Architecture & The Golden Rule

Onion Architecture aapke codebase ko concentric rings (pyaz ke chilkon) mein organize karti hai:

```text
                    ┌─────────────────────────────────────────┐
                    │           Presentation Layer            │  ← FastAPI Router, DTOs, HTTP Auth
                    │      (what the outside world sees)      │
                    ├─────────────────────────────────────────┤
                    │           Application Layer             │  ← Use Cases (Workflow Orchestration)
                    │        (orchestrates the actions)       │
                    ├─────────────────────────────────────────┤
                    │              Domain Layer               │  ← Entities, Value Objects, Rules, Ports
                    │        (the HEART of your app)          │     (pure framework-free business logic)
                    ├─────────────────────────────────────────┤
                    │          Infrastructure Layer           │  ← Firestore, MongoDB, PostgreSQL auth + todos
                    │      (technical details & adapters)     │
                    └─────────────────────────────────────────┘
```

### 🏆 The Golden Rule (Dependency Inversion)

> **Dependencies Hamesha Bahir Se Andar Ki Taraf Jati Hain. Inner Layers KABHI Outer Layers Par Depend Nahi Kartein.**

1. `Domain Layer` kisi doosri layer ko nahi janti — na FastAPI ko, na Firebase ko, na requests library ko. Yeh 100% pure Python code hai.
2. `Application Layer` sirf `Domain Layer` ke models aur repository interfaces ko janti hai.
3. `Infrastructure Layer` aur `Presentation Layer` bahir ki outer rings hain jo inner contracts ko implement aur consume karti hain.

Iska faida yeh hai ke database switch karne par Domain ya Application Layer ki **ek single line bhi badalni nahi parti**!

---

## 3. ⚡ How Everything Connects (The Full Flow Diagram)

Jab client (React app ya Postman) **`POST /todos`** request bhejta hai, toh DDD mein data ka safar kaisa hota hai:

```text
  Client (React Frontend / Postman)
       │  [HTTP POST /todos with Bearer Token]
       ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 1. PRESENTATION LAYER — routes.py & dto.py                  │
  │    • HTTPBearer token extract karta hai                    │
  │    • Selected AuthRepository se token verify karta hai     │
  │    • Pydantic CreateTodoRequest se payload validate karta hai│
  │    • Application CreateTodoInput DTO banata hai             │
  │    • todo_service.create(data) call karta hai               │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 2. APPLICATION LAYER — todo_service.py                      │
  │    • Workflow orchestrate karta hai                         │
  │    • Domain Entity factory TodoItem.create(...) call karta hai│
  │    • repository.save(todo) call karta hai                   │
  │    • to_output(todo) se plain TodoOutput DTO return karta hai│
  │    • Terminal mein bilingual trace log karta hai            │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
            ┌────────────────────┴────────────────────┐
            ▼                                         ▼
  ┌──────────────────────────────┐    ┌───────────────────────────────────┐
  │ 3a. DOMAIN — models.py       │    │ 3b. INFRASTRUCTURE — separate files│
  │  TodoItem.create()           │    │  Selected TodoRepository adapter  │
  │  • TaskTitle (min 3, max 120)│    │  • FirestoreTodoRepository        │
  │  • Priority Enum verification│    │  • MongoTodoRepository            │
  │  • Generates UUID & UTC time │    │  • PostgreSQLTodoRepository       │
  │  • Binds owner_uid           │    │  DATABASE terminal setting        │
  │  TodoRepository (ABC contract│    │  selects one adapter              │
  └──────────────────────────────┘    └───────────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 4. PRESENTATION RESPONSE — routes.py                        │
  │    • TodoOutput DTO ko TodoResponse mein wrap karta hai     │
  │    • 201 Created status code ke sath JSON client ko bhejta hai│
  └─────────────────────────────────────────────────────────────┘
```

---

## 4. 🔗 DDD / Onion Concept Mapping Table

Dono projects mein concepts ka practical mapping:

| Architectural Concept | Asal Maqsad | DDD Implementation ([`backend/DDD/`](../backend/DDD/)) | MVC Implementation ([`backend/MVC/`](../backend/MVC/)) |
|---|---|---|---|
| **Entity (Aggregate Root)** | Unique ID aur business rules wali rich object | `TodoItem` in [`app/domain/todo.py`](../backend/DDD/app/domain/todo.py) | Plain Python dictionary in [`src_mvc/models/todo_model.py`](../backend/MVC/src_mvc/models/todo_model.py) |
| **Value Object** | Immutable validated types | `TaskTitle`, `Priority` in [`app/domain/todo.py`](../backend/DDD/app/domain/todo.py) | String + Pydantic validation checks |
| **Domain Exceptions** | Business invariants violate hone par aane wale errors | `DomainError`, `InvalidTaskTitleError`, `TaskAlreadyCompletedError` | Custom exceptions in [`src_mvc/models/todo_model.py`](../backend/MVC/src_mvc/models/todo_model.py) |
| **Repository Port (Interface)** | Data storage ka contract (abstraction) | `TodoRepository(ABC)`, `AuthRepository(ABC)` | **Koi interface nahi.** Controller direct Firestore se baat karta hai |
| **Repository Adapter** | Concrete storage engine | Har DB ka `TodoRepository` + `AuthRepository` adapter | Direct Firestore SDK queries in `todo_controller.py` + `firebase.py` |
| **Use Case (Service)** | Workflow coordinator | `TodoService`, `AuthService` in [`app/application/`](../backend/DDD/app/application/) | Direct controller methods in `todo_controller.py` & `auth_controller.py` |
| **Application DTO** | Layer-to-layer data container | `CreateTodoInput`, `TodoActionInput`, `TodoOutput`, `AuthOutput` | Not separated; uses Pydantic View models directly |
| **Presentation DTO** | HTTP API schemas | `CreateTodoRequest`, `TodoResponse`, `SignupRequest`, `LoginRequest` | `CreateTodoRequest`, `TodoResponse` in `todo_views.py` |
| **Composition Root** | Wiring aur Dependency Injection ki jagah | `app/main.py` (`create_app()` + `app.state`) | `main_mvc.py` (simple router mount) |
| **Observability** | Request trace aur step-by-step logging | `app/logging.py` (Bilingual English + Roman Urdu logs) | Standard print statements in controller |

---

## 5. 🔍 Layer-by-Layer & File-by-File Breakdown (Current Codebase)

### Layer 1: Domain ([`app/domain/`](../backend/DDD/app/domain/) — The Heart ❤️)
Yeh application ka sab se sacred hissa hai. Isme zero framework dependencies hain (FastAPI, Firebase, ya requests ka koi zikar nahi).

#### 1. Value Object: `TaskTitle`
```python
@dataclass(frozen=True)
class TaskTitle:
    """A title that always contains 3 to 120 characters."""
    value: str

    def __post_init__(self):
        clean_title = self.value.strip() if self.value else ""
        if len(clean_title) < 3:
            raise InvalidTaskTitleError("Title must have at least 3 characters.")
        if len(clean_title) > 120:
            raise InvalidTaskTitleError("Title cannot exceed 120 characters.")
        object.__setattr__(self, "value", clean_title)
```
> **Kyun zaroori hai?**  
> Plain string empty bhi ho sakti hai aur garbage bhi. Lekin agar system mein ek `TaskTitle` object ban chuka hai, toh yeh **by definition valid** hai. Kahin bhi bar bar `len()` check karne ki zaroorat nahi parti.

#### 2. Entity / Aggregate Root: `TodoItem`
```python
@dataclass
class TodoItem:
    """Main todo entity containing its own business rule."""
    id: str
    title: TaskTitle
    priority: Priority
    is_completed: bool
    created_at: datetime
    owner_uid: str
    completed_at: datetime | None = None

    @classmethod
    def create(cls, title: str, priority: str, owner_uid: str):
        return cls(
            id=str(uuid.uuid4()),
            title=TaskTitle(title),
            priority=Priority(priority.upper()),
            is_completed=False,
            created_at=datetime.now(timezone.utc),
            owner_uid=owner_uid,
        )

    def complete(self) -> None:
        if self.is_completed:
            raise TaskAlreadyCompletedError("Todo is already completed.")
        self.is_completed = True
        self.completed_at = datetime.now(timezone.utc)
```
> **Kyun zaroori hai?**  
> Business rule *"Jo task pehle se completed ho, wo dobara complete nahi ho sakta"* kisi controller ya database mein nahi, balki entity ke andar band hai. Agar koi developer controller mein check bhool bhi jaye, entity invariant ko violate nahi hone degi.

#### 3. Storage Contract: `TodoRepository(ABC)`
```python
class TodoRepository(ABC):
    """Storage contract implemented by memory and Firestore repositories."""
    @abstractmethod
    def save(self, todo: TodoItem) -> None:
        pass

    @abstractmethod
    def get_by_id(self, todo_id: str, owner_uid: str) -> TodoItem | None:
        pass

    @abstractmethod
    def get_by_owner(self, owner_uid: str) -> list[TodoItem]:
        pass

    @abstractmethod
    def delete(self, todo_id: str, owner_uid: str) -> None:
        pass
```
> **Kyun zaroori hai?**  
> Domain kehta hai: *"Mujhe ek aesa storage chahiye jo save, get, aur delete kar sake."* Domain yeh nahi kehta ke wo Firebase ho ya Postgres. Yeh **Dependency Inversion** hai.

---

### Layer 2: Application ([`app/application/`](../backend/DDD/app/application/) — The Orchestrator 🎯)

Application layer business rules define nahi karti, balki **workflows** ko coordinate karti hai.

#### 1. DTOs ([`app/application/dto.py`](../backend/DDD/app/application/dto.py))
```python
@dataclass(frozen=True)
class CreateTodoInput:
    title: str
    priority: str
    owner_uid: str

@dataclass(frozen=True)
class TodoOutput:
    id: str
    title: str
    priority: str
    is_completed: bool
    created_at: str
    completed_at: str | None
    owner_uid: str
```

#### 2. Use Cases ([`app/application/`](../backend/DDD/app/application/))
```python
class TodoService:
    """Create, list, complete, and delete todo use cases."""

    def __init__(self, repository: TodoRepository):
        self.repository = repository

    def create(self, data: CreateTodoInput) -> TodoOutput:
        todo = TodoItem.create(data.title, data.priority, data.owner_uid)
        self.repository.save(todo)
        log_step(
            "Application",
            f"Todo {todo.id} created and saved.",
            f"Todo {todo.id} create karke save kar diya.",
        )
        return to_output(todo)

    def complete(self, data: TodoActionInput) -> TodoOutput:
        todo = self.repository.get_by_id(data.todo_id, data.owner_uid)
        if not todo:
            raise TodoNotFoundError("Todo was not found for this user.")
        todo.complete()
        self.repository.save(todo)
        log_step(
            "Application",
            "Todo completed and saved.",
            "Todo complete karke save kar diya.",
        )
        return to_output(todo)
```
> **Notice:** `TodoService` ko yeh nahi pata ke `self.repository` Firestore, MongoDB, ya PostgreSQL hai. Wo sirf abstract `TodoRepository` interface methods call karta hai.

---

### Layer 3: Infrastructure ([`app/infrastructure/`](../backend/DDD/app/infrastructure/) — The Adapters 🔧)

Yeh layer interfaces ki **Concrete Implementations** deti hai:

1. **`FirestoreTodoRepository`**: Google Cloud Firestore REST API ke sath HTTPS ke zariye baat karti hai.
2. **`MongoTodoRepository`**: MongoDB documents ko PyMongo ke zariye read/write karti hai.
3. **`PostgreSQLTodoRepository`**: PostgreSQL `todos` table ko Psycopg ke zariye read/write karti hai.
4. Har database ka **AuthRepository** usi database mein user save karta hai. `AuthSecurity` password hash, Google ID token verification aur database-specific JWT handle karta hai. Same Google account bhi har selected database mein separate local UID leta hai.

```python
class FirestoreTodoRepository(TodoRepository):
    """Persistent Firestore storage over HTTPS; no gRPC DLL is needed."""

    def __init__(self, project_id: str, credentials):
        self.session = AuthorizedSession(credentials)
        project = quote(project_id, safe="")
        database = quote(os.environ["FIRESTORE_DATABASE_ID"], safe="()")
        api_url = os.environ["FIRESTORE_API_URL"].rstrip("/")
        self.user_collection = os.environ["FIRESTORE_USER_COLLECTION"]
        self.todo_collection = os.environ["FIRESTORE_TODO_COLLECTION"]
        self.base_url = (
            f"{api_url}/projects/{project}/databases/{database}/documents"
        )

    def save(self, todo: TodoItem) -> None:
        document_url = f"{self._user_document_path(todo.owner_uid)}/{self.todo_collection}/{quote(todo.id, safe='')}"
        response = self.session.patch(
            document_url,
            json={"fields": self._to_fields(todo)},
            timeout=15,
        )
        if response.status_code not in (200, 201):
            raise ValidationException(f"Firestore save failed: {response.text}")
```

---

### Layer 4: Presentation ([`app/presentation/`](../backend/DDD/app/presentation/) — The Gateway 🌐)

FastAPI endpoints jo incoming HTTP requests ko handle karte hain aur tokens verify karte hain.

```python
# app/presentation/routers/todos.py
@todo_router.post("", response_model=TodoResponse, status_code=201)
def create_todo(
    request: CreateTodoRequest,
    user: CurrentUserDep,
    todo_service: TodoServiceDep,
):
    log_step("Presentation", "Create todo request received.", "Create todo request mil gayi.")
    try:
        return todo_service.create(CreateTodoInput(
            request.title,
            request.priority,
            user.uid,
        ))
    except DomainError as error:
        raise HTTPException(400, str(error)) from error
```

---

### Composition Root (`main.py` & Dependency Wiring)

`main.py` wo markazi jagah hai jahan tamam layers aapas mein connect hoti hain:

```python
# 1. Select one database for both auth and todos
database = get_selected_database()
todo_repository, auth_repository = create_repositories(database)

# 2. Instantiate Use Cases and inject matching repositories
app.state.todo_service = TodoService(todo_repository)
app.state.auth_service = AuthService(auth_repository)

# 3. Mount API Routers
app.include_router(auth_router)
app.include_router(todo_router)
```

---

### Terminal Logger ([`app/logging.py`](../backend/DDD/app/logging.py) — Bilingual Traceability 📋)

`app/logging.py` har request aur har architectural layer ki execution ko terminal mein English aur Roman Urdu dono mein print karta hai:

```text
20:25:31 | INFO  | [REQ-001] | Presentation | Create todo request received.
         |       |             Create todo request mil gayi.
20:25:31 | INFO  | [REQ-001] | Auth         | Token is valid for developer@example.com.
         |       |             developer@example.com ka token valid hai.
20:25:31 | INFO  | [REQ-001] | Application  | Todo 4f5a... created and saved.
         |       |             Todo 4f5a... create karke save kar diya.
20:25:31 | INFO  | [REQ-001] | Infrastructure| Saved todo in Firestore.
         |       |             Todo Firestore mein save hua.
```

---

### 🏢 Enterprise Scale: Yeh layers mazeed kya kya kar sakti hain? (What, When, How)

| Layer | Hamare Project Mein | Enterprise Scale Par (What, When, How) |
|---|---|---|
| **Domain** | 1 Entity (`TodoItem`), 1 Value Object (`TaskTitle`) | **WHAT:** 50+ Aggregates, Domain Events, Policy Specifications.<br>**WHEN:** Banking, Insurance, ya Airline reservation system jahan complex financial rules hon.<br>**HOW:** Entity state change par `DomainEvent` emit karti hai (e.g. `PaymentSettledDomainEvent`). |
| **Application** | `TodoService` & `AuthService` | **WHAT:** CQRS (Command Query Responsibility Segregation), background celery workers, email notifications.<br>**WHEN:** Million requests per day jahan reads ko write operations se alag scale karna ho.<br>**HOW:** Commands Write-DB ko update karti hain, Queries Read-Replica se fast JSON return karti hain. |
| **Infrastructure** | Firestore + MongoDB + PostgreSQL adapters | **WHAT:** Polyglot Persistence (PostgreSQL + Redis Cache + Kafka Event Stream + ElasticSearch).<br>**WHEN:** High-traffic e-commerce systems.<br>**HOW:** Write Firestore/Postgres mein hoti hai aur sath hi Redis cache aur Kafka topic mein push hoti hai. |
| **Presentation** | FastAPI REST Endpoints | **WHAT:** Multi-protocol Gateways (REST API + GraphQL + gRPC + WebSockets).<br>**WHEN:** Jab web frontend ko REST, mobile app ko GraphQL, aur internal microservices ko high-speed gRPC chahiye ho.<br>**HOW:** Multiple routers same Application Use Cases ko reuse karte hain. |

---

## 6. 🎮 Traditional MVC Architecture Deep Dive ([`backend/MVC/`](../backend/MVC/))

Hamare [`backend/MVC`](../backend/MVC/) project mein yeh sab kaam 3 traditional layers mein hota hai:

```text
  [Client (Postman / Browser)]
              │
              ▼
    [todo_controller.py] ◄───► [todo_views.py] (Request/Response schemas)
              │
              ├───► [todo_model.py] (Helper functions & Dictionaries)
              │
              └───► [firebase.py] (Direct Firestore SDK collection write)
```

### MVC Controller Code Example:
```python
# backend/MVC/src_mvc/controllers/todo_controller.py
@router.post("", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(req: CreateTodoRequest):
    try:
        # 1. Model helper creates a plain dictionary
        todo = create_todo_dict(title=req.title, priority=req.priority)
        
        # 2. Controller DIRECTLY writes to Firestore database
        _collection().document(todo["id"]).set(todo)
        
        # 3. View model formats the response
        return TodoResponse(**todo)
    except InvalidTitleError as err:
        raise HTTPException(status_code=400, detail=str(err))
```

> **Farq:** MVC mein controller ek hi waqt mein HTTP route sambhal raha hai, database query execute kar raha hai, aur model helper ko call kar raha hai. Yeh choti applications ke liye tezi se banti hai, lekin system bara hone par **Fat Controllers** ban jate hain jinhe test aur maintain karna intehayi mushkil hota hai.

---

## 7. ⚖️ SOLID Principles: DDD vs MVC Ka Muqabla

| Principle | DDD / Onion Implementation | Traditional MVC Implementation |
|---|---|---|
| **S - Single Responsibility** | **100% Strictly Followed:**<br>• Presentation = Sirf HTTP requests aur auth verification.<br>• Use Case = Sirf workflow coordination.<br>• Entity = Sirf business invariant rules.<br>• Repository = Sirf database read/write. | **Violated in Controller:**<br>Controller ek hi function ke andar HTTP status codes, database queries, aur orchestration sab kuch mix kar deta hai. |
| **O - Open / Closed** | **100% Strictly Followed:**<br>Code extension ke liye open hai, modification ke liye closed. Naya storage (e.g. Postgres) add karne ke liye sirf naya repository adapter likhna parta hai. Domain aur Use Cases touch nahi hote. | **Violated:**<br>Database badalne ke liye `todo_controller.py` ke andar har single route handler ko rewrite karna parega. |
| **L - Liskov Substitution** | **100% Strictly Followed:**<br>Firestore, MongoDB, aur PostgreSQL repositories `TodoRepository` contract ki jagah swap ho sakti hain. | **No Contracts:**<br>Controller direct concrete Firestore SDK par depend karta hai. Koi formal abstraction nahi hoti. |
| **I - Interface Segregation** | **100% Strictly Followed:**<br>`TodoRepository` sirf wahi 4 methods expose karta hai jo use cases ko chahiye (`save`, `get_by_id`, `get_by_owner`, `delete`). | **Violated:**<br>Controller raw Firestore Client import karta hai jisme hazaron unused functions hote hain. |
| **D - Dependency Inversion** | **100% Strictly Followed:**<br>High-level use cases low-level Firestore par depend nahi karte; dono abstract interface (`TodoRepository`) par depend karte hain. | **Violated:**<br>High-level route handlers directly low-level `firebase.get_db()` client par depend karte hain. |

---

## 8. 📬 Request & Response Flows (Step-by-Step Traces)

Dono servers active hain:
- **DDD Server:** `http://127.0.0.1:8000`
- **MVC Server:** `http://127.0.0.1:8001`

---

### Flow 1: Health Check (`GET /`)

#### Port 8000 (DDD)
```http
GET http://127.0.0.1:8000/ HTTP/1.1
```
```json
{
  "status": "ok",
  "architecture": "DDD"
}
```

#### Port 8001 (MVC)
```http
GET http://127.0.0.1:8001/ HTTP/1.1
```
```json
{
  "status": "ok",
  "architecture": "MVC"
}
```

---

### Flow 2: Create Todo (`POST /todos`)

#### HTTP Request
```http
POST http://127.0.0.1:8000/todos HTTP/1.1
Content-Type: application/json
Authorization: Bearer <FIREBASE_ID_TOKEN>

{
  "title": "Master Software Architecture",
  "priority": "HIGH"
}
```

#### Execution Trace:
- **MVC (Port 8001):**  
  `todo_controller.py:create_todo()` ➔ `todo_model.py:create_todo_dict()` ➔ `_collection().document().set(todo)` ➔ `TodoResponse`.
- **DDD (Port 8000):**  
  `routers/todos.py:create_todo()` ➔ `current_user` token check ➔ `CreateTodoInput` DTO ➔ `TodoService.create()` ➔ `TodoItem.create()` (validates `TaskTitle`) ➔ `TodoRepository.save()` ➔ `FirestoreTodoRepository.save()` (HTTPS REST) ➔ `TodoOutput` ➔ `TodoResponse`.

#### Expected Response (201 Created):
```json
{
  "id": "e6a4b11f-c419-4cb5-829d-0125927c6f05",
  "title": "Master Software Architecture",
  "priority": "HIGH",
  "is_completed": false,
  "created_at": "2026-10-30T10:45:00.123456Z",
  "completed_at": null,
  "owner_uid": "user_123456"
}
```

---

### Flow 3: Complete Todo & Business Invariant Violation (`PATCH /todos/{id}/complete`)

* **First Request:** 200 OK return karta hai, `is_completed: true` aur `completed_at` timestamp set karta hai.
* **Second Request (Attempting to complete an already completed task):**
  - **Status Code:** `400 Bad Request`
  - **Response Body:**
    ```json
    {
      "detail": "Todo is already completed."
    }
    ```
  - **Architectural Farq:** MVC mein yeh check ek helper function karta hai jisko controller chahay toh bypass kar sakta hai. DDD mein yeh check **`TodoItem` Entity ke andar locked hai**—koi bhi use case ya controller Entity ke invariant ko bypass nahi kar sakta!

---

## 9. 📊 Pros & Cons (Faide aur Nuqsanat)

### 📊 Traditional MVC Architecture
| 👍 Pros (Faide) | 👎 Cons (Nuqsanat) |
|---|---|
| **Fast Initial Velocity:** Chand ghanton mein complete API live ho jata hai. | **Fat Controllers:** Code bara hone par controllers hazaron lines ke messy ho jate hain. |
| **Kam Files:** Sirf 5–6 files mein poora project khatam ho jata hai. | **Tight DB Coupling:** Database badalna matlab pure project ko scratch se rewrite karna. |
| **Low Mental Overhead:** Junior developers asani se samajh jate hain. | **Hard to Unit Test:** Har test ke liye real database emulator chalana parta hai. |

### 🏛️ DDD / Onion Architecture
| 👍 Pros (Faide) | 👎 Cons (Nuqsanat) |
|---|---|
| **Zero Database Coupling:** Core business logic database se 100% independent hai. | **More Files:** DTOs, interfaces, aur mappers ki wajah se zyada initial structure hota hai. |
| **Database Independence:** Repository contract ki wajah se adapters ko separately test kiya ja sakta hai. | **Learning Curve:** Team ko Aggregates, Ports aur Dependency Inversion samajhna parta hai. |
| **Long-Term Maintainability:** 5-10 saal tak code clean, modular aur predictable rehta hai. | **Overkill for Tiny Apps:** Simple 2-field CRUD apps ke liye heavy feel hota hai. |

---

## 10. 📋 Detailed Side-by-Side Comparison Matrix

| Paimana (Metric) | Traditional MVC (`backend/MVC/`) | DDD / Onion (`backend/DDD/`) |
|---|---|---|
| **Default Port** | `http://127.0.0.1:8001` | `http://127.0.0.1:8000` |
| **Total Files** | ~6 files | ~8 clean, focused modules |
| **Dependency Direction** | Controller ➔ Model ➔ Database | Outer Layers ➔ Inner Domain (Inverted) |
| **Business Invariants** | Helper functions in model | Encapsulated inside Entity & Value Objects |
| **Workflow Coordination** | Controller route function | Dedicated `TodoService` & `AuthService` |
| **Database Coupling** | Tight (`get_db()` in controller) | Loose (`TodoRepository` abstract interface) |
| **Storage Modes Supported** | Firestore only | Firestore, MongoDB, or PostgreSQL |
| **Database Selection** | Code is tied to Firestore | One `DATABASE` terminal setting |
| **Database Swap Cost** | 80% controller code rewrite | 0% domain/use case rewrite, sirf naya adapter |
| **SOLID Compliance** | Partial (S aur D violated) | **100% Strict SOLID Compliance** |
| **Best Used For** | MVPs, Small Prototypes, Simple CRUD | Enterprise, SaaS, FinTech, Scalable Systems |

---

## 11. 🎯 Final Verdict: Kab Konsa Architecture Chunein?

```text
                  [Start New Project]
                           │
                           ▼
             Is business logic complex?
                     │           │
                    YES          NO ───► [Choose MVC]
                     │
                     ▼
         Will it be maintained 2+ years?
                     │           │
                    YES          NO ───► [Choose MVC]
                     │
                     ▼
       Need database independence & fast testing?
                     │
                    YES ───────────────► [Choose DDD / Onion]
```

---

## 12. 🚀 How to Run Both Projects

### 🚀 Terminal 1: Run DDD Backend (Port 8000)
```powershell
cd backend\DDD
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

# Choose firestore, mongodb, or postgresql
$env:DATABASE = "mongodb"
python -m uvicorn main:app --reload --port 8000

# Swagger Documentation: http://127.0.0.1:8000/docs
```

### 🚀 Terminal 2: Run MVC Backend (Port 8001)
```powershell
cd backend\MVC
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

# Run MVC server
python main_mvc.py

# Swagger Documentation: http://127.0.0.1:8001/docs
```

---
<div align="center">
  <b>Built for Software Engineering Mastery</b><br>
  <i>Designed & Documented with Precision for Cloudpacer Internship</i>
</div>
