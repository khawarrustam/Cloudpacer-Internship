"""Todo application use cases."""

from datetime import datetime

from app.application.dto import CreateTodoInput, TodoActionInput, TodoOutput
from app.domain.todo import TodoItem, TodoNotFoundError, TodoRepository
from app.logging import log_step


def to_output(todo: TodoItem) -> TodoOutput:
    """Convert a domain TodoItem into API-friendly application data."""
    # Domain datetime/enum rich types hain; output DTO JSON-friendly strings rakhta hai.
    completed_at = None
    if todo.completed_at:
        completed_at = todo.completed_at.isoformat()

    return TodoOutput(
        id=todo.id,
        title=todo.title.value,
        priority=todo.priority.value,
        is_completed=todo.is_completed,
        created_at=todo.created_at.isoformat(),
        completed_at=completed_at,
        owner_uid=todo.owner_uid,
        due_at=_optional_iso(todo.reminder.due_at),
        reminder_at=_optional_iso(todo.reminder.reminder_at),
        reminder_sent_at=_optional_iso(todo.reminder.sent_at),
        reminder_option=todo.reminder.option.value,
    )


def _optional_iso(value: datetime | None) -> str | None:
    """Return an ISO datetime string while keeping missing values as None."""
    return value.isoformat() if value else None


class TodoService:
    """What: Coordinate create, list, complete, and delete workflows.

    When: Todo HTTP routes request an application use case.
    How: Apply domain behavior and persist through TodoRepository.
    """

    def __init__(self, repository: TodoRepository) -> None:
        self.repository = repository

    def create(self, data: CreateTodoInput) -> TodoOutput:
        """Validate a new todo through the domain, save it, and return it."""
        # Domain entity rule apply karti hai; repository sirf resulting state save karti hai.
        todo = TodoItem.create(
            title=data.title,
            priority=data.priority,
            owner_uid=data.owner_uid,
            owner_email=data.owner_email,
            due_at=data.due_at,
            reminder_option=data.reminder_option,
            custom_reminder_at=data.custom_reminder_at,
        )
        self.repository.save(todo)
        log_step(
            "Application",
            f"Todo {todo.id} created and saved.",
            f"Todo {todo.id} create karke save kar diya.",
        )
        return to_output(todo)

    def list(self, owner_uid: str) -> list[TodoOutput]:
        """Return only todos owned by the authenticated database user."""
        todos = self.repository.get_by_owner(owner_uid)
        log_step(
            "Application",
            f"Found {len(todos)} todo(s).",
            f"{len(todos)} todo milay.",
        )
        return [to_output(todo) for todo in todos]

    def complete(self, data: TodoActionInput) -> TodoOutput:
        """Find an owned todo, apply completion, and save it."""
        # Pehle ID + owner se entity read hoti hai, phir entity apna rule apply karti hai.
        todo = self._get_todo_or_fail(data)
        todo.complete()
        self.repository.save(todo)
        log_step(
            "Application",
            "Todo completed and saved.",
            "Todo complete karke save kar diya.",
        )
        return to_output(todo)

    def delete(self, data: TodoActionInput) -> None:
        """Verify todo ownership before deleting it."""
        self._get_todo_or_fail(data)
        self.repository.delete(data.todo_id, data.owner_uid)
        log_step("Application", "Todo deleted.", "Todo delete ho gaya.")

    def _get_todo_or_fail(self, data: TodoActionInput) -> TodoItem:
        """Keep the shared complete/delete ownership check in one place."""
        # Same helper missing aur doosre user ke todo dono ko safe 404 behavior deta hai.
        todo = self.repository.get_by_id(data.todo_id, data.owner_uid)
        if todo is None:
            raise TodoNotFoundError("Todo was not found for this user.")
        return todo
