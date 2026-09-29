"""
=============================================================================
MODEL LAYER — Todo Data Model + Business Rules (MVC Pattern)
=============================================================================
MVC architecture mein "Model" ka kaam data ki shape define karna aur
saare business rules / validations ko sambhalna hota hai.

MVC vs Clean Architecture / DDD ka Farq:
- MVC mein data aur rules isi ek file mein plain Python dictionaries aur helper
  functions ke zariye manage hotay hain.
- Clean Architecture (DDD) mein yeh alag alag layers mein divide hota hai:
  (entities.py, value_objects.py, exceptions.py).

Kahan Connected Hai:
- Is file ke functions (`create_todo_dict`, `mark_completed`, `validate_title`)
  aur exceptions (`InvalidTitleError`, `TodoAlreadyCompletedError`, `TodoNotFoundError`)
  ko `src_mvc/controllers/todo_controller.py` import karke use karta hai.
=============================================================================
"""

# ---------------------------------------------------------------------------
# LIBRARIES / IMPORTS (Kyun aur kis liye import ki gayi hain):
# ---------------------------------------------------------------------------
# 'datetime, timezone': Todo kab create hua ('created_at') aur kab complete hua ('completed_at')
# us waqt ki current UTC date & time record karne ke liye.
from datetime import datetime, timezone

# 'Enum': Ek specific set of constant values define karne ke liye taake ghalat values pass na ho sakein.
from enum import Enum

# 'typing.Optional': Type hinting ke liye use hota hai, batane ke liye ke koi value String bhi ho sakti hai aur None bhi.
from typing import Optional

# 'uuid': Universally Unique Identifier generate karne ke liye, taake har Todo ko unique ID milay.
import uuid


# ---------------------------------------------------------------------------
# ENUMS / CONSTANTS (Qeemtein fix karne ke liye):
# ---------------------------------------------------------------------------
class Priority(str, Enum):
    """
    Kyun banaya gaya:
    - Todo ki priority ko sirf 3 makhsoos darjon (LOW, MEDIUM, HIGH) tak mehdood rakhne ke liye.
    - String inherit karne se JSON serialization aasan ho jati hai.
    """
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


# ---------------------------------------------------------------------------
# CUSTOM EXCEPTIONS (Khusoosi Errors):
# ---------------------------------------------------------------------------
class TodoNotFoundError(Exception):
    """
    Kyun banaya gaya:
    - Jab user aisi ID mangay jo database mein mojood na ho, toh yeh error raise hota hai.
    - Controller isay pakar kar 404 Not Found response deta hai.
    """
    pass


class TodoAlreadyCompletedError(Exception):
    """
    Kyun banaya gaya:
    - Business Rule: Agar task pehle se mukammal (completed) hai toh usay dubara complete nahi kiya ja sakta.
    - Controller isay pakar kar 400 Bad Request response deta hai.
    """
    pass


class InvalidTitleError(Exception):
    """
    Kyun banaya gaya:
    - Business Rule: Todo ka title agar bohot chota (< 3) ya bohot lamba (> 120) ho toh yeh error trigger hota hai.
    - Controller isay pakar kar 400 Bad Request response deta hai.
    """
    pass


# ---------------------------------------------------------------------------
# BUSINESS LOGIC & HELPER FUNCTIONS:
# ---------------------------------------------------------------------------
def validate_title(title: str) -> str:
    """
    Kyun use ho raha hai:
    - Title ki safai (trimming) aur length validation ke business rules check karne ke liye.

    Kaise kaam karta hai:
    1. Title ke aagay peechay ki faltu spaces (`strip()`) khatam karta hai.
    2. Agar length 3 se kam ho toh `InvalidTitleError` deta hai.
    3. Agar length 120 se zyada ho toh `InvalidTitleError` deta hai.
    4. Agar valid ho toh saaf title wapis karta hai.

    Kahan connected hai:
    - Isi file ke `create_todo_dict()` mein call hota hai aur controller mein validation ke liye.
    """
    clean = title.strip() if title else ""
    if len(clean) < 3:
        raise InvalidTitleError("Title must be at least 3 characters long.")
    if len(clean) > 120:
        raise InvalidTitleError("Title cannot exceed 120 characters.")
    return clean


def create_todo_dict(title: str, priority: str = "MEDIUM") -> dict:
    """
    Kyun use ho raha hai:
    - Naya Todo object (dictionary ki shakal mein) banane ka factory function hai.

    Kaise kaam karta hai:
    1. Title ko `validate_title()` ke zariye check aur clean karta hai.
    2. Priority ko validate karta hai Priority enum ke zariye.
    3. Ek plain Python dictionary return karta hai jisme:
       - 'id': Naya unique UUID string.
       - 'title': Validated title.
       - 'priority': Priority string value.
       - 'is_completed': Shuru mein False.
       - 'created_at': Current UTC time (ISO format string).
       - 'completed_at': Shuru mein None.

    Kahan connected hai:
    - `src_mvc/controllers/todo_controller.py` ke `create_todo()` route mein call hota hai.
    - Banney ke baad yeh dictionary Firestore DB mein save hone jati hai.
    """
    clean_title = validate_title(title)
    valid_priority = Priority(priority.upper())

    return {
        "id": str(uuid.uuid4()),
        "title": clean_title,
        "priority": valid_priority.value,
        "is_completed": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None,
    }


def mark_completed(todo: dict) -> dict:
    """
    Kyun use ho raha hai:
    - Todo ko mukammal (complete) karne ka business rule enforce karta hai.

    Kaise kaam karta hai:
    1. Check karta hai ke `todo["is_completed"]` pehle se True toh nahi.
    2. Agar pehle se True ho, toh `TodoAlreadyCompletedError` throw karta hai.
    3. Agar False ho, toh `is_completed` ko True karta hai aur `completed_at` mein current time stamp daal kar dictionary return karta hai.

    Kahan connected hai:
    - `src_mvc/controllers/todo_controller.py` ke `complete_todo()` route mein call hota hai.
    - Is function ke return ke baad controller updated data Firestore DB mein save karta hai.
    """
    if todo["is_completed"]:
        raise TodoAlreadyCompletedError(
            f"Todo with ID '{todo['id']}' is already completed."
        )
    todo["is_completed"] = True
    todo["completed_at"] = datetime.now(timezone.utc).isoformat()
    return todo
