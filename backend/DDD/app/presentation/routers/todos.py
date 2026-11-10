"""Protected HTTP routes for todo workflows."""

from fastapi import APIRouter, HTTPException, status

from app.application.dto import CreateTodoInput, TodoActionInput, TodoOutput
from app.domain.todo import DomainError, TodoNotFoundError
from app.logging import log_step
from app.presentation.dependencies import CurrentUserDep, TodoServiceDep
from app.presentation.schemas import CreateTodoRequest, TodoResponse


router = APIRouter(prefix="/todos", tags=["Todos"])


@router.get("", response_model=list[TodoResponse])
def list_todos(
    user: CurrentUserDep,
    todo_service: TodoServiceDep,
) -> list[TodoOutput]:
    """Return todos belonging only to the verified current user."""
    log_step("Presentation", "Todo list requested.", "Todo list mangi gayi.")
    # Verified UID ki wajah se service sirf current database user ke todos read karti hai.
    return todo_service.list(user.uid)


@router.post("", response_model=TodoResponse, status_code=201)
def create_todo(
    request: CreateTodoRequest,
    user: CurrentUserDep,
    todo_service: TodoServiceDep,
) -> TodoOutput:
    """What: Create one todo for the verified user.

    When: The client submits POST /todos with a valid Bearer token.
    How: Map HTTP data to CreateTodoInput and let TodoService apply rules.
    """
    log_step(
        "Presentation",
        "Create todo request received.",
        "Create todo request mil gayi.",
    )
    try:
        # owner_uid client JSON se nahi, authenticated CurrentUser se aati hai.
        return todo_service.create(CreateTodoInput(
            title=request.title,
            priority=request.priority,
            owner_uid=user.uid,
        ))
    except DomainError as error:
        raise HTTPException(400, str(error)) from error


@router.patch("/{todo_id}/complete", response_model=TodoResponse)
def complete_todo(
    todo_id: str,
    user: CurrentUserDep,
    todo_service: TodoServiceDep,
) -> TodoOutput:
    """Complete one owned todo and translate domain errors to HTTP."""
    log_step(
        "Presentation",
        "Complete todo request received.",
        "Complete todo request mil gayi.",
    )
    try:
        # ID URL se aur owner verified token se combine hota hai.
        return todo_service.complete(TodoActionInput(
            todo_id=todo_id,
            owner_uid=user.uid,
        ))
    except TodoNotFoundError as error:
        raise HTTPException(404, str(error)) from error
    except DomainError as error:
        raise HTTPException(400, str(error)) from error


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(
    todo_id: str,
    user: CurrentUserDep,
    todo_service: TodoServiceDep,
) -> None:
    """Delete one owned todo or return HTTP 404."""
    log_step(
        "Presentation",
        "Delete todo request received.",
        "Delete todo request mil gayi.",
    )
    try:
        # Service delete se pehle ownership/existence check karti hai.
        todo_service.delete(TodoActionInput(
            todo_id=todo_id,
            owner_uid=user.uid,
        ))
    except TodoNotFoundError as error:
        raise HTTPException(404, str(error)) from error
    return None
