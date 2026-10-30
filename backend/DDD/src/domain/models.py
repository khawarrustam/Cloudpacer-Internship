"""Domain layer: todo rules and repository contracts."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import uuid


class DomainError(Exception):
    """Base error for business-rule failures."""


class InvalidTaskTitleError(DomainError):
    pass


class TaskAlreadyCompletedError(DomainError):
    pass


class TodoNotFoundError(DomainError):
    pass


class ValidationException(DomainError):
    pass


class Priority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


@dataclass(frozen=True)
class TaskTitle:
    """A title that always contains 3 to 120 characters."""

    value: str

    def __post_init__(self):
        clean_title = self.value.strip() if self.value else ""
        if len(clean_title) < 3:
            raise InvalidTaskTitleError("Title must have at least 3 characters.")
        if len(clean_title) > 120:
            raise InvalidTaskTitleError("Title cannot exceed 120 characters.")
        object.__setattr__(self, "value", clean_title)


@dataclass
class TodoItem:
    """Main todo entity containing its own business rule."""

    id: str
    title: TaskTitle
    priority: Priority
    is_completed: bool
    created_at: datetime
    owner_uid: str
    completed_at: datetime | None = None

    @classmethod
    def create(cls, title: str, priority: str, owner_uid: str):
        return cls(
            id=str(uuid.uuid4()),
            title=TaskTitle(title),
            priority=Priority(priority.upper()),
            is_completed=False,
            created_at=datetime.now(timezone.utc),
            owner_uid=owner_uid,
        )

    def complete(self) -> None:
        if self.is_completed:
            raise TaskAlreadyCompletedError("Todo is already completed.")
        self.is_completed = True
        self.completed_at = datetime.now(timezone.utc)


class TodoRepository(ABC):
    """Storage contract implemented by memory and Firestore repositories."""

    @abstractmethod
    def save(self, todo: TodoItem) -> None:
        pass

    @abstractmethod
    def get_by_id(self, todo_id: str, owner_uid: str) -> TodoItem | None:
        pass

    @abstractmethod
    def get_by_owner(self, owner_uid: str) -> list[TodoItem]:
        pass

    @abstractmethod
    def delete(self, todo_id: str, owner_uid: str) -> None:
        pass


@dataclass(frozen=True)
class UserData:
    uid: str
    email: str
    token: str


class AuthRepository(ABC):
    @abstractmethod
    def signup(self, email: str, password: str, name: str) -> UserData:
        pass

    @abstractmethod
    def login(self, email: str, password: str) -> UserData:
        pass
