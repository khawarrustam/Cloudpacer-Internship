"""MongoDB implementation of the todo repository contract."""

from datetime import datetime

from pymongo.collection import Collection

from app.domain.reminder import ReminderSettings
from app.domain.todo import Priority, TaskTitle, TodoItem, TodoRepository
from app.logging import log_step


class MongoTodoRepository(TodoRepository):
    """What: Persist TodoItem entities as MongoDB documents.

    When: MongoDB is the selected application database.
    How: Use one collection with owner_uid filtering and an owner index.
    """

    def __init__(self, collection: Collection) -> None:
        self.collection = collection
        # User todo-list filter ko faster banane ke liye owner field indexed hai.
        self.collection.create_index("owner_uid")
        # Worker due, incomplete aur unsent reminders isi index se filter karta hai.
        self.collection.create_index([
            ("reminder_at", 1),
            ("is_completed", 1),
            ("reminder_sent_at", 1),
        ])

    def save(self, todo: TodoItem) -> None:
        """Create a todo or replace its saved MongoDB document."""
        # Upsert missing ID par insert aur existing ID par latest full state replace karta hai.
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
        # ID akela enough nahi: owner filter authorization ko DB query tak carry karta hai.
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

    def get_due_reminders(
        self,
        now: datetime,
        limit: int,
    ) -> list[TodoItem]:
        """Return a limited batch of due, incomplete MongoDB reminders."""
        documents = self.collection.find({
            "is_completed": False,
            "reminder_at": {"$ne": None, "$lte": now.isoformat()},
            "reminder_sent_at": None,
        }).sort("reminder_at", 1).limit(limit)
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
            "due_at": _optional_iso(todo.reminder.due_at),
            "reminder_at": _optional_iso(todo.reminder.reminder_at),
            "reminder_email": todo.reminder.recipient_email,
            "reminder_sent_at": _optional_iso(todo.reminder.sent_at),
            "reminder_option": todo.reminder.option.value,
        }

    @staticmethod
    def _to_entity(document: dict) -> TodoItem:
        """Convert one MongoDB document back into TodoItem."""
        # Restore ke waqt domain value objects stored values ko dobara validate karte hain.
        completed_at = None
        if document.get("completed_at"):
            completed_at = datetime.fromisoformat(document["completed_at"])
        reminder = ReminderSettings.restore(
            due_at=_optional_datetime(document.get("due_at")),
            reminder_at=_optional_datetime(document.get("reminder_at")),
            recipient_email=document.get("reminder_email"),
            sent_at=_optional_datetime(document.get("reminder_sent_at")),
            option=document.get("reminder_option"),
        )
        return TodoItem(
            id=str(document["_id"]),
            title=TaskTitle(document["title"]),
            priority=Priority(document["priority"]),
            is_completed=document["is_completed"],
            created_at=datetime.fromisoformat(document["created_at"]),
            completed_at=completed_at,
            owner_uid=document["owner_uid"],
            reminder=reminder,
        )


def _optional_iso(value: datetime | None) -> str | None:
    """Serialize an optional datetime for simple MongoDB documents."""
    return value.isoformat() if value else None


def _optional_datetime(value: str | None) -> datetime | None:
    """Restore an optional ISO datetime."""
    return datetime.fromisoformat(value) if value else None
