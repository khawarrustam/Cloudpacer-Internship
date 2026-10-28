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
from src.shared.console import print_error, print_flow

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
    print_flow(
        source="Frontend -> POST /todos",
        destination="src/presentation/api/todo_router.py -> create_todo",
        data=f"title={request.title}, priority={request.priority}",
        english="The frontend sent new todo data to the API router.",
        roman_urdu="Frontend ne naya todo data API router ko bheja.",
    )

    try:
        command = CreateTodoCommand(
            title=request.title,
            priority=request.priority,
            owner_uid=user.uid,
        )
        result = use_case.execute(command)
        print_flow(
            source="src/application/use_cases/create_todo.py",
            destination="Frontend <- HTTP 201 response",
            data=f"todo_id={result.id}, is_completed={result.is_completed}",
            english="The created todo is going back to the frontend.",
            roman_urdu="Created todo frontend ko wapas ja raha hai.",
        )
        return result
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
    print_flow(
        source=f"Frontend -> PATCH /todos/{todo_id}/complete",
        destination="src/presentation/api/todo_router.py -> complete_todo",
        data=f"todo_id={todo_id}",
        english="The frontend sent a complete request to the API router.",
        roman_urdu="Frontend ne complete request API router ko bheji.",
    )

    try:
        command = CompleteTodoCommand(todo_id=todo_id, owner_uid=user.uid)
        result = use_case.execute(command)
        print_flow(
            source="src/application/use_cases/complete_todo.py",
            destination="Frontend <- HTTP 200 response",
            data=f"todo_id={result.id}, is_completed={result.is_completed}",
            english="The completed todo is going back to the frontend.",
            roman_urdu="Completed todo frontend ko wapas ja raha hai.",
        )
        return result
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
    print_flow(
        source="Frontend -> GET /todos",
        destination="src/application/use_cases/list_todos.py",
        data=f"owner_uid={user.uid}",
        english="The router is asking the list use case for this user's todos.",
        roman_urdu="Router list use case se is user ke todos mang raha hai.",
    )
    results = use_case.execute(owner_uid=user.uid)
    print_flow(
        source="src/application/use_cases/list_todos.py",
        destination="Frontend <- HTTP 200 response",
        data=f"todo_count={len(results)}",
        english="The todo list is going back to the frontend.",
        roman_urdu="Todo list frontend ko wapas ja rahi hai.",
    )
    return results


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(
    todo_id: str,
    user: CurrentUser = Depends(get_current_user),
    use_case: DeleteTodoUseCase = Depends(get_delete_use_case),
):
    print_flow(
        source=f"Frontend -> DELETE /todos/{todo_id}",
        destination="src/presentation/api/todo_router.py -> delete_todo",
        data=f"todo_id={todo_id}",
        english="The frontend sent a delete request to the API router.",
        roman_urdu="Frontend ne delete request API router ko bheji.",
    )

    try:
        command = DeleteTodoCommand(todo_id=todo_id, owner_uid=user.uid)
        use_case.execute(command)
        print_flow(
            source="src/application/use_cases/delete_todo.py",
            destination="Frontend <- HTTP 204 response",
            data=f"deleted_todo_id={todo_id}",
            english="Delete finished; an empty success response is going back.",
            roman_urdu="Delete ho gaya; empty success response wapas ja raha hai.",
        )
    except TodoNotFoundError as error:
        print_error("API", str(error), f"Todo nahi mila: {error}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    return None
