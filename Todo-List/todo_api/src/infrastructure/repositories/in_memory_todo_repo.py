from typing import Dict, List, Optional
from src.domain.entities import TodoItem
from src.domain.repositories import ITodoRepository


class InMemoryTodoRepository(ITodoRepository):
    """In-memory storage for unit tests and local dev without Firebase credentials."""

    def __init__(self):
        self._storage: Dict[str, TodoItem] = {}

    def save(self, todo: TodoItem) -> None:
        self._storage[todo.id] = todo

    def get_by_id(self, todo_id: str) -> Optional[TodoItem]:
        return self._storage.get(todo_id)

    def get_all(self) -> List[TodoItem]:
        return list(self._storage.values())
