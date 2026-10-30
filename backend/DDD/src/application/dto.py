"""Application input and output DTOs used by the use cases."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CreateTodoInput:
    title: str
    priority: str
    owner_uid: str


@dataclass(frozen=True)
class TodoActionInput:
    todo_id: str
    owner_uid: str


@dataclass(frozen=True)
class SignupInput:
    email: str
    password: str
    display_name: str


@dataclass(frozen=True)
class LoginInput:
    email: str
    password: str


@dataclass(frozen=True)
class TodoOutput:
    id: str
    title: str
    priority: str
    is_completed: bool
    created_at: str
    completed_at: str | None
    owner_uid: str


@dataclass(frozen=True)
class AuthOutput:
    uid: str
    email: str
    token: str
