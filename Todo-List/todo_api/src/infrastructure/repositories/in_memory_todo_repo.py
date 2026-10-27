"""Temporary in-memory implementation of the todo repository.

English: Data stays in RAM and disappears when the server stops.
Roman Urdu: Data RAM mein rehta hai aur server band honay par khatam ho jata hai.
"""

from typing import Dict, List, Optional

from src.domain.entities import TodoItem
from src.domain.repositories import ITodoRepository


class InMemoryTodoRepository(ITodoRepository):
    def __init__(self):
        self.storage: Dict[str, TodoItem] = {}

    def save(self, todo: TodoItem) -> None:
        self.storage[todo.id] = todo

    def get_by_id(
        self,
        todo_id: str,
        owner_uid: str = "",
    ) -> Optional[TodoItem]:
        todo = self.storage.get(todo_id)

        if todo and owner_uid and todo.owner_uid != owner_uid:
            return None

        return todo

    def get_all(self) -> List[TodoItem]:
        return list(self.storage.values())

    def get_by_owner(self, owner_uid: str) -> List[TodoItem]:
        return [
            todo
            for todo in self.storage.values()
            if todo.owner_uid == owner_uid
        ]

    def delete(self, todo_id: str, owner_uid: str = "") -> None:
        todo = self.get_by_id(todo_id, owner_uid)

        if todo:
            del self.storage[todo_id]
