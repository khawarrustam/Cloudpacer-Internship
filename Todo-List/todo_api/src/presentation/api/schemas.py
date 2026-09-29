"""
=============================================================================
PRESENTATION LAYER — Pydantic Schemas (Clean Architecture / DDD)
=============================================================================
Presentation Layer bahar se aane wali HTTP requests aur bahar jaane wale
HTTP responses ka format define karti hai.

Kyun Zaroori Hain:
- Pydantic models FastAPI ko auto-validation, documentation (Swagger UI),
  aur JSON serialization ki sahulat faraham karte hain.
- Clean Architecture mein presentation schemas sirf HTTP boundary par rehte hain,
  domain ya application layer ke andar nahi jaate.

Kahan Connected Hai:
- `CreateTodoRequest` aur `TodoResponse`: `src/presentation/api/todo_router.py`
  ke routes mein type hints aur response models ke tor par use hotay hain.
=============================================================================
"""

# ---------------------------------------------------------------------------
# LIBRARIES / IMPORTS (Kyun aur kis liye import ki gayi hain):
# ---------------------------------------------------------------------------
# 'BaseModel': Pydantic ka core class jo JSON data ko parse aur validate karta hai.
# 'Field': Attributes par validation constraints (min length, max length, example) lagane ke liye.
from pydantic import BaseModel, Field

# 'Optional': Batane ke liye ke field string bhi ho sakti hai ya null/None bhi.
from typing import Optional


# ---------------------------------------------------------------------------
# HTTP REQUEST SCHEMAS:
# ---------------------------------------------------------------------------
class CreateTodoRequest(BaseModel):
    """
    Kyun banaya gaya:
    - POST /todos request body ko validate karne ke liye.

    Fields:
    - title: Kam az kam 3 aur zyada se zyada 120 characters ka hona chahiye.
    - priority: Default 'MEDIUM'.
    """
    title: str = Field(
        ..., min_length=3, max_length=120, example="Setup DDD Onion layers"
    )
    priority: str = Field(default="MEDIUM", example="HIGH")


# ---------------------------------------------------------------------------
# HTTP RESPONSE SCHEMAS:
# ---------------------------------------------------------------------------
class TodoResponse(BaseModel):
    """
    Kyun banaya gaya:
    - Client ko JSON response bhejte waqt data structure enforce karne ke liye.

    Fields:
    - id: Unique identifier string.
    - title: Task title.
    - priority: Priority string (LOW, MEDIUM, HIGH).
    - is_completed: True/False status.
    - created_at: Creation time string.
    - completed_at: Completion time string ya null.
    """
    id: str
    title: str
    priority: str
    is_completed: bool
    created_at: str
    completed_at: Optional[str] = None
