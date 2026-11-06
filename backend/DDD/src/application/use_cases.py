"""Application layer: use cases called by the presentation layer."""

from src.application.dto import (
    AuthOutput,
    CreateTodoInput,
    LoginInput,
    SignupInput,
    TodoActionInput,
    TodoOutput,
)
from src.domain.models import (
    AuthRepository,
    TodoItem,
    TodoNotFoundError,
    TodoRepository,
)
from src.logs import log_step


def to_output(todo: TodoItem) -> TodoOutput:
    """Convert a domain TodoItem into API-friendly application data.

    Kyun: Domain objects ko directly presentation layer mein expose nahi karna;
    datetime aur Enum values ko simple strings mein convert karna hota hai.
    """
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
    )


class TodoUseCases:
    """Coordinate create, list, complete, and delete todo workflows."""

    def __init__(self, repository: TodoRepository):
        """Receive the selected database through dependency injection.

        Kyun: Use case ka code database switch hone par change na ho.
        """
        self.repository = repository

    def create(self, data: CreateTodoInput) -> TodoOutput:
        """Validate a new todo through the domain, then save and return it."""
        todo = TodoItem.create(data.title, data.priority, data.owner_uid)
        self.repository.save(todo)
        log_step(
            "Application",
            f"Todo {todo.id} created and saved.",
            f"Todo {todo.id} create karke save kar diya.",
        )
        return to_output(todo)

    def _get_todo_or_fail(self, data: TodoActionInput) -> TodoItem:
        """Return the user's todo or raise the shared not-found error.

        Kyun: Complete aur delete dono ko same ownership check chahiye. Is
        helper se woh rule aik jagah readable form mein rehta hai.
        """
        todo = self.repository.get_by_id(data.todo_id, data.owner_uid)
        if todo is None:
            raise TodoNotFoundError("Todo was not found for this user.")
        return todo

    def list(self, owner_uid: str) -> list[TodoOutput]:
        """Return only the todos owned by the logged-in Firebase user."""
        todos = self.repository.get_by_owner(owner_uid)
        log_step(
            "Application",
            f"Found {len(todos)} todo(s).",
            f"{len(todos)} todo milay.",
        )
        return [to_output(todo) for todo in todos]

    def complete(self, data: TodoActionInput) -> TodoOutput:
        """Find the user's todo, apply its completion rule, and save it.

        Kyun: Ownership check aur domain rule database update se pehle hon.
        """
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
        """Verify ownership/existence before deleting a todo."""
        self._get_todo_or_fail(data)
        self.repository.delete(data.todo_id, data.owner_uid)
        log_step("Application", "Todo deleted.", "Todo delete ho gaya.")


class AuthUseCases:
    """Coordinate signup and login without knowing Firebase details."""

    def __init__(self, repository: AuthRepository):
        """Receive an authentication repository from the startup wiring."""
        self.repository = repository

    def signup(self, data: SignupInput) -> AuthOutput:
        """Create a user, log them in, and return safe auth output."""
        user = self.repository.signup(
            data.email,
            data.password,
            data.display_name,
        )
        log_step("Application", "Signup completed.", "Signup mukammal ho gaya.")
        return AuthOutput(
            uid=user.uid,
            email=user.email,
            token=user.token,
        )

    def login(self, data: LoginInput) -> AuthOutput:
        """Verify credentials and return the Firebase ID token to the client."""
        user = self.repository.login(data.email, data.password)
        log_step("Application", "Login completed.", "Login mukammal ho gaya.")
        return AuthOutput(
            uid=user.uid,
            email=user.email,
            token=user.token,
        )
