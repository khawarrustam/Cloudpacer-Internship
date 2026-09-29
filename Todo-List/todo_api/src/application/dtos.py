from dataclasses import dataclass


@dataclass(frozen=True)
class CreateTodoCommand:
    title: str
    priority: str


@dataclass(frozen=True)
class CompleteTodoCommand:
    todo_id: str


@dataclass(frozen=True)
class TodoDTO:
    id: str
    title: str
    priority: str
    is_completed: bool
    created_at: str
    completed_at: str | None
