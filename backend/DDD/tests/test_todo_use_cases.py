import pytest

from src.application.dtos import CompleteTodoCommand, CreateTodoCommand, DeleteTodoCommand
from src.application.use_cases.complete_todo import CompleteTodoUseCase
from src.application.use_cases.create_todo import CreateTodoUseCase
from src.application.use_cases.delete_todo import DeleteTodoUseCase
from src.domain.exceptions import TaskAlreadyCompletedError, TodoNotFoundError
from src.infrastructure.repositories.in_memory_todo_repo import InMemoryTodoRepository


@pytest.fixture
def repo():
    return InMemoryTodoRepository()


def create_todo(repo, owner_uid="owner-a"):
    return CreateTodoUseCase(repo).execute(
        CreateTodoCommand(title="Ship the polished workspace", priority="HIGH", owner_uid=owner_uid)
    )


def test_complete_updates_an_owned_todo(repo):
    todo = create_todo(repo)

    result = CompleteTodoUseCase(repo).execute(
        CompleteTodoCommand(todo_id=todo.id, owner_uid="owner-a")
    )

    assert result.is_completed is True
    assert result.completed_at is not None
    assert result.owner_uid == "owner-a"


def test_complete_cannot_mutate_another_users_todo(repo):
    todo = create_todo(repo, owner_uid="owner-a")

    with pytest.raises(TodoNotFoundError):
        CompleteTodoUseCase(repo).execute(
            CompleteTodoCommand(todo_id=todo.id, owner_uid="owner-b")
        )

    assert repo.get_by_id(todo.id, "owner-a").is_completed is False


def test_completed_todo_cannot_be_completed_twice(repo):
    todo = create_todo(repo)
    use_case = CompleteTodoUseCase(repo)
    command = CompleteTodoCommand(todo_id=todo.id, owner_uid="owner-a")
    use_case.execute(command)

    with pytest.raises(TaskAlreadyCompletedError):
        use_case.execute(command)


def test_delete_removes_an_owned_todo(repo):
    todo = create_todo(repo)

    DeleteTodoUseCase(repo).execute(
        DeleteTodoCommand(todo_id=todo.id, owner_uid="owner-a")
    )

    assert repo.get_by_id(todo.id, "owner-a") is None


def test_delete_cannot_remove_another_users_todo(repo):
    todo = create_todo(repo, owner_uid="owner-a")

    with pytest.raises(TodoNotFoundError):
        DeleteTodoUseCase(repo).execute(
            DeleteTodoCommand(todo_id=todo.id, owner_uid="owner-b")
        )

    assert repo.get_by_id(todo.id, "owner-a") is not None
