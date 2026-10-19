"""
=============================================================================
MODEL LAYER — Todo Data Model + Business Rules (MVC Pattern)
=============================================================================
In the MVC architecture, the "Model" is responsible for defining the shape of the data
and handling all business rules/validations.

Difference between MVC and Clean Architecture / DDD:
- In MVC, data and rules are managed in this single file using plain Python dictionaries
  and helper functions.
- In Clean Architecture (DDD), this is divided into separate layers 
  (entities.py, value_objects.py, exceptions.py).

Where it's Connected:
- The functions in this file (`create_todo_dict`, `mark_completed`, `validate_title`)
  and exceptions (`InvalidTitleError`, `TodoAlreadyCompletedError`, `TodoNotFoundError`)
  are imported and used by `src_mvc/controllers/todo_controller.py`.
=============================================================================
"""

# ---------------------------------------------------------------------------
# LIBRARIES / IMPORTS (Why and for what they are imported):
# ---------------------------------------------------------------------------
# 'datetime, timezone': To record the current UTC date & time for when a Todo 
# is created ('created_at') and completed ('completed_at').
from datetime import datetime, timezone

# 'Enum': To define a specific set of constant values so invalid values cannot be passed.
from enum import Enum

# 'typing.Optional': Used for type hinting, indicating a value can be a String or None.
from typing import Optional

# 'uuid': To generate a Universally Unique Identifier, ensuring each Todo gets a unique ID.
import uuid


# ---------------------------------------------------------------------------
# ENUMS / CONSTANTS (To set fixed values):
# ---------------------------------------------------------------------------
class Priority(str, Enum):
    """
    Why it was created:
    - To restrict the Todo's priority to only 3 specific levels (LOW, MEDIUM, HIGH).
    - Inheriting from string makes JSON serialization easier.
    """
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


# ---------------------------------------------------------------------------
# CUSTOM EXCEPTIONS (Specific Errors):
# ---------------------------------------------------------------------------
class TodoNotFoundError(Exception):
    """
    Why it was created:
    - Triggered when a user requests an ID that does not exist in the database.
    - The controller catches this and returns a 404 Not Found response.
    """
    pass


class TodoAlreadyCompletedError(Exception):
    """
    Why it was created:
    - Business Rule: If a task is already completed, it cannot be completed again.
    - The controller catches this and returns a 400 Bad Request response.
    """
    pass


class InvalidTitleError(Exception):
    """
    Why it was created:
    - Business Rule: Triggered if a Todo's title is too short (< 3) or too long (> 120).
    - The controller catches this and returns a 400 Bad Request response.
    """
    pass


# ---------------------------------------------------------------------------
# BUSINESS LOGIC & HELPER FUNCTIONS:
# ---------------------------------------------------------------------------
def validate_title(title: str) -> str:
    """
    Why it's being used:
    - To check business rules for title cleanup (trimming) and length validation.

    How it works:
    1. Removes extra spaces from the beginning and end of the title (`strip()`).
    2. Raises `InvalidTitleError` if the length is less than 3.
    3. Raises `InvalidTitleError` if the length is more than 120.
    4. Returns the cleaned title if it's valid.

    Where it's connected:
    - Called in `create_todo_dict()` in this file and used for validation in the controller.
    """
    clean = title.strip() if title else ""
    if len(clean) < 3:
        raise InvalidTitleError("Title must be at least 3 characters long.")
    if len(clean) > 120:
        raise InvalidTitleError("Title cannot exceed 120 characters.")
    return clean


def create_todo_dict(title: str, priority: str = "MEDIUM") -> dict:
    """
    Why it's being used:
    - A factory function to create a new Todo object (in the form of a dictionary).

    How it works:
    1. Checks and cleans the title using `validate_title()`.
    2. Validates the priority using the Priority enum.
    3. Returns a plain Python dictionary containing:
       - 'id': A new unique UUID string.
       - 'title': The validated title.
       - 'priority': The priority string value.
       - 'is_completed': Initially False.
       - 'created_at': Current UTC time (ISO format string).
       - 'completed_at': Initially None.

    Where it's connected:
    - Called in the `create_todo()` route of `src_mvc/controllers/todo_controller.py`.
    - After creation, this dictionary is sent to be saved in the Firestore DB.
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
    Why it's being used:
    - Enforces the business rule for marking a Todo as complete.

    How it works:
    1. Checks if `todo["is_completed"]` is already True.
    2. If it is already True, raises `TodoAlreadyCompletedError`.
    3. If False, sets `is_completed` to True, adds the current timestamp to `completed_at`,
       and returns the dictionary.

    Where it's connected:
    - Called in the `complete_todo()` route of `src_mvc/controllers/todo_controller.py`.
    - After this function returns, the controller saves the updated data in the Firestore DB.
    """
    if todo["is_completed"]:
        raise TodoAlreadyCompletedError(
            f"Todo with ID '{todo['id']}' is already completed."
        )
    todo["is_completed"] = True
    todo["completed_at"] = datetime.now(timezone.utc).isoformat()
    return todo
