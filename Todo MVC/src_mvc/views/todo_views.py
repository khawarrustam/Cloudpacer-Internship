"""
=============================================================================
VIEW LAYER — Pydantic Schemas for Request & Response (MVC Pattern)
=============================================================================
In the MVC architecture, "View" refers to what the user/client will see.
Since this is a REST API (there are no HTML templates), Pydantic Models act as
our "Views" that define the structure of the Request body and Response JSON.

MVC vs Clean Architecture / DDD:
- In MVC, these same schemas handle both API validation and data transfer.
- In DDD, there are two distinct concepts: Presentation Schemas (for FastAPI) and
  Application DTOs (Data Transfer Objects that carry data between layers).

Where it's Connected:
- These classes are used in `src_mvc/controllers/todo_controller.py` for every route 
  as input (`req: CreateTodoRequest`) and output (`response_model=TodoResponse`).
=============================================================================
"""

# ---------------------------------------------------------------------------
# LIBRARIES / IMPORTS (Why and for what they are imported):
# ---------------------------------------------------------------------------
# 'BaseModel': Pydantic's base class that validates and serializes request and response data.
# 'Field': To apply additional constraints (like min_length, max_length, examples) on model fields.
from pydantic import BaseModel, Field

# 'Optional': To indicate that a field's value can be a string or None (null).
from typing import Optional


# ---------------------------------------------------------------------------
# REQUEST SCHEMAS (Data incoming from the client):
# ---------------------------------------------------------------------------
class CreateTodoRequest(BaseModel):
    """
    Why it was created:
    - To validate the incoming JSON body when a client makes a request to create 
      a new task via POST /todos.

    Fields and Rules:
    - title: Must be a String, with a minimum of 3 and a maximum of 120 characters.
    - priority: Optional string, defaults to 'MEDIUM'.

    Where it's connected:
    - As a parameter in `create_todo(req: CreateTodoRequest)` within 
      `src_mvc/controllers/todo_controller.py`.
    """
    title: str = Field(
        ..., min_length=3, max_length=120, examples=["Setup MVC Architecture"]
    )
    priority: str = Field(default="MEDIUM", examples=["HIGH"])


# ---------------------------------------------------------------------------
# RESPONSE SCHEMAS (Data sent back to the client):
# ---------------------------------------------------------------------------
class TodoResponse(BaseModel):
    """
    Why it was created:
    - To define a fixed JSON contract for the Todo data sent back to the client in the response.

    Fields:
    - id: The Todo's unique ID string.
    - title: The task's title.
    - priority: The task's priority (LOW, MEDIUM, HIGH).
    - is_completed: Boolean flag (True/False).
    - created_at: Timestamp of when the todo was created.
    - completed_at: Timestamp of when the todo was completed (null/None if not yet completed).

    Where it's connected:
    - As `response_model=TodoResponse` or `List[TodoResponse]` in 
      `src_mvc/controllers/todo_controller.py`.
    """
    id: str
    title: str
    priority: str
    is_completed: bool
    created_at: str
    completed_at: Optional[str] = None
