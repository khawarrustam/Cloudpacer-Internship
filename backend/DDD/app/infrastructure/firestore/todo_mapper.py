"""Map TodoItem entities to and from Firestore REST documents."""

from datetime import datetime

from app.domain.reminder import ReminderSettings
from app.domain.todo import Priority, TaskTitle, TodoItem


def todo_to_document(todo: TodoItem) -> dict:
    """Convert one TodoItem into Firestore's typed REST fields."""
    values = {
        "id": todo.id,
        "title": todo.title.value,
        "priority": todo.priority.value,
        "is_completed": todo.is_completed,
        "created_at": todo.created_at.isoformat(),
        "completed_at": _optional_iso(todo.completed_at),
        "owner_uid": todo.owner_uid,
        "due_at": _optional_iso(todo.reminder.due_at),
        "reminder_at": _optional_iso(todo.reminder.reminder_at),
        "reminder_email": todo.reminder.recipient_email,
        "reminder_sent_at": _optional_iso(todo.reminder.sent_at),
        "reminder_option": todo.reminder.option.value,
    }
    return {"fields": {key: _encode(value) for key, value in values.items()}}


def document_to_todo(document: dict) -> TodoItem:
    """Convert Firestore REST fields back into a domain TodoItem."""
    values = {
        key: _decode(value)
        for key, value in document.get("fields", {}).items()
    }
    return TodoItem(
        id=values["id"],
        title=TaskTitle(values["title"]),
        priority=Priority(values["priority"]),
        is_completed=values["is_completed"],
        created_at=datetime.fromisoformat(values["created_at"]),
        completed_at=_optional_datetime(values.get("completed_at")),
        owner_uid=values["owner_uid"],
        reminder=ReminderSettings.restore(
            due_at=_optional_datetime(values.get("due_at")),
            reminder_at=_optional_datetime(values.get("reminder_at")),
            recipient_email=values.get("reminder_email"),
            sent_at=_optional_datetime(values.get("reminder_sent_at")),
            option=values.get("reminder_option"),
        ),
    )


def _encode(value) -> dict:
    """Convert one Python value into Firestore REST format."""
    # Bool int ka subclass hai, isliye type order important hai.
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


def _optional_iso(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def _optional_datetime(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None
