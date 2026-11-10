"""Todo business rules, entity, value objects, and repository contract."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import uuid


class DomainError(Exception):
    """Parent error for todo business-rule failures."""


class InvalidTaskTitleError(DomainError):
    """Raised when a todo title is too short or too long."""


class TaskAlreadyCompletedError(DomainError):
    """Raised when an already completed todo is completed again."""


class TodoNotFoundError(DomainError):
    """Raised when the requested user's todo does not exist."""


class Priority(str, Enum):
    """Supported todo priority values."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


@dataclass(frozen=True)
class TaskTitle:
    """What: Represent an always-valid todo title.

    When: A TodoItem is created or restored from a database.
    How: Trim text and enforce the shared 3-to-120-character rule.
    """

    value: str

    def __post_init__(self) -> None:
        # Title ko entity mein enter hote hi clean aur valid banate hain. Baad
        # mein har layer safely assume kar sakti hai ke title valid hai.
        clean_title = (self.value or "").strip()
        if len(clean_title) < 3:
            raise InvalidTaskTitleError("Title must have at least 3 characters.")
        if len(clean_title) > 120:
            raise InvalidTaskTitleError("Title cannot exceed 120 characters.")
        object.__setattr__(self, "value", clean_title)


@dataclass
class TodoItem:
    """Main todo entity containing data and completion business rules."""

    id: str
    title: TaskTitle
    priority: Priority
    is_completed: bool
    created_at: datetime
    owner_uid: str
    completed_at: datetime | None = None

    @classmethod
    def create(cls, title: str, priority: str, owner_uid: str) -> "TodoItem":
        """Create a new valid, incomplete todo with a unique ID and UTC time."""
        # ID/time client se nahi lete; server consistent trusted values banata hai.
        return cls(
            id=str(uuid.uuid4()),
            title=TaskTitle(title),
            priority=Priority(priority.upper()),
            is_completed=False,
            created_at=datetime.now(timezone.utc),
            owner_uid=owner_uid,
        )

    def complete(self) -> None:
        """Apply the one-time completion business rule."""
        # Completion ka rule route ya database mein nahi, entity ke andar hai.
        if self.is_completed:
            raise TaskAlreadyCompletedError("Todo is already completed.")
        self.is_completed = True
        self.completed_at = datetime.now(timezone.utc)


class TodoRepository(ABC):
    """What: Define persistence operations required by todo use cases.

    When: TodoService saves or reads domain entities.
    How: Infrastructure adapters implement this contract for each database.
    """

    # Service isi contract par depend karti hai, isliye selected database badalne
    # par application workflow ko change karne ki zarurat nahi hoti.
    @abstractmethod
    def save(self, todo: TodoItem) -> None:
        """Create a todo or save its latest state."""
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, todo_id: str, owner_uid: str) -> TodoItem | None:
        """Return one owned todo, or None when not found."""
        raise NotImplementedError

    @abstractmethod
    def get_by_owner(self, owner_uid: str) -> list[TodoItem]:
        """Return all todos belonging to one authenticated user."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, todo_id: str, owner_uid: str) -> None:
        """Delete one todo only for its owner."""
        raise NotImplementedError
