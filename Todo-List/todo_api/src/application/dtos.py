"""
=============================================================================
APPLICATION LAYER — Data Transfer Objects (DTOs) & Commands
=============================================================================
DTOs (Data Transfer Objects) aur Commands plain data structures hotay hain
jinka maqsad mukhtalif layers ke darmiyan data transmit karna hota hai.

Kyun Zaroori Hain:
- Domain Entities ko direct presentation (HTTP) layer par expose nahi kiya jata
  taake domain model bahar ke framework (FastAPI) se azaad rahe.
- Commands user ki intent (khwahish) ko represent karti hain (jaise: Create Todo, Complete Todo).

Kahan Connected Hai:
- `CreateTodoCommand`: `src/presentation/api/todo_router.py` banata hai aur `CreateTodoUseCase` ko deta hai.
- `CompleteTodoCommand`: `src/presentation/api/todo_router.py` banata hai aur `CompleteTodoUseCase` ko deta hai.
- `TodoDTO`: Tamam use cases (`create_todo`, `complete_todo`, `list_todos`) result ke tor par return karte hain jo router Pydantic response mein convert karta hai.
=============================================================================
"""

# ---------------------------------------------------------------------------
# LIBRARIES / IMPORTS (Kyun aur kis liye import ki gayi hain):
# ---------------------------------------------------------------------------
# 'dataclass': Boilerplate code ke baghair lightweight aur immutable ('frozen=True') DTO classes bananey ke liye.
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# COMMANDS (Input DTOs - User ki Intent):
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class CreateTodoCommand:
    """
    Kyun banaya gaya:
    - Naya Todo create karne ke liye zaroori input data pack karne ke liye.
    - Fields:
      - title: Task ka title string.
      - priority: Task ki priority string.

    Kahan connected hai:
    - Router se `CreateTodoUseCase.execute(cmd)` mein pass hota hai.
    """
    title: str
    priority: str


@dataclass(frozen=True)
class CompleteTodoCommand:
    """
    Kyun banaya gaya:
    - Kisi specific task ko complete karne ke liye ID carry karne ke liye.
    - Fields:
      - todo_id: Target task ki unique ID.

    Kahan connected hai:
    - Router se `CompleteTodoUseCase.execute(cmd)` mein pass hota hai.
    """
    todo_id: str


# ---------------------------------------------------------------------------
# OUTPUT DTO (Presentation ko wapis bhejne ke liye):
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class TodoDTO:
    """
    Kyun banaya gaya:
    - Use case execution ke baad safe aur clean data presentation layer ko wapis karne ke liye.
    - Isme domain logic ya methods nahi hotay, sirf raw primitive values hoti hain.

    Fields:
    - id: Task ID string.
    - title: Plain title string.
    - priority: Plain priority string.
    - is_completed: Boolean status.
    - created_at: ISO-8601 formatted timestamp string.
    - completed_at: ISO-8601 formatted timestamp string ya None.

    Kahan connected hai:
    - Use cases return karte hain aur router ise `TodoResponse` schema mein map karta hai.
    """
    id: str
    title: str
    priority: str
    is_completed: bool
    created_at: str
    completed_at: str | None
