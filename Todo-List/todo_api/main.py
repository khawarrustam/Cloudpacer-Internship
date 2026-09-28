import os
from fastapi import FastAPI
import firebase_admin
from firebase_admin import credentials, firestore

# Domain Repositories
from src.domain.repositories import ITodoRepository
from src.infrastructure.repositories.in_memory_todo_repo import InMemoryTodoRepository
from src.infrastructure.repositories.firestore_todo_repo import FirestoreTodoRepository

# Use Cases
from src.application.use_cases.create_todo import CreateTodoUseCase
from src.application.use_cases.complete_todo import CompleteTodoUseCase
from src.application.use_cases.list_todos import ListTodosUseCase

# Presentation
from src.presentation.api.todo_router import (
    router as todo_router,
    get_create_use_case,
    get_complete_use_case,
    get_list_use_case
)

app = FastAPI(
    title="Todo Onion Architecture API",
    description="Domain-Driven Design + Onion Architecture with FastAPI & Firebase/In-Memory"
)

# -------------------------------------------------------------
# Dependency Injection / Wiring
# -------------------------------------------------------------
USE_FIREBASE = os.getenv("USE_FIREBASE", "false").lower() == "true"

if USE_FIREBASE:
    # Firebase Setup (Provide serviceAccountKey.json path or default app credentials)
    cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "serviceAccountKey.json")
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

# Instantiate Use Cases
create_use_case = CreateTodoUseCase(todo_repo=todo_repo)
complete_use_case = CompleteTodoUseCase(todo_repo=todo_repo)
list_use_case = ListTodosUseCase(todo_repo=todo_repo)

# Wire dependencies into FastAPI router
app.dependency_overrides[get_create_use_case] = lambda: create_use_case
app.dependency_overrides[get_complete_use_case] = lambda: complete_use_case
app.dependency_overrides[get_list_use_case] = lambda: list_use_case

# Include Router
app.include_router(todo_router)

@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "architecture": "Onion / DDD"}