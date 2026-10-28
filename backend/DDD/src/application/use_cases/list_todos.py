"""Use case for listing todos."""

from typing import List

from src.application.dtos import TodoDTO
from src.application.mappers import todo_to_dto
from src.domain.repositories import ITodoRepository
from src.shared.console import module_file, print_flow, print_step


class ListTodosUseCase:
    def __init__(self, todo_repo: ITodoRepository):
        self.todo_repo = todo_repo

    def execute(self, owner_uid: str = "") -> List[TodoDTO]:
        # English: Normal users only receive their own todos.
        # Roman Urdu: Normal user ko sirf uske apne todos milte hain.
        print_flow(
            source="src/application/use_cases/list_todos.py",
            destination=module_file(self.todo_repo),
            data=f"owner_uid={owner_uid or 'all'}",
            english="Asking the repository for the correct todo list.",
            roman_urdu="Repository se sahi todo list mangi ja rahi hai.",
        )
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
        print_flow(
            source=module_file(self.todo_repo),
            destination="src/application/mappers.py",
            data=f"todo_count={len(todos)}",
            english="Sending domain todos to the DTO mapper.",
            roman_urdu="Domain todos DTO mapper ko bhejay ja rahe hain.",
        )
        return [todo_to_dto(todo) for todo in todos]
