"""Application input and output DTOs used by the use cases."""

from dataclasses import dataclass
from datetime import datetime


# Input DTOs presentation se use case tak simple data le jati hain. Output DTOs
# use case ka result presentation ko deti hain; in mein FastAPI/Pydantic nahi hai.


@dataclass(frozen=True)
class CreateTodoInput:
    """Data needed by the application layer to create one todo."""

    title: str
    priority: str
    owner_uid: str
    owner_email: str
    due_at: datetime | None
    reminder_option: str
    custom_reminder_at: datetime | None


@dataclass(frozen=True)
class TodoActionInput:
    """Todo ID plus owner ID used for secure complete/delete actions."""

    todo_id: str
    owner_uid: str


@dataclass(frozen=True)
class SignupInput:
    """Signup data passed from the HTTP route to the auth service."""

    email: str
    password: str
    display_name: str


@dataclass(frozen=True)
class LoginInput:
    """Login credentials passed to the auth service."""

    email: str
    password: str


@dataclass(frozen=True)
class GoogleLoginInput:
    """Google ID token passed from the HTTP route to the auth service."""

    credential: str


@dataclass(frozen=True)
class TodoOutput:
    """Database-independent todo data returned by application services."""

    id: str
    title: str
    priority: str
    is_completed: bool
    created_at: str
    completed_at: str | None
    owner_uid: str
    due_at: str | None
    reminder_at: str | None
    reminder_sent_at: str | None
    reminder_option: str


@dataclass(frozen=True)
class AuthOutput:
    """Authenticated user data returned to the presentation layer."""

    uid: str
    email: str
    token: str
