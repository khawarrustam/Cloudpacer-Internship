"""Simple input and output objects for todo use cases.

English: Commands carry input; TodoDTO carries safe output.
Roman Urdu: Command input laata hai; TodoDTO safe output le jata hai.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CreateTodoCommand:
    title: str
    priority: str
    owner_uid: str = ""


@dataclass(frozen=True)
class CompleteTodoCommand:
    todo_id: str
    owner_uid: str


@dataclass(frozen=True)
class DeleteTodoCommand:
    todo_id: str
    owner_uid: str


@dataclass(frozen=True)
class TodoDTO:
    id: str
    title: str
    priority: str
    is_completed: bool
    created_at: str
    completed_at: str | None
    owner_uid: str = ""
