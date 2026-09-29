from abc import ABC, abstractmethod
from typing import List, Optional
from .entities import TodoItem


class ITodoRepository(ABC):
    """Port / Abstraction: Domain defines the contract; Infrastructure implements it."""

    @abstractmethod
    def save(self, todo: TodoItem) -> None:
        pass

    @abstractmethod
    def get_by_id(self, todo_id: str) -> Optional[TodoItem]:
        pass

    @abstractmethod
    def get_all(self) -> List[TodoItem]:
        pass
