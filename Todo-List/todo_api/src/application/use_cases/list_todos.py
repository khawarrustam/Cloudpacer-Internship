"""Use case for listing todos."""

from typing import List

from src.application.dtos import TodoDTO
from src.application.mappers import todo_to_dto
from src.domain.repositories import ITodoRepository
from src.shared.console import print_step


class ListTodosUseCase:
    def __init__(self, todo_repo: ITodoRepository):
        self.todo_repo = todo_repo

    def execute(self, owner_uid: str = "") -> List[TodoDTO]:
        # English: Normal users only receive their own todos.
        # Roman Urdu: Normal user ko sirf uske apne todos milte hain.
        todos = (
            self.todo_repo.get_by_owner(owner_uid)
            if owner_uid
            else self.todo_repo.get_all()
        )

        print_step(
            "Application",
            f"Found {len(todos)} todo(s).",
            f"{len(todos)} todo milay.",
        )
        return [todo_to_dto(todo) for todo in todos]
