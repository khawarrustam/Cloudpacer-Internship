"""
=============================================================================
DOMAIN LAYER — Repository Interface / Port (Clean Architecture / DDD)
=============================================================================
Clean Architecture (Onion / Hexagonal) ka sab se ahem usool hai:
"Dependency Inversion Principle (DIP)".

Domain Layer ko yeh bilkul nahi pata hona chahiye ke data kahan save ho raha hai
(kya woh Firebase hai, PostgreSQL hai, MongoDB hai, ya sirf Memory hai).
Is liye Domain Layer sirf ek "Contract / Interface (Port)" define karti hai.

Kahan Connected Hai:
- Implementations (Adapters):
  1. `src/infrastructure/repositories/firestore_todo_repo.py` (Real Firebase DB)
  2. `src/infrastructure/repositories/in_memory_todo_repo.py` (Testing / Local Memory)
- Consumers:
  Tamam Use Cases (`create_todo.py`, `complete_todo.py`, `list_todos.py`) is interface
  par depend karte hain.
- Dependency Injection:
  `main.py` faisla karta hai ke konsi repository initialize karke use cases ko deni hai.
=============================================================================
"""

# ---------------------------------------------------------------------------
# LIBRARIES / IMPORTS (Kyun aur kis liye import ki gayi hain):
# ---------------------------------------------------------------------------
# 'ABC, abstractmethod': Abstract Base Class banane ke liye, taake Python enforce kare
# ke jo bhi class is interface ko inherit karegi usko yeh methods lazmi implement karne honge.
from abc import ABC, abstractmethod

# 'List, Optional': Type hints ke liye (list of entities ya single entity jo None bhi ho sakti hai).
from typing import List, Optional

# ENTITY IMPORT: Repository methods TodoItem objects ko save aur return karte hain.
from .entities import TodoItem


# ---------------------------------------------------------------------------
# REPOSITORY INTERFACE / PORT:
# ---------------------------------------------------------------------------
class ITodoRepository(ABC):
    """
    Kyun banaya gaya:
    - Database operations ka formal contract / port define karne ke liye.

    Methods:
    - save: TodoItem ko database/storage mein store ya update karta hai.
    - get_by_id: ID ke zariye TodoItem dhoond kar lata hai (agar na mile toh None).
    - get_all: Tamam TodoItems ki list return karta hai.
    """

    @abstractmethod
    def save(self, todo: TodoItem) -> None:
        """TodoItem aggregate ko persistence storage mein save ya update karta hai."""
        pass

    @abstractmethod
    def get_by_id(self, todo_id: str) -> Optional[TodoItem]:
        """Specific ID ke TodoItem ko dhoondta hai; agar na mile toh None deta hai."""
        pass

    @abstractmethod
    def get_all(self) -> List[TodoItem]:
        """Tamam TodoItems ko fetch karke list ki shakal mein return karta hai."""
        pass
