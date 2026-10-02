"""
=============================================================================
INFRASTRUCTURE LAYER — Firestore Repository Adapter (Clean Architecture)
=============================================================================
"""

from typing import List, Optional
from datetime import datetime
from google.cloud import firestore

from src.domain.entities import TodoItem
from src.domain.value_objects import TaskTitle, Priority
from src.domain.repositories import ITodoRepository


class FirestoreTodoRepository(ITodoRepository):

    def __init__(self, db: firestore.Client, collection_name: str = "todos"):
        print(f"   📂 File    : src/infrastructure/repositories/firestore_todo_repo.py")
        print(f"   🔧 Function: FirestoreTodoRepository.__init__()")
        print(f"   🏛️  Layer   : INFRASTRUCTURE LAYER (Firestore Adapter)")
        print(f"   🗄️  Collection: '{collection_name}'")
        self.collection = db.collection(collection_name)

    def _to_entity(self, doc_data: dict) -> TodoItem:
        """Mapper: Firestore dict → Domain Entity"""
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
        """Serializer: Domain Entity → Firestore dict"""
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
        print(f"   📂 File    : src/infrastructure/repositories/firestore_todo_repo.py")
        print(f"   🔧 Function: FirestoreTodoRepository.save()")
        print(f"   🏛️  Layer   : INFRASTRUCTURE LAYER")
        print(f"   🗄️  Action  : Firestore.collection('todos').document('{todo.id}').set(data)")
        print(f"              Serializing Entity → Dict via _to_document()")

        doc_data = self._to_document(todo)
        self.collection.document(todo.id).set(doc_data)

        print(f"   ✅ Firestore .set() completed for document id='{todo.id}'")

    def get_by_id(self, todo_id: str) -> Optional[TodoItem]:
        print(f"   📂 File    : src/infrastructure/repositories/firestore_todo_repo.py")
        print(f"   🔧 Function: FirestoreTodoRepository.get_by_id()")
        print(f"   🏛️  Layer   : INFRASTRUCTURE LAYER")
        print(f"   🗄️  Action  : Firestore.collection('todos').document('{todo_id}').get()")

        doc = self.collection.document(todo_id).get()

        if not doc.exists:
            print(f"   ❌ Firestore: Document '{todo_id}' does NOT exist → returning None")
            return None

        print(f"   ✅ Firestore: Document found! Hydrating via _to_entity()")
        return self._to_entity(doc.to_dict())

    def get_all(self) -> List[TodoItem]:
        print(f"   📂 File    : src/infrastructure/repositories/firestore_todo_repo.py")
        print(f"   🔧 Function: FirestoreTodoRepository.get_all()")
        print(f"   🏛️  Layer   : INFRASTRUCTURE LAYER")
        print(f"   🗄️  Action  : Firestore.collection('todos').stream() — fetching all docs")

        docs = self.collection.stream()
        entities = [self._to_entity(doc.to_dict()) for doc in docs]

        print(f"   ✅ Firestore returned {len(entities)} document(s), hydrated to entities")

        return entities
