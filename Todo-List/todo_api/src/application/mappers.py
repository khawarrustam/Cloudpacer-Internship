"""Convert domain objects into safe application output objects."""

from src.application.dtos import TodoDTO
from src.domain.entities import TodoItem


def todo_to_dto(todo: TodoItem) -> TodoDTO:
    """Return plain todo data for the API layer."""
    return TodoDTO(
        id=todo.id,
        title=todo.title.value,
        priority=todo.priority.value,
        is_completed=todo.is_completed,
        created_at=todo.created_at.isoformat(),
        completed_at=todo.completed_at.isoformat() if todo.completed_at else None,
        owner_uid=todo.owner_uid,
    )
