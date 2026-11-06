"""MongoDB todo infrastructure."""

from datetime import datetime

from pymongo import MongoClient

from src.domain.models import Priority, TaskTitle, TodoItem, TodoRepository
from src.logs import log_step


class MongoTodoRepository(TodoRepository):
    """Store todos as simple MongoDB documents."""

    def __init__(self, uri: str, database_name: str, collection_name: str):
        """Connect to MongoDB and select the todo collection.

        Startup ping wrong URI ko early detect karta hai. owner_uid index each
        user's todo list ko faster banata hai.
        """
        self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        self.client.admin.command("ping")
        self.collection = self.client[database_name][collection_name]
        self.collection.create_index("owner_uid")

    @staticmethod
    def _to_document(todo: TodoItem) -> dict:
        """Convert a TodoItem into one MongoDB document."""
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
        """Convert a MongoDB document back into a TodoItem."""
        return TodoItem(
            id=str(document["_id"]),
            title=TaskTitle(document["title"]),
            priority=Priority(document["priority"]),
            is_completed=document["is_completed"],
            created_at=datetime.fromisoformat(document["created_at"]),
            completed_at=(
                datetime.fromisoformat(document["completed_at"])
                if document.get("completed_at")
                else None
            ),
            owner_uid=document["owner_uid"],
        )

    def save(self, todo: TodoItem) -> None:
        """Create a new todo or replace its saved MongoDB document."""
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
        """Find a todo only when its ID and owner both match."""
        document = self.collection.find_one({
            "_id": todo_id,
            "owner_uid": owner_uid,
        })
        message = "found the todo" if document else "did not find the todo"
        roman_urdu = "todo mil gaya" if document else "todo nahi mila"
        log_step(
            "Infrastructure",
            f"MongoDB {message}.",
            f"MongoDB ko {roman_urdu}.",
        )
        return self._to_entity(document) if document else None

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
