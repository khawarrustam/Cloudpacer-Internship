"""Application input and output DTOs used by the use cases."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CreateTodoInput:
    """Data needed by the application layer to create one todo."""
    title: str
    priority: str
    owner_uid: str


@dataclass(frozen=True)
class TodoActionInput:
    """Todo ID plus owner ID used for secure complete/delete actions."""
    todo_id: str
    owner_uid: str


@dataclass(frozen=True)
class SignupInput:
    """Signup data passed from the HTTP route to the auth use case."""
    email: str
    password: str
    display_name: str


@dataclass(frozen=True)
class LoginInput:
    """Login credentials passed to the auth use case."""
    email: str
    password: str


@dataclass(frozen=True)
class TodoOutput:
    """Database-independent todo data returned by application use cases."""
    id: str
    title: str
    priority: str
    is_completed: bool
    created_at: str
    completed_at: str | None
    owner_uid: str


@dataclass(frozen=True)
class AuthOutput:
    """Authenticated user data returned to the presentation layer."""
    uid: str
    email: str
    token: str
