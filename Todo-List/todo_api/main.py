"""
=============================================================================
COMPOSITION ROOT — Main Entry Point & Dependency Injection (Clean Architecture)
=============================================================================
Clean Architecture / Onion Architecture mein yeh file "Composition Root" kehlati hai.
Yani woh wahid jagah jahan system ki tamam layers aapas mein connect (wire) hoti hain:
1. Environment configuration check karna (Firebase use karna hai ya In-Memory).
2. Muta'aliqa Repository Adapter instantiate karna.
3. Use Cases banana aur unhe Repository inject karna.
4. FastAPI Router ke dependency placeholders ko actual use cases se override karna.
5. Application server start karna.

Chalanay Ka Tareeqa:
  uvicorn main:app --host 127.0.0.1 --port 8000 --reload

Kahan Connected Hai:
- Yeh file poore project ki saari layers (Domain, Infrastructure, Application, Presentation)
  ko aapas mein jorti hai.
=============================================================================
"""

# ---------------------------------------------------------------------------
# LIBRARIES / IMPORTS
# ---------------------------------------------------------------------------
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import firebase_admin
from firebase_admin import credentials, firestore

# DOMAIN LAYER IMPORT: Abstract Repository Interface (Port)
from src.domain.repositories import ITodoRepository

# INFRASTRUCTURE LAYER IMPORTS: Concrete Database Adapters
from src.infrastructure.repositories.in_memory_todo_repo import InMemoryTodoRepository
from src.infrastructure.repositories.firestore_todo_repo import FirestoreTodoRepository

# APPLICATION LAYER IMPORTS: Business Workflows (Use Cases)
from src.application.use_cases.create_todo import CreateTodoUseCase
from src.application.use_cases.complete_todo import CompleteTodoUseCase
from src.application.use_cases.list_todos import ListTodosUseCase

# PRESENTATION LAYER IMPORTS: HTTP Router aur Dependency Injection placeholders
from src.presentation.api.todo_router import (
    router as todo_router,
    get_create_use_case,
    get_complete_use_case,
    get_list_use_case,
)
from src.presentation.api.auth_router import router as auth_router


# ---------------------------------------------------------------------------
# FASTAPI APPLICATION SETUP:
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Todo Onion Architecture API",
    description="Domain-Driven Design + Onion Clean Architecture with FastAPI & Firebase/In-Memory",
)

# ---------------------------------------------------------------------------
# CORS MIDDLEWARE SETUP:
# ---------------------------------------------------------------------------
# CORS (Cross-Origin Resource Sharing) allow karna zaroori hai taake 
# frontend (port 5173) backend (port 8000) se baat kar sake.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development, we allow all origins. In production, replace with ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# DEPENDENCY INJECTION / WIRING (Layers ko aapas mein jorna):
# ---------------------------------------------------------------------------

# Step 1: Database Adapter ka intekhab
USE_FIREBASE = os.getenv("USE_FIREBASE", "false").lower() == "true"

if USE_FIREBASE:
    cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "serviceAccountKey.json")
    if not firebase_admin._apps:
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        else:
            firebase_admin.initialize_app()
    db = firestore.client()
    todo_repo: ITodoRepository = FirestoreTodoRepository(db=db)
    print("Database: Running with Firebase Firestore")
else:
    todo_repo: ITodoRepository = InMemoryTodoRepository()
    print("Database: Running with In-Memory Repository (No credentials needed)")


# Step 2: Use Cases ko Instantiate karna aur Repository Inject karna
create_use_case = CreateTodoUseCase(todo_repo=todo_repo)
complete_use_case = CompleteTodoUseCase(todo_repo=todo_repo)
list_use_case = ListTodosUseCase(todo_repo=todo_repo)


# Step 3: FastAPI Dependency Overrides
app.dependency_overrides[get_create_use_case] = lambda: create_use_case
app.dependency_overrides[get_complete_use_case] = lambda: complete_use_case
app.dependency_overrides[get_list_use_case] = lambda: list_use_case


# Step 4: Router ko Main App mein Shamil (Include) karna
app.include_router(todo_router)
app.include_router(auth_router)


# ---------------------------------------------------------------------------
# HEALTH CHECK ENDPOINT:
# ---------------------------------------------------------------------------
@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "architecture": "Onion / DDD"}


# ---------------------------------------------------------------------------
# DIRECT EXECUTION SERVER (Uvicorn):
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
