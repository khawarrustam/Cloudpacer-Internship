"""Thin protected HTTP routes for todo endpoints."""

from fastapi import APIRouter, status

from app.application.dto import TodoOutput
from app.presentation.controllers.todo_controller import (
    add_todo,
    finish_todo,
    get_todos,
    remove_todo,
)
from app.presentation.dependencies import CurrentUserDep, TodoServiceDep
from app.presentation.schemas import CreateTodoRequest, TodoResponse


router = APIRouter(prefix="/todos", tags=["Todos"])


@router.get("", response_model=list[TodoResponse])
def list_todos(
    user: CurrentUserDep,
    todo_service: TodoServiceDep,
) -> list[TodoOutput]:
    """Delegate list handling to the todo controller."""
    return get_todos(user.uid, todo_service)


@router.post("", response_model=TodoResponse, status_code=201)
def create_todo(
    request: CreateTodoRequest,
    user: CurrentUserDep,
    todo_service: TodoServiceDep,
) -> TodoOutput:
    """Delegate create handling with trusted user identity."""
    return add_todo(request, user.uid, user.email, todo_service)


@router.patch("/{todo_id}/complete", response_model=TodoResponse)
def complete_todo(
    todo_id: str,
    user: CurrentUserDep,
    todo_service: TodoServiceDep,
) -> TodoOutput:
    """Delegate completion handling to the todo controller."""
    return finish_todo(todo_id, user.uid, todo_service)


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(
    todo_id: str,
    user: CurrentUserDep,
    todo_service: TodoServiceDep,
) -> None:
    """Delegate deletion handling to the todo controller."""
    remove_todo(todo_id, user.uid, todo_service)
