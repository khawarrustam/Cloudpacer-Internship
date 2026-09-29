from src.domain.entities import TodoItem
from src.domain.value_objects import Priority
from src.domain.repositories import ITodoRepository
from src.application.dtos import CreateTodoCommand, TodoDTO


class CreateTodoUseCase:
    def __init__(self, todo_repo: ITodoRepository):
        self.todo_repo = todo_repo

    def execute(self, cmd: CreateTodoCommand) -> TodoDTO:
        todo = TodoItem.create(title=cmd.title, priority=Priority(cmd.priority.upper()))
        self.todo_repo.save(todo)

        return TodoDTO(
            id=todo.id,
            title=todo.title.value,
            priority=todo.priority.value,
            is_completed=todo.is_completed,
            created_at=todo.created_at.isoformat(),
            completed_at=None,
        )
