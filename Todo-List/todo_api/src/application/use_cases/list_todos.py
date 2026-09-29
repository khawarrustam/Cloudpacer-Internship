"""
=============================================================================
APPLICATION LAYER — List Todos Use Case (Clean Architecture / DDD)
=============================================================================
Yeh Use Case database mein mojood tamam Todos ko fetch karne aur unhe
DTOs ki list mein convert karke presentation layer ko bhejne ke liye use hota hai.

ListTodosUseCase ka Kaam:
1. Repository se saari domain entities mangwana (`get_all()`).
2. Har entity ko safe `TodoDTO` mein transform karna.
3. List of DTOs return karna.

Kahan Connected Hai:
- Instantiation: `main.py` is class ko repository ke sath instantiate karta hai.
- Caller: `src/presentation/api/todo_router.py` ke `get_todos` GET endpoint se call hota hai.
- Storage Call: `src/domain/repositories.py` ke `get_all()` method ko call karta hai.
=============================================================================
"""

# ---------------------------------------------------------------------------
# LIBRARIES / IMPORTS (Kyun aur kis liye import ki gayi hain):
# ---------------------------------------------------------------------------
# 'typing.List': Ek se zyada items ki list return type annotate karne ke liye.
from typing import List

# REPOSITORY INTERFACE: Tamam todos retrieve karne ke liye abstract contract.
from src.domain.repositories import ITodoRepository

# APPLICATION DTO: Single todo ka presentation-safe data container.
from src.application.dtos import TodoDTO


# ---------------------------------------------------------------------------
# USE CASE CLASS:
# ---------------------------------------------------------------------------
class ListTodosUseCase:
    """
    Kyun banaya gaya:
    - Single Responsibility: Tamam Todos ki list laane ka workflow manage karna.
    """

    def __init__(self, todo_repo: ITodoRepository):
        """
        Dependency Injection (DI):
        - Abstract repository interface inject hota hai.
        """
        self.todo_repo = todo_repo

    def execute(self) -> List[TodoDTO]:
        """
        Kyun use ho raha hai:
        - Tamam todos ko repository se fetch karke DTOs ki list banata hai.

        Kaise kaam karta hai:
        1. `self.todo_repo.get_all()` call karke saari `TodoItem` entities hasil karta hai.
        2. List comprehension ke zariye har entity ko `TodoDTO` mein map karta hai.
        3. DTOs ki list return karta hai.

        Kahan connected hai:
        - `src/presentation/api/todo_router.py` ke `get_todos` GET route se call hota hai.
        """
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
