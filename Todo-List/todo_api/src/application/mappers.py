"""Convert domain objects into safe application output objects."""

from src.application.dtos import TodoDTO
from src.domain.entities import TodoItem
from src.shared.console import print_flow


def todo_to_dto(todo: TodoItem) -> TodoDTO:
    """Return plain todo data for the API layer."""
    print_flow(
        source="src/domain/entities.py -> TodoItem",
        destination="src/application/dtos.py -> TodoDTO",
        data=f"id={todo.id}, title={todo.title.value}",
        english="Changing the domain object into safe response data.",
        roman_urdu="Domain object ko safe response data mein badla ja raha hai.",
    )
    return TodoDTO(
        id=todo.id,
        title=todo.title.value,
        priority=todo.priority.value,
        is_completed=todo.is_completed,
        created_at=todo.created_at.isoformat(),
        completed_at=todo.completed_at.isoformat() if todo.completed_at else None,
        owner_uid=todo.owner_uid,
    )
