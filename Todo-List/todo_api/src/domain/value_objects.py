"""
=============================================================================
DOMAIN LAYER — Value Objects & Enums (Clean Architecture / DDD)
=============================================================================
Value Objects woh objects hotay hain jinki apni koi alag identity (ID) nahi hoti,
balki woh apni value se pehchanay jatay hain aur IMMUTABLE (na-qabil-e-tabdeeli) hotay hain.
Yeh apne andar validation rules khud enforce karte hain (Self-validating).

Kahan Connected Hai:
- `Priority` aur `TaskTitle`: `src/domain/entities.py` ke `TodoItem` aggregate mein use hotay hain.
- `Priority`: `src/application/use_cases/create_todo.py` mein command se priority set karne ke liye use hota hai.
- `TaskTitle`: `src/infrastructure/repositories/firestore_todo_repo.py` mein DB data ko domain entity mein convert karte waqt use hota hai.
=============================================================================
"""

# ---------------------------------------------------------------------------
# LIBRARIES / IMPORTS (Kyun aur kis liye import ki gayi hain):
# ---------------------------------------------------------------------------
# 'dataclass': Python ki utility jo classes ke boilerplate code (jaise __init__, __repr__, __eq__) ko auto-generate karti hai.
from dataclasses import dataclass

# 'Enum': Makhsoos fixed values ka group bananey ke liye taake ghalat string pass na ho sake.
from enum import Enum

# EXCEPTION IMPORT: Jab title validation rules par poora na utre toh error raise karne ke liye.
from src.domain.exceptions import InvalidTaskTitleError


# ---------------------------------------------------------------------------
# ENUMS:
# ---------------------------------------------------------------------------
class Priority(str, Enum):
    """
    Kyun banaya gaya:
    - Task ki priority ko sirf teen levels (LOW, MEDIUM, HIGH) tak mehdood rakhne ke liye.
    - String inherit karne se JSON serialization aur comparison aasan rehta hai.
    """
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


# ---------------------------------------------------------------------------
# VALUE OBJECTS:
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class TaskTitle:
    """
    Kyun banaya gaya:
    - Domain-Driven Design (DDD) mein plain string use karne ke bajaye 'TaskTitle'
      ek Value Object banaya gaya hai jo khud apni validation check karta hai.
    - 'frozen=True' ka matlab hai ke banne ke baad iski value change nahi ho sakti (Immutable).

    Kaise kaam karta hai:
    - '__post_init__': Jab bhi naya TaskTitle banaya jata hai, yeh method foran chalta hai:
      1. Spaces strip karta hai.
      2. Agar length 3 se kam ho toh `InvalidTaskTitleError` deta hai.
      3. Agar length 120 se zyada ho toh `InvalidTaskTitleError` deta hai.
      4. Object ke andar cleaned value set karta hai.

    Kahan connected hai:
    - `src/domain/entities.py` mein `TodoItem.title: TaskTitle` ke tor par.
    """
    value: str

    def __post_init__(self):
        clean = self.value.strip() if self.value else ""
        if len(clean) < 3:
            raise InvalidTaskTitleError("Title must be at least 3 characters long.")
        if len(clean) > 120:
            raise InvalidTaskTitleError("Title cannot exceed 120 characters.")
        object.__setattr__(self, "value", clean)
