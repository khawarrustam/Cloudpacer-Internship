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
# LIBRARIES / IMPORTS (Kyun aur kis liye import ki gayi hain):
# ---------------------------------------------------------------------------
# 'os': Environment variables (jaise USE_FIREBASE, FIREBASE_CREDENTIALS_PATH) parhne
# aur file mojood hone ki tasdeeq karne ke liye.
import os

# 'FastAPI': Main web application framework jisme API run hogi.
from fastapi import FastAPI

# 'firebase_admin': Firebase SDK initialize karne ke liye.
# 'credentials, firestore': Service account key authenticate karne aur Firestore database client banane ke liye.
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
# DEPENDENCY INJECTION / WIRING (Layers ko aapas mein jorna):
# ---------------------------------------------------------------------------

# Step 1: Database Adapter ka intekhab (Configuration-based Switching)
# Agar environment variable USE_FIREBASE=true ho toh Firestore chalega, warna InMemory.
USE_FIREBASE = os.getenv("USE_FIREBASE", "false").lower() == "true"

if USE_FIREBASE:
    # Firebase Firestore Setup
    cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "serviceAccountKey.json")
    if not firebase_admin._apps:
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        else:
            firebase_admin.initialize_app()
    db = firestore.client()
    # Firestore Adapter ko ITodoRepository ke tor par initialize kiya
    todo_repo: ITodoRepository = FirestoreTodoRepository(db=db)
    print("Database: Running with Firebase Firestore")
else:
    # InMemory Adapter ko ITodoRepository ke tor par initialize kiya (No credentials required)
    todo_repo: ITodoRepository = InMemoryTodoRepository()
    print("Database: Running with In-Memory Repository (No credentials needed)")


# Step 2: Use Cases ko Instantiate karna aur Repository Inject karna
create_use_case = CreateTodoUseCase(todo_repo=todo_repo)
complete_use_case = CompleteTodoUseCase(todo_repo=todo_repo)
list_use_case = ListTodosUseCase(todo_repo=todo_repo)


# Step 3: FastAPI Dependency Overrides (Router ke sath Use Cases connect karna)
# Router ke placeholders ko actual banaye gaye use case objects se replace kiya jata hai.
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
    """
    Kyun use ho raha hai:
    - API ki health aur architecture type confirm karne ke liye.
    """
    return {"status": "ok", "architecture": "Onion / DDD"}


# ---------------------------------------------------------------------------
# DIRECT EXECUTION SERVER (Uvicorn):
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # 'uvicorn': ASGI server jo app ko port 8000 par live host karta hai.
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)