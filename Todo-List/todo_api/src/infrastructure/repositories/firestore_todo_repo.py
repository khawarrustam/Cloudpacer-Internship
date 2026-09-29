"""
=============================================================================
INFRASTRUCTURE LAYER — Firestore Repository Adapter (Clean Architecture)
=============================================================================
Yeh class `FirestoreTodoRepository` hamara Cloud Database Adapter hai:
- Yeh Domain layer ke contract `ITodoRepository` ko Google Cloud Firestore ke sath
  implement karta hai.
- Yeh Domain Entities (`TodoItem`) aur Firestore Documents (Python dictionaries)
  ke darmiyan translation (Mapping/Hydration) ka kaam karti hai.

Clean Architecture Rule:
- Domain layer ko Firestore ke baare mein kuch nahi pata. Firestore ki saari details
  isi file ke andar band (encapsulated) hain.

Kahan Connected Hai:
- Implements: `src/domain/repositories.py` ka `ITodoRepository`.
- Instantiation: `main.py` isay Firestore client (`db`) pass karke initialize karta hai.
=============================================================================
"""

# ---------------------------------------------------------------------------
# LIBRARIES / IMPORTS (Kyun aur kis liye import ki gayi hain):
# ---------------------------------------------------------------------------
# 'typing': List (collection of todos) aur Optional (item exist kare ya None ho).
from typing import List, Optional

# 'datetime': Firestore ke ISO strings aur Python ke datetime objects ke darmiyan conversion ke liye.
from datetime import datetime

# 'google.cloud.firestore': Google Cloud Firestore ka client type hint aur database operations ke liye.
from google.cloud import firestore

# DOMAIN ENTITY & VALUE OBJECTS: Firestore document se domain entity construct karne ke liye.
from src.domain.entities import TodoItem
from src.domain.value_objects import TaskTitle, Priority

# REPOSITORY INTERFACE: Abstract contract jisko yeh class satisfy karti hai.
from src.domain.repositories import ITodoRepository


# ---------------------------------------------------------------------------
# FIRESTORE REPOSITORY ADAPTER:
# ---------------------------------------------------------------------------
class FirestoreTodoRepository(ITodoRepository):
    """
    Kyun banaya gaya:
    - Production-ready cloud database storage provider jo Firestore par data persist karta hai.
    """

    def __init__(self, db: firestore.Client, collection_name: str = "todos"):
        """
        Kyun use ho raha hai:
        - Firestore client receive karta hai aur target collection ("todos") ka reference save karta hai.
        """
        self.collection = db.collection(collection_name)

    def _to_entity(self, doc_data: dict) -> TodoItem:
        """
        Kyun use ho raha hai:
        - Mapper / Hydration: Firestore document dictionary ko Domain Entity (`TodoItem`) mein tabdeel karta hai.

        Kaise kaam karta hai:
        1. String timestamps (`created_at`, `completed_at`) ko `datetime` objects mein parse karta hai.
        2. Plain strings ko Domain Value Objects (`TaskTitle`, `Priority`) mein wrap karta hai.
        3. Validated `TodoItem` aggregate object return karta hai.
        """
        created_at = doc_data["created_at"]
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        completed_at = doc_data.get("completed_at")
        if isinstance(completed_at, str):
            completed_at = datetime.fromisoformat(completed_at)

        return TodoItem(
            id=doc_data["id"],
            title=TaskTitle(doc_data["title"]),
            priority=Priority(doc_data["priority"]),
            is_completed=doc_data["is_completed"],
            created_at=created_at,
            completed_at=completed_at,
        )

    def _to_document(self, todo: TodoItem) -> dict:
        """
        Kyun use ho raha hai:
        - Serializer: Domain Entity (`TodoItem`) ko plain Firestore dictionary mein convert karta hai.

        Kaise kaam karta hai:
        - Entity ke attributes ko primitive JSON-compatible types (strings, booleans) mein nikaal kar dictionary banata hai.
        """
        return {
            "id": todo.id,
            "title": todo.title.value,
            "priority": todo.priority.value,
            "is_completed": todo.is_completed,
            "created_at": todo.created_at.isoformat(),
            "completed_at": (
                todo.completed_at.isoformat() if todo.completed_at else None
            ),
        }

    def save(self, todo: TodoItem) -> None:
        """
        Kyun use ho raha hai:
        - Domain entity ko document bana kar Firestore collection mein save (.set()) karta hai.
        """
        self.collection.document(todo.id).set(self._to_document(todo))

    def get_by_id(self, todo_id: str) -> Optional[TodoItem]:
        """
        Kyun use ho raha hai:
        - Firestore se specific ID ka document mangwata hai.
        - Agar document na mile toh `None` deta hai, agar mil jaye toh `_to_entity` ke zariye entity bana kar deta hai.
        """
        doc = self.collection.document(todo_id).get()
        if not doc.exists:
            return None
        return self._to_entity(doc.to_dict())

    def get_all(self) -> List[TodoItem]:
        """
        Kyun use ho raha hai:
        - Firestore collection ke saare documents stream karta hai aur sab ko `TodoItem` entities ki list mein convert karta hai.
        """
        docs = self.collection.stream()
        return [self._to_entity(doc.to_dict()) for doc in docs]
