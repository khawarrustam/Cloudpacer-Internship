"""Firestore implementation of the todo repository contract."""

from datetime import datetime
from urllib.parse import quote

from google.auth.transport.requests import AuthorizedSession

from app.domain.todo import Priority, TaskTitle, TodoItem, TodoRepository
from app.logging import log_step


class FirestoreTodoRepository(TodoRepository):
    """What: Persist TodoItem entities in Firestore.

    When: Firestore is the selected application database.
    How: Use Firestore's authenticated REST API and per-user subcollections.
    """

    def __init__(
        self,
        session: AuthorizedSession,
        documents_url: str,
        user_collection: str,
        todo_collection: str,
        page_size: int,
    ) -> None:
        self.session = session
        self.documents_url = documents_url
        self.user_collection = user_collection
        self.todo_collection = todo_collection
        self.page_size = page_size

    def save(self, todo: TodoItem) -> None:
        """Create or update one Firestore todo document."""
        response = self.session.patch(
            self._document_url(todo.owner_uid, todo.id),
            json=self._to_document(todo),
        )
        response.raise_for_status()
        log_step(
            "Infrastructure",
            "Saved todo in Firebase Firestore.",
            "Todo Firebase Firestore mein save hua.",
        )

    def get_by_id(self, todo_id: str, owner_uid: str) -> TodoItem | None:
        """Find one owned Firestore todo or return None."""
        response = self.session.get(self._document_url(owner_uid, todo_id))
        if response.status_code == 404:
            log_step(
                "Infrastructure",
                "Firebase Firestore did not find the todo.",
                "Firebase Firestore ko todo nahi mila.",
            )
            return None
        response.raise_for_status()
        log_step(
            "Infrastructure",
            "Firebase Firestore found the todo.",
            "Firebase Firestore ko todo mil gaya.",
        )
        return self._to_entity(response.json())

    def get_by_owner(self, owner_uid: str) -> list[TodoItem]:
        """Read all Firestore todos for one user, including every page."""
        documents = []
        page_token = None
        while True:
            params = {"pageSize": self.page_size}
            if page_token:
                params["pageToken"] = page_token
            response = self.session.get(
                self._collection_url(owner_uid),
                params=params,
            )
            response.raise_for_status()
            data = response.json()
            documents.extend(data.get("documents", []))
            page_token = data.get("nextPageToken")
            if not page_token:
                break

        log_step(
            "Infrastructure",
            f"Firestore returned {len(documents)} todo(s).",
            f"Firestore ne {len(documents)} todo diye.",
        )
        return [self._to_entity(document) for document in documents]

    def delete(self, todo_id: str, owner_uid: str) -> None:
        """Delete one user's todo document from Firestore."""
        response = self.session.delete(self._document_url(owner_uid, todo_id))
        if response.status_code != 404:
            response.raise_for_status()
        log_step(
            "Infrastructure",
            "Deleted todo from Firebase Firestore.",
            "Todo Firebase Firestore se delete hua.",
        )

    def _collection_url(self, owner_uid: str) -> str:
        """Build the current user's private todo collection URL."""
        users = quote(self.user_collection, safe="")
        owner = quote(owner_uid, safe="")
        todos = quote(self.todo_collection, safe="")
        return f"{self.documents_url}/{users}/{owner}/{todos}"

    def _document_url(self, owner_uid: str, todo_id: str) -> str:
        """Build the URL for one todo document."""
        return f"{self._collection_url(owner_uid)}/{quote(todo_id, safe='')}"

    @staticmethod
    def _to_document(todo: TodoItem) -> dict:
        """Convert TodoItem into Firestore REST fields."""
        values = {
            "id": todo.id,
            "title": todo.title.value,
            "priority": todo.priority.value,
            "is_completed": todo.is_completed,
            "created_at": todo.created_at.isoformat(),
            "completed_at": (
                todo.completed_at.isoformat() if todo.completed_at else None
            ),
            "owner_uid": todo.owner_uid,
        }
        fields = {key: _encode(value) for key, value in values.items()}
        return {"fields": fields}

    @staticmethod
    def _to_entity(document: dict) -> TodoItem:
        """Convert Firestore REST fields back into TodoItem."""
        values = {
            key: _decode(value)
            for key, value in document.get("fields", {}).items()
        }
        completed_at = None
        if values.get("completed_at"):
            completed_at = datetime.fromisoformat(values["completed_at"])
        return TodoItem(
            id=values["id"],
            title=TaskTitle(values["title"]),
            priority=Priority(values["priority"]),
            is_completed=values["is_completed"],
            created_at=datetime.fromisoformat(values["created_at"]),
            completed_at=completed_at,
            owner_uid=values["owner_uid"],
        )


def _encode(value) -> dict:
    """Convert one Python value into Firestore REST format."""
    if value is None:
        return {"nullValue": None}
    if isinstance(value, bool):
        return {"booleanValue": value}
    return {"stringValue": str(value)}


def _decode(value: dict):
    """Convert one Firestore REST value into a Python value."""
    if "nullValue" in value:
        return None
    if "booleanValue" in value:
        return value["booleanValue"]
    return value.get("stringValue", "")
