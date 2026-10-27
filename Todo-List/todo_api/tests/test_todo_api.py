from src.application.use_cases.complete_todo import CompleteTodoUseCase
from src.application.use_cases.create_todo import CreateTodoUseCase
from src.application.use_cases.delete_todo import DeleteTodoUseCase
from src.application.use_cases.list_todos import ListTodosUseCase
from src.infrastructure.repositories.in_memory_todo_repo import (
    InMemoryTodoRepository,
)
from src.presentation.api.dependencies import CurrentUser
from src.presentation.api.schemas import CreateTodoRequest
from src.presentation.api.todo_router import (
    complete_todo,
    create_todo,
    delete_todo,
    get_todos,
)


def test_todo_routes_work_together():
    repository = InMemoryTodoRepository()
    user = CurrentUser(
        uid="route-test-user",
        email="route-test@example.com",
    )
    create_use_case = CreateTodoUseCase(repository)
    list_use_case = ListTodosUseCase(repository)
    complete_use_case = CompleteTodoUseCase(repository)
    delete_use_case = DeleteTodoUseCase(repository)

    todo = create_todo(
        request=CreateTodoRequest(
            title="Learn the simple DDD flow",
            priority="HIGH",
        ),
        user=user,
        use_case=create_use_case,
    )

    todos = get_todos(user=user, use_case=list_use_case)
    assert [item.id for item in todos] == [todo.id]

    completed = complete_todo(
        todo_id=todo.id,
        user=user,
        use_case=complete_use_case,
    )
    assert completed.is_completed is True

    result = delete_todo(
        todo_id=todo.id,
        user=user,
        use_case=delete_use_case,
    )
    assert result is None
    assert get_todos(user=user, use_case=list_use_case) == []
