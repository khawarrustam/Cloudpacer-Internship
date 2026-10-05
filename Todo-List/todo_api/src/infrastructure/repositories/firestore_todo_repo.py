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
        print(f"   🗄️  Collection: '{collection_name}' (Nested under users/UID)")
        self.db = db
        self.collection_name = collection_name

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
            owner_uid=doc_data.get("owner_uid", ""),
            completed_at=completed_at,
        )

    def _to_document(self, todo: TodoItem) -> dict:
        """Serializer: Domain Entity → Firestore dict"""
        return {
            "id": todo.id,
            "title": todo.title.value,
            "priority": todo.priority.value,
            "is_completed": todo.is_completed,
            "owner_uid": todo.owner_uid,
            "created_at": todo.created_at.isoformat(),
            "completed_at": (
                todo.completed_at.isoformat() if todo.completed_at else None
            ),
        }

    def save(self, todo: TodoItem) -> None:
        print(f"   📂 File    : src/infrastructure/repositories/firestore_todo_repo.py")
        print(f"   🔧 Function: FirestoreTodoRepository.save()")
        print(f"   🏛️  Layer   : INFRASTRUCTURE LAYER")

        doc_data = self._to_document(todo)
        
        if todo.owner_uid:
            print(f"   🗄️  Action  : Firestore.collection('users').document('{todo.owner_uid}').collection('{self.collection_name}').document('{todo.id}').set(data)")
            self.db.collection("users").document(todo.owner_uid).collection(self.collection_name).document(todo.id).set(doc_data)
        else:
            print(f"   🗄️  Action  : Firestore.collection('{self.collection_name}').document('{todo.id}').set(data)")
            self.db.collection(self.collection_name).document(todo.id).set(doc_data)

        print(f"   ✅ Firestore .set() completed for document id='{todo.id}'")

    def get_by_id(self, todo_id: str) -> Optional[TodoItem]:
        print(f"   📂 File    : src/infrastructure/repositories/firestore_todo_repo.py")
        print(f"   🔧 Function: FirestoreTodoRepository.get_by_id()")
        print(f"   🏛️  Layer   : INFRASTRUCTURE LAYER")
        print(f"   🗄️  Action  : Firestore.collection_group('{self.collection_name}').where('id', '==', '{todo_id}').stream()")

        # Collection group query handles both top-level todos and nested users/{uid}/todos
        docs = self.db.collection_group(self.collection_name).where("id", "==", todo_id).stream()
        
        for doc in docs:
            print(f"   ✅ Firestore: Document found! Hydrating via _to_entity()")
            return self._to_entity(doc.to_dict())

        print(f"   ❌ Firestore: Document '{todo_id}' does NOT exist → returning None")
        return None

    def get_all(self) -> List[TodoItem]:
        print(f"   📂 File    : src/infrastructure/repositories/firestore_todo_repo.py")
        print(f"   🔧 Function: FirestoreTodoRepository.get_all()")
        print(f"   🏛️  Layer   : INFRASTRUCTURE LAYER")
        print(f"   🗄️  Action  : Firestore.collection_group('{self.collection_name}').stream() — fetching all docs")

        docs = self.db.collection_group(self.collection_name).stream()
        entities = [self._to_entity(doc.to_dict()) for doc in docs]

        print(f"   ✅ Firestore returned {len(entities)} document(s), hydrated to entities")

        return entities

    def get_by_owner(self, owner_uid: str) -> List[TodoItem]:
        print(f"   📂 File    : src/infrastructure/repositories/firestore_todo_repo.py")
        print(f"   🔧 Function: FirestoreTodoRepository.get_by_owner()")
        print(f"   🏛️  Layer   : INFRASTRUCTURE LAYER")
        print(f"   🗄️  Action  : Firestore.collection('users').document('{owner_uid}').collection('{self.collection_name}').stream()")

        docs = self.db.collection("users").document(owner_uid).collection(self.collection_name).stream()
        entities = [self._to_entity(doc.to_dict()) for doc in docs]

        print(f"   ✅ Firestore returned {len(entities)} document(s) for user '{owner_uid}'")
        return entities
