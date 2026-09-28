from typing import List
from src.domain.repositories import ITodoRepository
from src.application.dtos import TodoDTO


class ListTodosUseCase:
    def __init__(self, todo_repo: ITodoRepository):
        self.todo_repo = todo_repo

    def execute(self) -> List[TodoDTO]:
        todos = self.todo_repo.get_all()
        return [
            TodoDTO(
                id=t.id,
                title=t.title.value,
                priority=t.priority.value,
                is_completed=t.is_completed,
                created_at=t.created_at.isoformat(),
                completed_at=t.completed_at.isoformat() if t.completed_at else None,
            )
            for t in todos
        ]
