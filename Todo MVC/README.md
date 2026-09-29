# 🏗️ Todo MVC — Traditional MVC Architecture (with Firebase Firestore)

> The **exact same Todo List application** built with the **Model-View-Controller (MVC)** pattern using FastAPI + Firebase Firestore.  
> Compare this side-by-side with the DDD/Onion version in [`Todo-List/todo_api/`](file:///Users/apple/internship-practice/Todo-List/todo_api/).  
> 📖 **Comprehensive Master Architecture Guide:** [`../README.md`](file:///Users/apple/internship-practice/README.md)

**Author:** RanaKhawarAli

---

## 📁 Project Structure

```text
Todo MVC/
├── main_mvc.py                     # 🔌 Entry point (run MVC server on port 8001)
├── requirements.txt                # 📦 Dependencies (FastAPI + firebase-admin)
├── serviceAccountKey.json          # 🔑 Firebase Credentials
├── Todo_MVC_API.postman_collection.json # 📬 Postman collection for Port 8001
│
└── src_mvc/
    ├── models/                     # 📊 MODEL — Data schema + business validation helpers
    │   └── todo_model.py           #     create_todo_dict(), mark_completed(), validate_title()
    │
    ├── views/                      # 👁️ VIEW — Pydantic schemas (request/response)
    │   └── todo_views.py           #     CreateTodoRequest, TodoResponse
    │
    ├── controllers/                # 🎮 CONTROLLER — Route handlers + orchestration + DB
    │   └── todo_controller.py      #     POST, GET, PATCH, DELETE /todos
    │
    └── db/                         # 💾 DATABASE — Firebase Firestore connection
        └── firebase.py             #     connect_db(), disconnect_db(), get_db()
```

---

## 🚀 How to Run

### Prerequisites
- Python 3.11+
- `serviceAccountKey.json` present in this folder (or parent workspace).

### Setup & Run

```bash
cd "Todo MVC"

# Activate virtual environment
source venv/bin/activate

# Install dependencies (if not installed)
pip install -r requirements.txt

# Run the server (port 8001 to avoid conflict with DDD on 8000)
python main_mvc.py
```

Server will start on: `http://127.0.0.1:8001`

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check (`{"status": "ok", "architecture": "MVC"}`) |
| `POST` | `/todos` | Create a new todo |
| `GET` | `/todos` | List all todos |
| `GET` | `/todos/{id}` | Get a single todo |
| `PATCH` | `/todos/{id}/complete` | Mark todo as completed (enforces business rule) |
| `DELETE` | `/todos/{id}` | Delete a todo |

### Swagger Docs
- `http://127.0.0.1:8001/docs` — Interactive API docs
- `http://127.0.0.1:8001/redoc` — ReDoc

---

## 🔀 Side-by-Side: MVC vs DDD/Onion

### File-to-File Comparison

| Responsibility | MVC (This Project) | DDD/Onion (`Todo-List/todo_api/`) |
|---|---|---|
| **Data schema** | `src_mvc/models/todo_model.py` | `src/domain/entities.py` + `src/domain/value_objects.py` |
| **Business rules** | `src_mvc/models/todo_model.py` | `src/domain/entities.py` (method on entity) |
| **Exceptions** | `src_mvc/models/todo_model.py` | `src/domain/exceptions.py` |
| **Request/Response** | `src_mvc/views/todo_views.py` | `src/presentation/api/schemas.py` + `src/application/dtos.py` |
| **Route handlers** | `src_mvc/controllers/todo_controller.py` | `src/presentation/api/todo_router.py` |
| **Workflow orchestration** | `src_mvc/controllers/todo_controller.py` | `src/application/use_cases/*.py` (3 files) |
| **DB operations** | `src_mvc/db/firebase.py` + controller | `src/domain/repositories.py` (port) + `src/infrastructure/repositories/*.py` (adapter) |
| **Entry point** | `main_mvc.py` (simple lifespan wiring) | `main.py` (composition root + DI container wiring) |
| **Total files** | **6 files** | **14+ files** |

---

## 💡 Key Architectural Takeaway (Roman Urdu)

MVC architecture mein Controller sab kuch khud karta hai:
1. HTTP request receive karta hai (`todo_views.py`)
2. Model function call karta hai (`todo_model.py`)
3. Direct Firestore collection mein insert/read/update karta hai (`firebase.get_db()`)
4. Response View return karta hai.

**Fayda:** Boht fast aur kam files mein ban jata hai.  
**Nuqsan:** Controller "Fat" ho jata hai aur database ke sath tightly coupled hota hai.

Mukammal request/response flow aur SOLID principles breakdown ke liye parhein: [Architectural Master Guide (README.md)](file:///Users/apple/internship-practice/README.md).
