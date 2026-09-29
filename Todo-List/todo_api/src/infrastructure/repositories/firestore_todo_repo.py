from typing import List, Optional
from datetime import datetime
from google.cloud import firestore
from src.domain.entities import TodoItem
from src.domain.value_objects import TaskTitle, Priority
from src.domain.repositories import ITodoRepository


class FirestoreTodoRepository(ITodoRepository):
    def __init__(self, db: firestore.Client, collection_name: str = "todos"):
        self.collection = db.collection(collection_name)

    def _to_entity(self, doc_data: dict) -> TodoItem:
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
        self.collection.document(todo.id).set(self._to_document(todo))

    def get_by_id(self, todo_id: str) -> Optional[TodoItem]:
        doc = self.collection.document(todo_id).get()
        if not doc.exists:
            return None
        return self._to_entity(doc.to_dict())

    def get_all(self) -> List[TodoItem]:
        docs = self.collection.stream()
        return [self._to_entity(doc.to_dict()) for doc in docs]
