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

# ---------------------------------------------------------------------------
# LIBRARIES / IMPORTS (Kyun aur kis liye import ki gayi hain):
# ---------------------------------------------------------------------------
# 'typing.List': Responses mein multiple items ki list represent karne ke liye.
from typing import List

# 'fastapi':
# - APIRouter: Endpoints ko group karne ke liye (/todos prefix ke sath).
# - HTTPException: HTTP error response (400, 404) return karne ke liye.
# - Depends: FastAPI ka Dependency Injection tool jo use cases ko dynamically provide karta hai.
# - status: Standard HTTP status codes (201, 400, 404).
from fastapi import APIRouter, HTTPException, Depends, status

# SCHEMAS: HTTP request validation aur response body structure.
from src.presentation.api.schemas import CreateTodoRequest, TodoResponse

# COMMANDS: Use cases ko input dene ke liye application DTOs.
from src.application.dtos import CreateTodoCommand, CompleteTodoCommand

# USE CASES: Business workflows jo execute honge.
from src.application.use_cases.create_todo import CreateTodoUseCase
from src.application.use_cases.complete_todo import CompleteTodoUseCase
from src.application.use_cases.list_todos import ListTodosUseCase

# DOMAIN EXCEPTIONS: Pakar kar HTTP status code mein badalne ke liye.
from src.domain.exceptions import DomainError, TodoNotFoundError


# Router instance with '/todos' prefix
router = APIRouter(prefix="/todos", tags=["Todos"])


# ---------------------------------------------------------------------------
# DEPENDENCY PLACEHOLDERS (FastAPI Dependency Injection):
# ---------------------------------------------------------------------------
# Yeh functions sirf placeholders hain. `main.py` inko `app.dependency_overrides`
# ke zariye actual configured use case instances se replace (override) karega.

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
    """
    Kyun use ho raha hai:
    - Naya Todo task create karne ke liye HTTP POST endpoint.

    Kaise kaam karta hai (Flow):
    1. Client se `req: CreateTodoRequest` receive hota hai.
    2. Data ko `CreateTodoCommand(title=req.title, priority=req.priority)` mein pack karta hai.
    3. Injected `use_case.execute(cmd)` call karta hai.
    4. Agar domain validation fail ho (`DomainError`), toh HTTP 400 Bad Request raise karta hai.
    5. Result wapis client ko 201 Created status ke sath chala jata hai.

    Data Flow:
    HTTP Request -> Router -> Command DTO -> CreateTodoUseCase -> Entity -> Repository -> Response
    """
    try:
        cmd = CreateTodoCommand(title=req.title, priority=req.priority)
        return use_case.execute(cmd)
    except DomainError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@router.patch("/{todo_id}/complete", response_model=TodoResponse)
def complete_todo(
    todo_id: str, use_case: CompleteTodoUseCase = Depends(get_complete_use_case)
):
    """
    Kyun use ho raha hai:
    - Kisi specific Todo ko complete mark karne ke liye HTTP PATCH endpoint.

    Kaise kaam karta hai (Flow):
    1. URL path se `todo_id` leta hai aur `CompleteTodoCommand(todo_id=todo_id)` banata hai.
    2. `use_case.execute(cmd)` ko call karta hai.
    3. Agar task na mile (`TodoNotFoundError`), toh HTTP 404 Not Found throw karta hai.
    4. Agar business rule tootay (`DomainError`, jaise already completed), toh HTTP 400 throw karta hai.
    5. Successfully updated DTO ko client ko return karta hai.

    Data Flow:
    HTTP Request -> Router -> Command DTO -> CompleteTodoUseCase -> Entity -> Repository -> Response
    """
    try:
        cmd = CompleteTodoCommand(todo_id=todo_id)
        return use_case.execute(cmd)
    except TodoNotFoundError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))
    except DomainError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@router.get("", response_model=List[TodoResponse])
def get_todos(use_case: ListTodosUseCase = Depends(get_list_use_case)):
    """
    Kyun use ho raha hai:
    - Tamam Todos ki list laane ke liye HTTP GET endpoint.

    Kaise kaam karta hai (Flow):
    1. Injected `use_case.execute()` ko call karta hai.
    2. Use Case repository se saare items fetch karke DTOs return karta hai.
    3. DTOs ki list ko `TodoResponse` models ki list ke roop mein client ko bhejta hai.

    Data Flow:
    HTTP Request -> Router -> ListTodosUseCase -> Repository -> DTOs List -> Client
    """
    return use_case.execute()
