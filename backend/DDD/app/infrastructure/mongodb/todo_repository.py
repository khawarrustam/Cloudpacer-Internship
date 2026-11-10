"""MongoDB implementation of the todo repository contract."""

from datetime import datetime

from pymongo.collection import Collection

from app.domain.todo import Priority, TaskTitle, TodoItem, TodoRepository
from app.logging import log_step


class MongoTodoRepository(TodoRepository):
    """What: Persist TodoItem entities as MongoDB documents.

    When: MongoDB is the selected application database.
    How: Use one collection with owner_uid filtering and an owner index.
    """

    def __init__(self, collection: Collection) -> None:
        self.collection = collection
        self.collection.create_index("owner_uid")

    def save(self, todo: TodoItem) -> None:
        """Create a todo or replace its saved MongoDB document."""
        self.collection.replace_one(
            {"_id": todo.id},
            self._to_document(todo),
            upsert=True,
        )
        log_step(
            "Infrastructure",
            "Saved todo in MongoDB.",
            "Todo MongoDB mein save hua.",
        )

    def get_by_id(self, todo_id: str, owner_uid: str) -> TodoItem | None:
        """Find a todo only when ID and owner both match."""
        document = self.collection.find_one({
            "_id": todo_id,
            "owner_uid": owner_uid,
        })
        if document is None:
            log_step(
                "Infrastructure",
                "MongoDB did not find the todo.",
                "MongoDB ko todo nahi mila.",
            )
            return None
        log_step(
            "Infrastructure",
            "MongoDB found the todo.",
            "MongoDB ko todo mil gaya.",
        )
        return self._to_entity(document)

    def get_by_owner(self, owner_uid: str) -> list[TodoItem]:
        """Return all MongoDB todos for one user."""
        documents = list(self.collection.find({"owner_uid": owner_uid}))
        log_step(
            "Infrastructure",
            f"MongoDB returned {len(documents)} todo(s).",
            f"MongoDB ne {len(documents)} todo diye.",
        )
        return [self._to_entity(document) for document in documents]

    def delete(self, todo_id: str, owner_uid: str) -> None:
        """Delete a todo only when it belongs to the current user."""
        self.collection.delete_one({"_id": todo_id, "owner_uid": owner_uid})
        log_step(
            "Infrastructure",
            "Deleted todo from MongoDB.",
            "Todo MongoDB se delete hua.",
        )

    @staticmethod
    def _to_document(todo: TodoItem) -> dict:
        """Convert TodoItem into one MongoDB document."""
        return {
            "_id": todo.id,
            "title": todo.title.value,
            "priority": todo.priority.value,
            "is_completed": todo.is_completed,
            "created_at": todo.created_at.isoformat(),
            "completed_at": (
                todo.completed_at.isoformat() if todo.completed_at else None
            ),
            "owner_uid": todo.owner_uid,
        }

    @staticmethod
    def _to_entity(document: dict) -> TodoItem:
        """Convert one MongoDB document back into TodoItem."""
        completed_at = None
        if document.get("completed_at"):
            completed_at = datetime.fromisoformat(document["completed_at"])
        return TodoItem(
            id=str(document["_id"]),
            title=TaskTitle(document["title"]),
            priority=Priority(document["priority"]),
            is_completed=document["is_completed"],
            created_at=datetime.fromisoformat(document["created_at"]),
            completed_at=completed_at,
            owner_uid=document["owner_uid"],
        )
