"""Storage contract used by todo use cases.

English: The domain defines what storage must do, not how it does it.
Roman Urdu: Domain batata hai storage kya kare, yeh nahi ke kaise kare.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.entities import TodoItem


class ITodoRepository(ABC):
    @abstractmethod
    def save(self, todo: TodoItem) -> None:
        """Create or update one todo."""

    @abstractmethod
    def get_by_id(
        self,
        todo_id: str,
        owner_uid: str = "",
    ) -> Optional[TodoItem]:
        """Find one todo, optionally limited to one user."""

    @abstractmethod
    def get_all(self) -> List[TodoItem]:
        """Return all todos for trusted admin work."""

    @abstractmethod
    def get_by_owner(self, owner_uid: str) -> List[TodoItem]:
        """Return only one user's todos."""

    @abstractmethod
    def delete(self, todo_id: str, owner_uid: str = "") -> None:
        """Delete one todo, optionally limited to one user."""
