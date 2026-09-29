from pydantic import BaseModel, Field


class CreateTodoRequest(BaseModel):
    title: str = Field(
        ..., min_length=3, max_length=120, example="Setup DDD Onion layers"
    )
    priority: str = Field(default="MEDIUM", example="HIGH")


class TodoResponse(BaseModel):
    id: str
    title: str
    priority: str
    is_completed: bool
    created_at: str
    completed_at: str | None
