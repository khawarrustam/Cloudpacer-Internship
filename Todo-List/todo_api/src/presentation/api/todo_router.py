"""HTTP routes for todo actions."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from src.application.dtos import (
    CompleteTodoCommand,
    CreateTodoCommand,
    DeleteTodoCommand,
)
from src.application.use_cases.complete_todo import CompleteTodoUseCase
from src.application.use_cases.create_todo import CreateTodoUseCase
from src.application.use_cases.delete_todo import DeleteTodoUseCase
from src.application.use_cases.list_todos import ListTodosUseCase
from src.domain.exceptions import DomainError, TodoNotFoundError
from src.presentation.api.dependencies import CurrentUser, get_current_user
from src.presentation.api.schemas import CreateTodoRequest, TodoResponse
from src.shared.console import print_error, print_step

router = APIRouter(prefix="/todos", tags=["Todos"])


# English: main.py replaces these placeholders with real use cases.
# Roman Urdu: main.py in placeholders ki jagah real use cases deta hai.
def get_create_use_case() -> CreateTodoUseCase:
    raise NotImplementedError


def get_complete_use_case() -> CompleteTodoUseCase:
    raise NotImplementedError


def get_list_use_case() -> ListTodosUseCase:
    raise NotImplementedError


def get_delete_use_case() -> DeleteTodoUseCase:
    raise NotImplementedError


@router.post("", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(
    request: CreateTodoRequest,
    user: CurrentUser = Depends(get_current_user),
    use_case: CreateTodoUseCase = Depends(get_create_use_case),
):
    print_step(
        "API",
        f"POST /todos received from {user.email}.",
        f"{user.email} se POST /todos request mili.",
    )

    try:
        command = CreateTodoCommand(
            title=request.title,
            priority=request.priority,
            owner_uid=user.uid,
        )
        return use_case.execute(command)
    except DomainError as error:
        print_error("API", str(error), f"Request fail hui: {error}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.patch("/{todo_id}/complete", response_model=TodoResponse)
def complete_todo(
    todo_id: str,
    user: CurrentUser = Depends(get_current_user),
    use_case: CompleteTodoUseCase = Depends(get_complete_use_case),
):
    print_step(
        "API",
        f"Completing todo {todo_id}.",
        f"Todo {todo_id} complete kiya ja raha hai.",
    )

    try:
        command = CompleteTodoCommand(todo_id=todo_id, owner_uid=user.uid)
        return use_case.execute(command)
    except TodoNotFoundError as error:
        print_error("API", str(error), f"Todo nahi mila: {error}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except DomainError as error:
        print_error("API", str(error), f"Request fail hui: {error}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.get("", response_model=List[TodoResponse])
def get_todos(
    user: CurrentUser = Depends(get_current_user),
    use_case: ListTodosUseCase = Depends(get_list_use_case),
):
    print_step(
        "API",
        f"Loading todos for {user.email}.",
        f"{user.email} ke todos load ho rahe hain.",
    )
    return use_case.execute(owner_uid=user.uid)


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(
    todo_id: str,
    user: CurrentUser = Depends(get_current_user),
    use_case: DeleteTodoUseCase = Depends(get_delete_use_case),
):
    print_step(
        "API",
        f"Deleting todo {todo_id}.",
        f"Todo {todo_id} delete kiya ja raha hai.",
    )

    try:
        command = DeleteTodoCommand(todo_id=todo_id, owner_uid=user.uid)
        use_case.execute(command)
    except TodoNotFoundError as error:
        print_error("API", str(error), f"Todo nahi mila: {error}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    return None
