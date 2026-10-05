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
from src.presentation.api.dependencies import get_current_user, CurrentUser
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
# ENDPOINTS / ROUTE HANDLERS (All routes require authentication):
# ---------------------------------------------------------------------------

@router.post("", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(
    req: CreateTodoRequest,
    user: CurrentUser = Depends(get_current_user),
    use_case: CreateTodoUseCase = Depends(get_create_use_case),
):
    print("\n" + "="*60)
    print("📥 [DDD] REQUEST RECEIVED — PRESENTATION LAYER")
    print("="*60)
    print(f"   📂 File    : src/presentation/api/todo_router.py")
    print(f"   🔧 Function: create_todo()")
    print(f"   🌐 Route   : POST /todos")
    print(f"   🔐 User    : {user.email} (uid={user.uid})")
    print(f"   📝 Title   : {req.title}")
    print(f"   🎯 Priority: {req.priority}")
    print("-"*60)
    print(f"   ➡️  STEP 1: Presentation → Application Layer")
    print(f"              Building CreateTodoCommand(title, priority, owner_uid)")

    try:
        cmd = CreateTodoCommand(title=req.title, priority=req.priority, owner_uid=user.uid)

        print(f"   ➡️  STEP 2: Calling CreateTodoUseCase.execute(cmd)")
        result = use_case.execute(cmd)

        print(f"   📤 STEP 3: Sending Response | Status: 201 Created")
        print("="*60 + "\n")
        return result

    except DomainError as err:
        print(f"   ❌ DomainError: {str(err)}")
        print("="*60 + "\n")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@router.patch("/{todo_id}/complete", response_model=TodoResponse)
def complete_todo(
    todo_id: str,
    user: CurrentUser = Depends(get_current_user),
    use_case: CompleteTodoUseCase = Depends(get_complete_use_case),
):
    print("\n" + "="*60)
    print("📥 [DDD] REQUEST RECEIVED — PRESENTATION LAYER")
    print("="*60)
    print(f"   📂 File    : src/presentation/api/todo_router.py")
    print(f"   🔧 Function: complete_todo()")
    print(f"   🌐 Route   : PATCH /todos/{todo_id}/complete")
    print(f"   🔐 User    : {user.email} (uid={user.uid})")
    print(f"   🆔 todo_id : {todo_id}")
    print("-"*60)

    try:
        cmd = CompleteTodoCommand(todo_id=todo_id)

        print(f"   ➡️  STEP 1: Calling CompleteTodoUseCase.execute(cmd)")
        result = use_case.execute(cmd)

        # Verify the todo belongs to this user
        if result.owner_uid and result.owner_uid != user.uid:
            print(f"   ❌ Forbidden! Todo owner={result.owner_uid} but user={user.uid}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only complete your own todos.",
            )

        print(f"   📤 Response | Status: 200 OK")
        print("="*60 + "\n")
        return result

    except TodoNotFoundError as err:
        print(f"   ❌ TodoNotFoundError: {str(err)}")
        print("="*60 + "\n")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))
    except DomainError as err:
        print(f"   ❌ DomainError: {str(err)}")
        print("="*60 + "\n")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@router.get("", response_model=List[TodoResponse])
def get_todos(
    user: CurrentUser = Depends(get_current_user),
    use_case: ListTodosUseCase = Depends(get_list_use_case),
):
    print("\n" + "="*60)
    print("📥 [DDD] REQUEST RECEIVED — PRESENTATION LAYER")
    print("="*60)
    print(f"   📂 File    : src/presentation/api/todo_router.py")
    print(f"   🔧 Function: get_todos()")
    print(f"   🌐 Route   : GET /todos")
    print(f"   🔐 User    : {user.email} (uid={user.uid})")
    print("-"*60)
    print(f"   ➡️  Fetching only this user's todos")

    results = use_case.execute(owner_uid=user.uid)

    print(f"   ✅ Returning {len(results)} todo(s) for user {user.email}")
    print("="*60 + "\n")

    return results
