"""Firestore implementation of the todo repository.

English: This adapter translates domain objects to Firestore documents.
Roman Urdu: Yeh adapter domain object ko Firestore document mein badalta hai.
"""

from datetime import datetime
from typing import List, Optional

from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from src.domain.entities import TodoItem
from src.domain.repositories import ITodoRepository
from src.domain.value_objects import Priority, TaskTitle


class FirestoreTodoRepository(ITodoRepository):
    def __init__(
        self,
        db: firestore.Client,
        collection_name: str = "todos",
    ):
        self.db = db
        self.collection_name = collection_name

    def _to_entity(self, data: dict) -> TodoItem:
        created_at = data["created_at"]
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        completed_at = data.get("completed_at")
        if isinstance(completed_at, str):
            completed_at = datetime.fromisoformat(completed_at)

        return TodoItem(
            id=data["id"],
            title=TaskTitle(data["title"]),
            priority=Priority(data["priority"]),
            is_completed=data["is_completed"],
            created_at=created_at,
            owner_uid=data.get("owner_uid", ""),
            completed_at=completed_at,
        )

    def _to_document(self, todo: TodoItem) -> dict:
        return {
            "id": todo.id,
            "title": todo.title.value,
            "priority": todo.priority.value,
            "is_completed": todo.is_completed,
            "owner_uid": todo.owner_uid,
            "created_at": todo.created_at.isoformat(),
            "completed_at": (
                todo.completed_at.isoformat()
                if todo.completed_at
                else None
            ),
        }

    def _user_collection(self, owner_uid: str):
        return (
            self.db.collection("users")
            .document(owner_uid)
            .collection(self.collection_name)
        )

    def save(self, todo: TodoItem) -> None:
        document = self._to_document(todo)

        if todo.owner_uid:
            self._user_collection(todo.owner_uid).document(todo.id).set(
                document
            )
            return

        self.db.collection(self.collection_name).document(todo.id).set(
            document
        )

    def get_by_id(
        self,
        todo_id: str,
        owner_uid: str = "",
    ) -> Optional[TodoItem]:
        if owner_uid:
            snapshot = self._user_collection(owner_uid).document(todo_id).get()
            return (
                self._to_entity(snapshot.to_dict())
                if snapshot.exists
                else None
            )

        # English: Unscoped lookup is only for trusted admin work.
        # Roman Urdu: Owner ke baghair lookup sirf trusted admin kaam ke liye hai.
        documents = (
            self.db.collection_group(self.collection_name)
            .where(filter=FieldFilter("id", "==", todo_id))
            .stream()
        )

        for document in documents:
            return self._to_entity(document.to_dict())

        return None

    def get_all(self) -> List[TodoItem]:
        documents = self.db.collection_group(self.collection_name).stream()
        return [
            self._to_entity(document.to_dict())
            for document in documents
        ]

    def get_by_owner(self, owner_uid: str) -> List[TodoItem]:
        documents = self._user_collection(owner_uid).stream()
        return [
            self._to_entity(document.to_dict())
            for document in documents
        ]

    def delete(self, todo_id: str, owner_uid: str = "") -> None:
        if owner_uid:
            self._user_collection(owner_uid).document(todo_id).delete()
            return

        todo = self.get_by_id(todo_id)
        if todo and todo.owner_uid:
            self._user_collection(todo.owner_uid).document(todo_id).delete()
        elif todo:
            self.db.collection(self.collection_name).document(todo_id).delete()
