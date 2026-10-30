"""Application layer: use cases called by the presentation layer."""

from src.application.dto import (
    AuthOutput,
    CreateTodoInput,
    LoginInput,
    SignupInput,
    TodoActionInput,
    TodoOutput,
)
from src.domain.models import TodoItem, TodoNotFoundError, TodoRepository
from src.logs import log_step


def to_output(todo: TodoItem) -> TodoOutput:
    """Convert a domain entity into plain application output."""
    return TodoOutput(
        id=todo.id,
        title=todo.title.value,
        priority=todo.priority.value,
        is_completed=todo.is_completed,
        created_at=todo.created_at.isoformat(),
        completed_at=(
            todo.completed_at.isoformat() if todo.completed_at else None
        ),
        owner_uid=todo.owner_uid,
    )


class TodoUseCases:
    """Create, list, complete, and delete todo use cases."""

    def __init__(self, repository: TodoRepository):
        self.repository = repository

    def create(self, data: CreateTodoInput) -> TodoOutput:
        todo = TodoItem.create(data.title, data.priority, data.owner_uid)
        self.repository.save(todo)
        log_step(
            "Application",
            f"Todo {todo.id} created and saved.",
            f"Todo {todo.id} create karke save kar diya.",
        )
        return to_output(todo)

    def list(self, owner_uid: str) -> list[TodoOutput]:
        todos = self.repository.get_by_owner(owner_uid)
        log_step(
            "Application",
            f"Found {len(todos)} todo(s).",
            f"{len(todos)} todo milay.",
        )
        return [to_output(todo) for todo in todos]

    def complete(self, data: TodoActionInput) -> TodoOutput:
        todo = self.repository.get_by_id(data.todo_id, data.owner_uid)
        if not todo:
            raise TodoNotFoundError("Todo was not found for this user.")
        todo.complete()
        self.repository.save(todo)
        log_step(
            "Application",
            "Todo completed and saved.",
            "Todo complete karke save kar diya.",
        )
        return to_output(todo)

    def delete(self, data: TodoActionInput) -> None:
        if not self.repository.get_by_id(data.todo_id, data.owner_uid):
            raise TodoNotFoundError("Todo was not found for this user.")
        self.repository.delete(data.todo_id, data.owner_uid)
        log_step("Application", "Todo deleted.", "Todo delete ho gaya.")


class AuthUseCases:
    """Signup and login use cases."""

    def __init__(self, repository):
        self.repository = repository

    def signup(self, data: SignupInput) -> AuthOutput:
        user = self.repository.signup(
            data.email,
            data.password,
            data.display_name,
        )
        log_step("Application", "Signup completed.", "Signup mukammal ho gaya.")
        return AuthOutput(user.uid, user.email, user.token)

    def login(self, data: LoginInput) -> AuthOutput:
        user = self.repository.login(data.email, data.password)
        log_step("Application", "Login completed.", "Login mukammal ho gaya.")
        return AuthOutput(user.uid, user.email, user.token)
