"""
=============================================================================
INFRASTRUCTURE LAYER — In-Memory Repository Adapter (Clean Architecture)
=============================================================================
Infrastructure layer bahar ki duniya (Databases, Third-party APIs, File System)
se interact karti hai.

Yeh class `InMemoryTodoRepository` hamara In-Memory Storage Adapter hai:
- Yeh Domain layer ke contract `ITodoRepository` ko implement karti hai.
- Yeh data ko Python dictionary (`self._storage`) mein RAM ke andar save rakhti hai.
- Faida: Unit tests chalane ke liye ya bina Firebase account / internet ke local development
  karne ke liye yeh best hai.

Kahan Connected Hai:
- Implements: `src/domain/repositories.py` ka `ITodoRepository`.
- Instantiation: `main.py` mein jab `USE_FIREBASE=false` ho, toh yeh repository instantiate hoti hai.
=============================================================================
"""

# ---------------------------------------------------------------------------
# LIBRARIES / IMPORTS (Kyun aur kis liye import ki gayi hain):
# ---------------------------------------------------------------------------
# 'typing': Dict (dictionary storage), List (saare todos ki list), Optional (item milay ya None) ke liye.
from typing import Dict, List, Optional

# DOMAIN ENTITY: Jisko memory mein store karna hai.
from src.domain.entities import TodoItem

# REPOSITORY INTERFACE: Abstract base class jiske methods ko yeh class implement karti hai.
from src.domain.repositories import ITodoRepository


# ---------------------------------------------------------------------------
# IN-MEMORY ADAPTER CLASS:
# ---------------------------------------------------------------------------
class InMemoryTodoRepository(ITodoRepository):
    """
    Kyun banaya gaya:
    - Fast testing aur credentials-free local execution ke liye in-memory storage provider.
    """

    def __init__(self):
        """Storage ke liye khali Python dictionary initialize karta hai."""
        self._storage: Dict[str, TodoItem] = {}

    def save(self, todo: TodoItem) -> None:
        """
        Kyun use ho raha hai:
        - Todo item ko memory dictionary mein save ya update karta hai.
        - Key: `todo.id`, Value: `TodoItem` object.
        """
        self._storage[todo.id] = todo

    def get_by_id(self, todo_id: str) -> Optional[TodoItem]:
        """
        Kyun use ho raha hai:
        - Memory dictionary se specific ID ka Todo dhoondta hai.
        - Agar mojood ho toh `TodoItem` return karta hai, warna `None`.
        """
        return self._storage.get(todo_id)

    def get_all(self) -> List[TodoItem]:
        """
        Kyun use ho raha hai:
        - Tamam stored `TodoItem` entities ko list ki shakal mein return karta hai.
        """
        return list(self._storage.values())

    def get_by_owner(self, owner_uid: str) -> List[TodoItem]:
        """
        Kyun use ho raha hai:
        - Sirf ek specific user ke todos filter karke return karta hai.
        """
        return [t for t in self._storage.values() if t.owner_uid == owner_uid]
