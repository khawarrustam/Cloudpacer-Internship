# 🧅 Todo API — DDD + Onion Architecture

> **A clean, production-ready Todo REST API** built with FastAPI, following Domain-Driven Design (DDD) and Onion Architecture patterns. Supports both **Firebase Firestore** and **In-Memory** storage.

**Author:** RanaKhawarAli

---

## 📖 Table of Contents

- [What is DDD?](#-what-is-ddd-domain-driven-design)
- [What is Onion Architecture?](#-what-is-onion-architecture)
- [How This Project Follows DDD + Onion](#-how-this-project-follows-ddd--onion)
- [Project Structure](#-project-structure)
- [How Everything Connects](#-how-everything-connects-the-full-flow)
- [Layer-by-Layer Breakdown](#-layer-by-layer-breakdown)
- [How to Run](#-how-to-run)
- [API Endpoints](#-api-endpoints)
- [Testing with Postman](#-testing-with-postman)
- [Key DDD Concepts Used](#-key-ddd-concepts-used)

---

## 🧠 What is DDD (Domain-Driven Design)?

**DDD** means you design your code around the **business problem**, not the technology.

Think of it this way:

> ❌ **Without DDD:** "I have a database table called `todos`, let me write CRUD operations."
>
> ✅ **With DDD:** "In my business, a **Todo** has rules — it needs a title (min 3 chars), a priority (LOW/MEDIUM/HIGH), and once completed, it can't be completed again. Let me write code that **enforces these rules** first, and connect the database later."

**Key idea:** Your business rules live in one place (the **Domain layer**), and they don't care whether you use Firebase, PostgreSQL, MongoDB, or even a text file.

---

## 🧅 What is Onion Architecture?

Onion Architecture organizes your code in **layers**, like the layers of an onion:

```
                    ┌──────────────────────────────────┐
                    │       Presentation Layer          │  ← API / Routes (FastAPI Router)
                    │   (what the outside world sees)   │
                    ├──────────────────────────────────┤
                    │       Application Layer           │  ← Use Cases (business workflows)
                    │   (orchestrates the actions)      │
                    ├──────────────────────────────────┤
                    │         Domain Layer              │  ← Entities, Value Objects, Rules
                    │   (the HEART of your app)         │     (pure business logic)
                    ├──────────────────────────────────┤
                    │      Infrastructure Layer         │  ← Database, Firebase, External APIs
                    │   (technical details / adapters)  │
                    └──────────────────────────────────┘
```

### The Golden Rule

> **Inner layers NEVER depend on outer layers.**

- `Domain` knows nothing about `Application`, `Presentation`, or `Infrastructure`
- `Application` knows about `Domain`, but NOT about `Presentation` or `Infrastructure`
- `Infrastructure` **implements** interfaces defined by `Domain`

This means you can **swap Firebase for PostgreSQL** without touching a single line of business logic!

---

## 🔗 How This Project Follows DDD + Onion

Here's the mapping from theory to actual code:

| DDD / Onion Concept | Our Code | File |
|---|---|---|
| **Entity (Aggregate Root)** | `TodoItem` class | `src/domain/entities.py` |
| **Value Object** | `TaskTitle`, `Priority` | `src/domain/value_objects.py` |
| **Domain Exception** | `DomainError`, `TaskAlreadyCompletedError` | `src/domain/exceptions.py` |
| **Repository Interface (Port)** | `ITodoRepository` (abstract class) | `src/domain/repositories.py` |
| **Use Case (Application Service)** | `CreateTodoUseCase`, `CompleteTodoUseCase`, `ListTodosUseCase` | `src/application/use_cases/` |
| **DTOs (Data Transfer Objects)** | `CreateTodoCommand`, `TodoDTO` | `src/application/dtos.py` |
| **Repository Implementation (Adapter)** | `FirestoreTodoRepository`, `InMemoryTodoRepository` | `src/infrastructure/repositories/` |
| **API / Presentation** | FastAPI Router, Pydantic Schemas | `src/presentation/api/` |
| **Dependency Injection (Wiring)** | `main.py` | `main.py` |

---

## 📁 Project Structure

```
todo_api/
├── main.py                          # 🔌 Entry point — wires everything together
├── requirements.txt                 # 📦 Python dependencies
├── serviceAccountKey.json           # 🔑 Firebase credentials (gitignored)
├── Todo_API.postman_collection.json # 📬 Postman collection for testing
│
└── src/
    ├── domain/                      # 🧅 LAYER 1: Core Business Logic (innermost)
    │   ├── entities.py              #     TodoItem — the main business object
    │   ├── value_objects.py         #     TaskTitle, Priority — validated types
    │   ├── exceptions.py            #     Business rule violations
    │   └── repositories.py          #     ITodoRepository — abstract interface
    │
    ├── application/                 # 🧅 LAYER 2: Use Cases (orchestration)
    │   ├── dtos.py                  #     Commands & DTOs — data going in/out
    │   └── use_cases/
    │       ├── create_todo.py       #     CreateTodoUseCase
    │       ├── complete_todo.py     #     CompleteTodoUseCase
    │       └── list_todos.py        #     ListTodosUseCase
    │
    ├── infrastructure/              # 🧅 LAYER 3: Technical Details (outermost)
    │   └── repositories/
    │       ├── in_memory_todo_repo.py    # InMemoryTodoRepository (for testing)
    │       └── firestore_todo_repo.py    # FirestoreTodoRepository (production)
    │
    └── presentation/                # 🧅 LAYER 3: API / Routes (outermost)
        └── api/
            ├── schemas.py           #     Pydantic request/response models
            └── todo_router.py       #     FastAPI endpoints
```

---

## ⚡ How Everything Connects (The Full Flow)

Let's trace what happens when you call **`POST /todos`** to create a new todo:

```
  Client (Postman/Browser)
       │
       ▼
  ┌─────────────────────────────────────────────────────┐
  │ 1. PRESENTATION — todo_router.py                     │
  │    • Receives HTTP POST request                      │
  │    • Validates JSON body with Pydantic (schemas.py)  │
  │    • Creates a CreateTodoCommand (DTO)               │
  │    • Calls use_case.execute(command)                 │
  └──────────────────────┬──────────────────────────────┘
                         │
                         ▼
  ┌─────────────────────────────────────────────────────┐
  │ 2. APPLICATION — create_todo.py (Use Case)           │
  │    • Receives the command                            │
  │    • Calls TodoItem.create() (Domain factory)        │
  │    • Calls todo_repo.save(todo)                      │
  │    • Converts entity → TodoDTO and returns it        │
  └──────────────────────┬──────────────────────────────┘
                         │
            ┌────────────┴────────────┐
            ▼                         ▼
  ┌──────────────────┐    ┌──────────────────────────┐
  │ 3a. DOMAIN        │    │ 3b. INFRASTRUCTURE       │
  │  TodoItem.create()│    │  FirestoreTodoRepository │
  │  • Validates title│    │  • .save() → Firestore   │
  │  • Sets UUID      │    │  • .get_by_id()          │
  │  • Sets priority  │    │  • .get_all()            │
  │  • Sets timestamp │    │                          │
  └──────────────────┘    └──────────────────────────┘
```

### Step-by-Step (Simple English):

1. **You send a request** → `POST /todos` with `{"title": "Learn DDD", "priority": "HIGH"}`

2. **Router receives it** (`todo_router.py`) → Pydantic validates the JSON, creates a `CreateTodoCommand`

3. **Use Case runs** (`create_todo.py`) → Calls `TodoItem.create("Learn DDD", Priority.HIGH)`

4. **Domain validates** (`entities.py` + `value_objects.py`):
   - `TaskTitle("Learn DDD")` → ✅ valid (3-120 chars)
   - `Priority.HIGH` → ✅ valid enum value
   - Generates UUID, sets `created_at` timestamp

5. **Repository saves** (`firestore_todo_repo.py`) → Converts entity to dict, saves to Firestore

6. **Response returns** → Use case converts entity to `TodoDTO`, router sends JSON back to client

---

## 🔍 Layer-by-Layer Breakdown

### Layer 1: Domain (The Heart ❤️)

This is the **most important layer**. It contains your business rules and knows NOTHING about databases, APIs, or frameworks.

#### `entities.py` — TodoItem (Aggregate Root)

```python
@dataclass
class TodoItem:
    id: str
    title: TaskTitle          # Not just a string — a validated Value Object!
    priority: Priority        # Not just a string — a validated Enum!
    is_completed: bool
    created_at: datetime
    completed_at: datetime | None

    @classmethod
    def create(cls, title, priority):
        # Factory method — creates a valid todo with UUID + timestamp
        ...

    def mark_as_completed(self):
        # Business Rule: Can't complete a todo that's already completed!
        if self.is_completed:
            raise TaskAlreadyCompletedError(...)
        self.is_completed = True
```

**Why is this important?** The business rule "a completed task cannot be completed again" lives HERE, not in the database or API layer. No matter who calls this code, the rule is always enforced.

#### `value_objects.py` — TaskTitle & Priority

```python
@dataclass(frozen=True)       # frozen = immutable (can't change after creation)
class TaskTitle:
    value: str

    def __post_init__(self):
        if len(self.value) < 3:     # Business rule: min 3 chars
            raise InvalidTaskTitleError(...)
        if len(self.value) > 120:   # Business rule: max 120 chars
            raise InvalidTaskTitleError(...)

class Priority(str, Enum):    # Only 3 valid values
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
```

**Why Value Objects?** A plain `str` can be anything — `""`, `"x"`, even 10,000 chars. A `TaskTitle` is ALWAYS valid. If it exists, it's guaranteed to be 3-120 characters.

#### `repositories.py` — ITodoRepository (Port/Interface)

```python
class ITodoRepository(ABC):           # ABC = Abstract Base Class
    @abstractmethod
    def save(self, todo: TodoItem) -> None: ...

    @abstractmethod
    def get_by_id(self, todo_id: str) -> Optional[TodoItem]: ...

    @abstractmethod
    def get_all(self) -> List[TodoItem]: ...
```

**Why an interface?** The domain says "I need a repository that can save, get_by_id, and get_all." It does NOT say "I need Firebase" or "I need PostgreSQL." This is the **Dependency Inversion Principle** — the domain defines the contract, infrastructure implements it.

---

### Layer 2: Application (The Orchestrator 🎯)

Use cases coordinate the workflow. They don't contain business logic — they just call domain methods in the right order.

#### `create_todo.py` — CreateTodoUseCase

```python
class CreateTodoUseCase:
    def __init__(self, todo_repo: ITodoRepository):   # Receives repo via DI
        self.todo_repo = todo_repo

    def execute(self, cmd: CreateTodoCommand) -> TodoDTO:
        todo = TodoItem.create(title=cmd.title, priority=Priority(cmd.priority))
        self.todo_repo.save(todo)     # Save via interface (doesn't know if it's Firebase or Memory)
        return TodoDTO(...)           # Convert to DTO for the outside world
```

**Notice:** The use case depends on `ITodoRepository` (interface), NOT on `FirestoreTodoRepository` (implementation). This is the magic of Onion Architecture!

---

### Layer 3: Infrastructure (The Adapter 🔧)

This layer provides **concrete implementations** of the interfaces defined by the domain.

#### Two implementations — same interface:

| Implementation | Use Case | Storage |
|---|---|---|
| `InMemoryTodoRepository` | Local dev / testing | Python dictionary |
| `FirestoreTodoRepository` | Production | Google Cloud Firestore |

Both implement `ITodoRepository`. The rest of the app doesn't know which one is being used!

---

### Layer 3: Presentation (The Gateway 🌐)

FastAPI router that receives HTTP requests and converts them to use case calls.

```python
@router.post("", status_code=201)
def create_todo(req: CreateTodoRequest, use_case = Depends(get_create_use_case)):
    cmd = CreateTodoCommand(title=req.title, priority=req.priority)
    return use_case.execute(cmd)   # Delegates to application layer
```

---

### Wiring It All Together: `main.py`

`main.py` is the **Composition Root** — where all dependencies are created and connected:

```python
# 1. Choose repository based on environment
if USE_FIREBASE:
    todo_repo = FirestoreTodoRepository(db=firestore.client())
else:
    todo_repo = InMemoryTodoRepository()

# 2. Create use cases with the chosen repository
create_use_case = CreateTodoUseCase(todo_repo=todo_repo)
complete_use_case = CompleteTodoUseCase(todo_repo=todo_repo)
list_use_case = ListTodosUseCase(todo_repo=todo_repo)

# 3. Inject into FastAPI router
app.dependency_overrides[get_create_use_case] = lambda: create_use_case
```

**This is Dependency Injection (DI)** — the use cases don't create their own repositories. Instead, `main.py` decides which implementation to use and "injects" it.

---

## 🚀 How to Run

### Prerequisites

- Python 3.11+
- pip

### 1. Clone & Setup

```bash
cd Todo-List/todo_api

# Create virtual environment
python3 -m venv venv
source venv/bin/activate     # Mac/Linux
# venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Run WITHOUT Firebase (In-Memory)

No credentials needed — data lives in memory (resets on restart):

```bash
source venv/bin/activate
python main.py
```

### 3. Run WITH Firebase (Firestore)

1. Place your `serviceAccountKey.json` in the `todo_api/` folder
2. Run:

```bash
source venv/bin/activate
USE_FIREBASE=true python main.py
```

### 4. Access the API

| URL | Description |
|---|---|
| `http://127.0.0.1:8000` | Health check |
| `http://127.0.0.1:8000/docs` | 📚 Swagger UI (interactive API docs) |
| `http://127.0.0.1:8000/redoc` | 📖 ReDoc (alternative docs) |

---

## 📡 API Endpoints

| Method | Endpoint | Description | Request Body |
|---|---|---|---|
| `GET` | `/` | Health check | — |
| `POST` | `/todos` | Create a new todo | `{"title": "...", "priority": "HIGH"}` |
| `GET` | `/todos` | List all todos | — |
| `PATCH` | `/todos/{id}/complete` | Mark a todo as complete | — |

### Example: Create a Todo

```bash
curl -X POST http://127.0.0.1:8000/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn Onion Architecture", "priority": "HIGH"}'
```

**Response (201 Created):**

```json
{
  "id": "a1b2c3d4-...",
  "title": "Learn Onion Architecture",
  "priority": "HIGH",
  "is_completed": false,
  "created_at": "2026-09-28T15:30:00+00:00",
  "completed_at": null
}
```

### Error Responses

| Scenario | Status Code | Example |
|---|---|---|
| Title too short (< 3 chars) | `422` | `{"title": "AB"}` |
| Missing title | `422` | `{"priority": "HIGH"}` |
| Todo not found | `404` | `PATCH /todos/wrong-id/complete` |
| Already completed | `400` | Completing the same todo twice |

---

## 📬 Testing with Postman

1. Import `Todo_API.postman_collection.json` into Postman
2. Run requests in this order:
   - **Create Todo** → automatically saves the `todo_id`
   - **List Todos** → verify it was created
   - **Complete Todo** → uses the saved `todo_id`
   - **Error Cases** → test validation and business rules

---

## 📚 Key DDD Concepts Used

| Concept | What It Means | Where In Our Code |
|---|---|---|
| **Entity** | An object with a unique ID that has a lifecycle | `TodoItem` (has `id`, can change state) |
| **Value Object** | An immutable object defined by its value, not ID | `TaskTitle`, `Priority` (no ID, just validated data) |
| **Aggregate Root** | The main entity that enforces all business rules | `TodoItem` (owns `mark_as_completed()` rule) |
| **Repository** | Abstraction for data storage | `ITodoRepository` (interface) |
| **Use Case** | A single business action | `CreateTodoUseCase`, `CompleteTodoUseCase` |
| **DTO** | Data structure for crossing layer boundaries | `CreateTodoCommand`, `TodoDTO` |
| **Dependency Inversion** | High-level modules don't depend on low-level ones | Domain defines `ITodoRepository`, Infrastructure implements it |
| **Dependency Injection** | Dependencies are provided, not created internally | `main.py` injects repos into use cases |

---

## 🧪 Why This Architecture Matters

```
❌ Without Onion:
   Router → directly calls Firebase → business rules scattered everywhere

✅ With Onion:
   Router → Use Case → Domain Entity → Repository Interface → Firebase
   (each layer has ONE job, and can be tested/swapped independently)
```

### Real-World Benefits:

1. **Swap databases easily** — Switch from Firebase to PostgreSQL? Just write a new `PostgresTodoRepository` that implements `ITodoRepository`. Zero changes to business logic.

2. **Test without a database** — Use `InMemoryTodoRepository` in tests. No Firebase needed.

3. **Business rules in one place** — "Title must be 3-120 chars" is in `TaskTitle`, not scattered across API routes and database queries.

4. **Team-friendly** — Frontend, backend, and database teams can work independently because layers have clear boundaries.

---

## 📄 License

MIT License — feel free to use this as a learning reference!
