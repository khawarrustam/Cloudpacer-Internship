"""Request and response shapes for todo HTTP routes.

English: Pydantic checks JSON at the API boundary.
Roman Urdu: Pydantic API par anay wala JSON check karta hai.
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field


class CreateTodoRequest(BaseModel):
    title: str = Field(
        ...,
        min_length=3,
        max_length=120,
        examples=["Learn DDD basics"],
    )
    priority: Literal[
        "LOW",
        "MEDIUM",
        "HIGH",
        "low",
        "medium",
        "high",
    ] = Field(default="MEDIUM", examples=["HIGH"])


class TodoResponse(BaseModel):
    id: str
    title: str
    priority: str
    is_completed: bool
    created_at: str
    completed_at: Optional[str] = None
