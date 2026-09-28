from src.domain.repositories import ITodoRepository
from src.domain.exceptions import TodoNotFoundError
from src.application.dtos import CompleteTodoCommand, TodoDTO


class CompleteTodoUseCase:
    def __init__(self, todo_repo: ITodoRepository):
        self.todo_repo = todo_repo

    def execute(self, cmd: CompleteTodoCommand) -> TodoDTO:
        todo = self.todo_repo.get_by_id(cmd.todo_id)
        if not todo:
            raise TodoNotFoundError(f"Todo with ID '{cmd.todo_id}' was not found.")

        # Business logic aggregate ke method se chalegi
        todo.mark_as_completed()

        self.todo_repo.save(todo)

        return TodoDTO(
            id=todo.id,
            title=todo.title.value,
            priority=todo.priority.value,
            is_completed=todo.is_completed,
            created_at=todo.created_at.isoformat(),
            completed_at=todo.completed_at.isoformat() if todo.completed_at else None,
        )
