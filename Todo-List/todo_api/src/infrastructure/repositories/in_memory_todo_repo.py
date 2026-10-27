"""Temporary in-memory implementation of the todo repository.

English: Data stays in RAM and disappears when the server stops.
Roman Urdu: Data RAM mein rehta hai aur server band honay par khatam ho jata hai.
"""

from typing import Dict, List, Optional

from src.domain.entities import TodoItem
from src.domain.repositories import ITodoRepository
from src.shared.console import print_flow


class InMemoryTodoRepository(ITodoRepository):
    def __init__(self):
        self.storage: Dict[str, TodoItem] = {}

    def save(self, todo: TodoItem) -> None:
        print_flow(
            source="src/infrastructure/repositories/in_memory_todo_repo.py -> save",
            destination="in_memory_todo_repo.py -> RAM dictionary",
            data=f"todo_id={todo.id}, title={todo.title.value}",
            english="Saving the todo in temporary memory.",
            roman_urdu="Todo temporary memory mein save ho raha hai.",
        )
        self.storage[todo.id] = todo

    def get_by_id(
        self,
        todo_id: str,
        owner_uid: str = "",
    ) -> Optional[TodoItem]:
        print_flow(
            source="src/infrastructure/repositories/in_memory_todo_repo.py -> get_by_id",
            destination="in_memory_todo_repo.py -> RAM lookup",
            data=f"todo_id={todo_id}, owner_uid={owner_uid or 'not supplied'}",
            english="Looking for one todo in temporary memory.",
            roman_urdu="Temporary memory mein aik todo dhoonda ja raha hai.",
        )
        todo = self.storage.get(todo_id)

        if todo and owner_uid and todo.owner_uid != owner_uid:
            return None

        print_flow(
            source="in_memory_todo_repo.py -> RAM dictionary",
            destination="Calling file in src/application/use_cases/",
            data=f"todo_found={bool(todo)}",
            english="Returning the lookup result to the use case.",
            roman_urdu="Lookup result use case ko wapas ja raha hai.",
        )
        return todo

    def get_all(self) -> List[TodoItem]:
        todos = list(self.storage.values())
        print_flow(
            source="in_memory_todo_repo.py -> RAM dictionary",
            destination="src/application/use_cases/list_todos.py",
            data=f"todo_count={len(todos)}",
            english="Returning all temporary todos to the list use case.",
            roman_urdu="Tamam temporary todos list use case ko wapas ja rahe hain.",
        )
        return todos

    def get_by_owner(self, owner_uid: str) -> List[TodoItem]:
        todos = [
            todo
            for todo in self.storage.values()
            if todo.owner_uid == owner_uid
        ]
        print_flow(
            source="in_memory_todo_repo.py -> RAM dictionary",
            destination="src/application/use_cases/list_todos.py",
            data=f"owner_uid={owner_uid}, todo_count={len(todos)}",
            english="Returning this user's temporary todos.",
            roman_urdu="Is user ke temporary todos wapas ja rahe hain.",
        )
        return todos

    def delete(self, todo_id: str, owner_uid: str = "") -> None:
        todo = self.get_by_id(todo_id, owner_uid)

        if todo:
            del self.storage[todo_id]
            print_flow(
                source="in_memory_todo_repo.py -> RAM dictionary",
                destination="Removed from temporary memory",
                data=f"deleted_todo_id={todo_id}",
                english="The todo was removed from temporary memory.",
                roman_urdu="Todo temporary memory se remove ho gaya.",
            )
