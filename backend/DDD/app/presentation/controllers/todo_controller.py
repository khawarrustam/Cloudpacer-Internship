"""Presentation controllers for todo requests."""

from fastapi import HTTPException

from app.application.dto import CreateTodoInput, TodoActionInput, TodoOutput
from app.application.todo_service import TodoService
from app.domain.reminder import ReminderError
from app.domain.todo import DomainError, TodoNotFoundError
from app.logging import log_step
from app.presentation.schemas import CreateTodoRequest


def get_todos(owner_uid: str, todo_service: TodoService) -> list[TodoOutput]:
    """Return only the authenticated user's todos."""
    log_step("Presentation", "Todo list requested.", "Todo list mangi gayi.")
    return todo_service.list(owner_uid)


def add_todo(
    request: CreateTodoRequest,
    owner_uid: str,
    owner_email: str,
    todo_service: TodoService,
) -> TodoOutput:
    """Map trusted user/request data to the create-todo use case."""
    log_step(
        "Presentation",
        "Create todo request received.",
        "Create todo request mil gayi.",
    )
    try:
        return todo_service.create(CreateTodoInput(
            title=request.title,
            priority=request.priority,
            owner_uid=owner_uid,
            owner_email=owner_email,
            due_at=request.due_at,
            reminder_option=request.reminder_option,
            custom_reminder_at=request.custom_reminder_at,
        ))
    except (DomainError, ReminderError) as error:
        raise HTTPException(400, str(error)) from error


def finish_todo(
    todo_id: str,
    owner_uid: str,
    todo_service: TodoService,
) -> TodoOutput:
    """Complete an owned todo and translate expected domain errors."""
    log_step(
        "Presentation",
        "Complete todo request received.",
        "Complete todo request mil gayi.",
    )
    try:
        return todo_service.complete(TodoActionInput(todo_id, owner_uid))
    except TodoNotFoundError as error:
        raise HTTPException(404, str(error)) from error
    except DomainError as error:
        raise HTTPException(400, str(error)) from error


def remove_todo(
    todo_id: str,
    owner_uid: str,
    todo_service: TodoService,
) -> None:
    """Delete an owned todo and return HTTP 404 when it does not exist."""
    log_step(
        "Presentation",
        "Delete todo request received.",
        "Delete todo request mil gayi.",
    )
    try:
        todo_service.delete(TodoActionInput(todo_id, owner_uid))
    except TodoNotFoundError as error:
        raise HTTPException(404, str(error)) from error
