"""Todo entity and its business rules.

English: The domain does not know about FastAPI or Firebase.
Roman Urdu: Domain ko FastAPI ya Firebase ka pata nahi hota.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
import uuid

from src.domain.exceptions import TaskAlreadyCompletedError
from src.domain.value_objects import Priority, TaskTitle


@dataclass
class TodoItem:
    """Main business object for one todo."""

    id: str
    title: TaskTitle
    priority: Priority
    is_completed: bool
    created_at: datetime
    owner_uid: str = ""
    completed_at: datetime | None = None

    @classmethod
    def create(
        cls,
        title: str,
        priority: Priority = Priority.MEDIUM,
        owner_uid: str = "",
    ) -> "TodoItem":
        """Create a new valid todo with an id and time."""
        return cls(
            id=str(uuid.uuid4()),
            title=TaskTitle(title),
            priority=priority,
            is_completed=False,
            created_at=datetime.now(timezone.utc),
            owner_uid=owner_uid,
            completed_at=None,
        )

    def mark_as_completed(self) -> None:
        """Complete the todo once; completing it twice is not allowed."""
        if self.is_completed:
            raise TaskAlreadyCompletedError(
                f"Todo with ID '{self.id}' is already completed."
            )

        self.is_completed = True
        self.completed_at = datetime.now(timezone.utc)
