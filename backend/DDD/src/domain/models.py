"""Domain layer: todo rules and repository contracts."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import uuid


class DomainError(Exception):
    """Parent error for todo business-rule failures.

    Kyun: Routes tamam domain errors ko aik common type se handle kar sakti hain.
    """


class InvalidTaskTitleError(DomainError):
    """Raised when a todo title is too short or too long."""
    pass


class TaskAlreadyCompletedError(DomainError):
    """Raised to stop an already completed todo being completed again."""
    pass


class TodoNotFoundError(DomainError):
    """Raised when the requested user's todo does not exist."""
    pass


class ValidationException(DomainError):
    """Wrap authentication/input errors that can safely reach the API."""
    pass


class Priority(str, Enum):
    """Allow only the three priority values supported by the application."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


@dataclass(frozen=True)
class TaskTitle:
    """A title value that always contains 3 to 120 characters.

    Kyun: Validation domain ke andar rehne se har route aur database par same
    title rule automatically apply hota hai.
    """

    value: str

    def __post_init__(self):
        """Trim and validate the title immediately after object creation."""
        clean_title = self.value.strip() if self.value else ""
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
    def create(cls, title: str, priority: str, owner_uid: str):
        """Create a new incomplete todo with a unique ID and UTC time.

        Kyun: Har naya todo aik consistent, valid state mein start hona chahiye.
        """
        return cls(
            id=str(uuid.uuid4()),
            title=TaskTitle(title),
            priority=Priority(priority.upper()),
            is_completed=False,
            created_at=datetime.now(timezone.utc),
            owner_uid=owner_uid,
        )

    def complete(self) -> None:
        """Mark this todo complete and remember when it was completed.

        Kyun: Entity khud duplicate completion ko rokti hai, chahe koi bhi
        database adapter active ho.
        """
        if self.is_completed:
            raise TaskAlreadyCompletedError("Todo is already completed.")
        self.is_completed = True
        self.completed_at = datetime.now(timezone.utc)


class TodoRepository(ABC):
    """Common storage contract implemented by every todo database.

    Kyun: Use cases ko Firestore, MongoDB, ya PostgreSQL ka direct knowledge
    nahi chahiye; unko sirf yeh four operations chahiye.
    """

    @abstractmethod
    def save(self, todo: TodoItem) -> None:
        """Create a todo or save its latest state."""
        pass

    @abstractmethod
    def get_by_id(self, todo_id: str, owner_uid: str) -> TodoItem | None:
        """Return one owned todo, or None when it is not found."""
        pass

    @abstractmethod
    def get_by_owner(self, owner_uid: str) -> list[TodoItem]:
        """Return all todos belonging to one authenticated user."""
        pass

    @abstractmethod
    def delete(self, todo_id: str, owner_uid: str) -> None:
        """Delete one todo only for its owner."""
        pass


@dataclass(frozen=True)
class UserData:
    """Small authenticated-user object returned by Firebase infrastructure."""
    uid: str
    email: str
    token: str


class AuthRepository(ABC):
    """Authentication contract used by application-level auth use cases."""

    @abstractmethod
    def signup(self, email: str, password: str, name: str) -> UserData:
        """Create an account and return authenticated user data."""
        pass

    @abstractmethod
    def login(self, email: str, password: str) -> UserData:
        """Verify credentials and return authenticated user data."""
        pass
