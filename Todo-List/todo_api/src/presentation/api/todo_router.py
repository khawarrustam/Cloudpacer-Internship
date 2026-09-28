from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from src.presentation.api.schemas import CreateTodoRequest, TodoResponse
from src.application.dtos import CreateTodoCommand, CompleteTodoCommand
from src.application.use_cases.create_todo import CreateTodoUseCase
from src.application.use_cases.complete_todo import CompleteTodoUseCase
from src.application.use_cases.list_todos import ListTodosUseCase
from src.domain.exceptions import DomainError, TodoNotFoundError

router = APIRouter(prefix="/todos", tags=["Todos"])


# Dependency placeholders (main.py mein inject honge)
def get_create_use_case() -> CreateTodoUseCase:
    raise NotImplementedError


def get_complete_use_case() -> CompleteTodoUseCase:
    raise NotImplementedError


def get_list_use_case() -> ListTodosUseCase:
    raise NotImplementedError


@router.post("", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(
    req: CreateTodoRequest, use_case: CreateTodoUseCase = Depends(get_create_use_case)
):
    try:
        cmd = CreateTodoCommand(title=req.title, priority=req.priority)
        return use_case.execute(cmd)
    except DomainError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@router.patch("/{todo_id}/complete", response_model=TodoResponse)
def complete_todo(
    todo_id: str, use_case: CompleteTodoUseCase = Depends(get_complete_use_case)
):
    try:
        cmd = CompleteTodoCommand(todo_id=todo_id)
        return use_case.execute(cmd)
    except TodoNotFoundError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))
    except DomainError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@router.get("", response_model=List[TodoResponse])
def get_todos(use_case: ListTodosUseCase = Depends(get_list_use_case)):
    return use_case.execute()
