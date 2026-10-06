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
from google.cloud.firestore_v1.base_query import FieldFilter


class FirestoreTodoRepository(ITodoRepository):

    def __init__(self, db: firestore.Client, collection_name: str = "todos"):
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
        doc_data = self._to_document(todo)
        
        # ALWAYS save under the user's specific sub-collection to ensure isolation
        if todo.owner_uid:
            self.db.collection("users").document(todo.owner_uid).collection(self.collection_name).document(todo.id).set(doc_data)
        else:
            # Fallback for system tasks (if any)
            self.db.collection(self.collection_name).document(todo.id).set(doc_data)

    def get_by_id(self, todo_id: str) -> Optional[TodoItem]:
        # Use collection_group but we will verify ownership in the Use Case/Router
        docs = self.db.collection_group(self.collection_name).where(filter=FieldFilter("id", "==", todo_id)).stream()

        for doc in docs:
            return self._to_entity(doc.to_dict())

        return None

    def get_all(self) -> List[TodoItem]:
        """
        DANGER: This fetches EVERYTHING from all users. 
        Should only be used for administrative purposes.
        """
        docs = self.db.collection_group(self.collection_name).stream()
        return [self._to_entity(doc.to_dict()) for doc in docs]

    def get_by_owner(self, owner_uid: str) -> List[TodoItem]:
        """
        SECURE: Fetches tasks ONLY from the specific user's sub-collection.
        """
        docs = self.db.collection("users").document(owner_uid).collection(self.collection_name).stream()
        return [self._to_entity(doc.to_dict()) for doc in docs]
