"""
=============================================================================
PRESENTATION LAYER — FastAPI Todo Router (Clean Architecture / DDD)
=============================================================================
Yeh router Presentation Layer ka part hai jo HTTP requests aur Web framework (FastAPI)
ko handle karta hai.

Clean Architecture Rule:
- Router ke paas apna koi business logic nahi hota aur na hi yeh direct database
  se baat karta hai!
- Router ka kaam sirf yeh hai:
  1. HTTP Request pakarna.
  2. Request data se Command DTO banana.
  3. Muta'aliqa Use Case ko `Depends()` ke zariye inject karke uska `execute()` chalana.
  4. Agar Domain Errors aayein toh unko standard HTTP exceptions (400, 404) mein map karna.
  5. Result ko Response Schema ke zariye client ko return karna.

Kahan Connected Hai:
- `main.py`: Is router ko `app.include_router(todo_router)` se include karta hai
  aur `app.dependency_overrides` ke zariye use cases inject karta hai.
=============================================================================
"""

from typing import List
from fastapi import APIRouter, HTTPException, Depends, status

from src.presentation.api.schemas import CreateTodoRequest, TodoResponse
from src.application.dtos import CreateTodoCommand, CompleteTodoCommand
from src.application.use_cases.create_todo import CreateTodoUseCase
from src.application.use_cases.complete_todo import CompleteTodoUseCase
from src.application.use_cases.list_todos import ListTodosUseCase
from src.domain.exceptions import DomainError, TodoNotFoundError

router = APIRouter(prefix="/todos", tags=["Todos"])


# ---------------------------------------------------------------------------
# DEPENDENCY PLACEHOLDERS (FastAPI Dependency Injection):
# ---------------------------------------------------------------------------
def get_create_use_case() -> CreateTodoUseCase:
    """Dependency placeholder for CreateTodoUseCase."""
    raise NotImplementedError


def get_complete_use_case() -> CompleteTodoUseCase:
    """Dependency placeholder for CompleteTodoUseCase."""
    raise NotImplementedError


def get_list_use_case() -> ListTodosUseCase:
    """Dependency placeholder for ListTodosUseCase."""
    raise NotImplementedError


# ---------------------------------------------------------------------------
# ENDPOINTS / ROUTE HANDLERS:
# ---------------------------------------------------------------------------

@router.post("", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(
    req: CreateTodoRequest, use_case: CreateTodoUseCase = Depends(get_create_use_case)
):
    print("\n" + "="*60)
    print("📥 [DDD] REQUEST RECEIVED — PRESENTATION LAYER")
    print("="*60)
    print(f"   📂 File    : src/presentation/api/todo_router.py")
    print(f"   🔧 Function: create_todo()")
    print(f"   🌐 Route   : POST /todos")
    print(f"   📝 Title   : {req.title}")
    print(f"   🎯 Priority: {req.priority}")
    print("-"*60)
    print(f"   ➡️  STEP 1: Presentation → Application Layer")
    print(f"              Building CreateTodoCommand(title, priority)")
    print(f"              📂 File: src/application/dtos.py → CreateTodoCommand")

    try:
        cmd = CreateTodoCommand(title=req.title, priority=req.priority)

        print(f"   ➡️  STEP 2: Calling CreateTodoUseCase.execute(cmd)")
        print(f"              📂 File: src/application/use_cases/create_todo.py")

        result = use_case.execute(cmd)

        print("-"*60)
        print(f"   ✅ STEP 3: Use Case returned TodoDTO to Router")
        print(f"              ID       : {result.id}")
        print(f"              Title    : {result.title}")
        print(f"              Priority : {result.priority}")
        print(f"   ➡️  STEP 4: Building TodoResponse (Presentation Schema)")
        print(f"              📂 File: src/presentation/api/schemas.py → TodoResponse")
        print(f"   📤 STEP 5: Sending Response to Client | Status: 201 Created")
        print("="*60 + "\n")

        return result

    except DomainError as err:
        print(f"   ❌ DomainError caught in Router!")
        print(f"      📂 Raised by: src/domain/exceptions.py → DomainError")
        print(f"      Detail: {str(err)}")
        print("="*60 + "\n")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@router.patch("/{todo_id}/complete", response_model=TodoResponse)
def complete_todo(
    todo_id: str, use_case: CompleteTodoUseCase = Depends(get_complete_use_case)
):
    print("\n" + "="*60)
    print("📥 [DDD] REQUEST RECEIVED — PRESENTATION LAYER")
    print("="*60)
    print(f"   📂 File    : src/presentation/api/todo_router.py")
    print(f"   🔧 Function: complete_todo()")
    print(f"   🌐 Route   : PATCH /todos/{{todo_id}}/complete")
    print(f"   🆔 todo_id : {todo_id}")
    print("-"*60)
    print(f"   ➡️  STEP 1: Building CompleteTodoCommand(todo_id)")
    print(f"              📂 File: src/application/dtos.py → CompleteTodoCommand")

    try:
        cmd = CompleteTodoCommand(todo_id=todo_id)

        print(f"   ➡️  STEP 2: Calling CompleteTodoUseCase.execute(cmd)")
        print(f"              📂 File: src/application/use_cases/complete_todo.py")

        result = use_case.execute(cmd)

        print("-"*60)
        print(f"   ✅ STEP 3: Use Case returned updated TodoDTO to Router")
        print(f"              ID           : {result.id}")
        print(f"              is_completed : {result.is_completed}")
        print(f"              completed_at : {result.completed_at}")
        print(f"   ➡️  STEP 4: Building TodoResponse and sending to Client")
        print(f"   📤 STEP 5: Response | Status: 200 OK")
        print("="*60 + "\n")

        return result

    except TodoNotFoundError as err:
        print(f"   ❌ TodoNotFoundError caught in Router!")
        print(f"      📂 Raised by: src/domain/exceptions.py → TodoNotFoundError")
        print(f"      Detail: {str(err)}")
        print("="*60 + "\n")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))
    except DomainError as err:
        print(f"   ❌ DomainError caught in Router!")
        print(f"      📂 Raised by: src/domain/exceptions.py → DomainError")
        print(f"      Detail: {str(err)}")
        print("="*60 + "\n")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@router.get("", response_model=List[TodoResponse])
def get_todos(use_case: ListTodosUseCase = Depends(get_list_use_case)):
    print("\n" + "="*60)
    print("📥 [DDD] REQUEST RECEIVED — PRESENTATION LAYER")
    print("="*60)
    print(f"   📂 File    : src/presentation/api/todo_router.py")
    print(f"   🔧 Function: get_todos()")
    print(f"   🌐 Route   : GET /todos")
    print("-"*60)
    print(f"   ➡️  STEP 1: Calling ListTodosUseCase.execute()")
    print(f"              📂 File: src/application/use_cases/list_todos.py")

    results = use_case.execute()

    print(f"   ✅ STEP 2: Use Case returned {len(results)} TodoDTO(s)")
    for i, r in enumerate(results, 1):
        print(f"             [{i}] id={r.id[:8]}... | title={r.title} | completed={r.is_completed}")
    print(f"   📤 STEP 3: Sending Response | Status: 200 OK")
    print("="*60 + "\n")

    return results
