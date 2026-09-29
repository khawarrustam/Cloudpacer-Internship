from dataclasses import dataclass
from datetime import datetime, timezone
import uuid
from src.domain.value_objects import TaskTitle, Priority
from src.domain.exceptions import TaskAlreadyCompletedError

@dataclass
class TodoItem:
    """Aggregate Root: Enforces all business invariants on a Todo."""
    id: str
    title: TaskTitle
    priority: Priority
    is_completed: bool
    created_at: datetime
    completed_at: datetime | None = None

    @classmethod
    def create(cls, title: str, priority: Priority = Priority.MEDIUM) -> "TodoItem":
        """Factory method: Validates inputs and creates a clean aggregate."""
        return cls(
            id=str(uuid.uuid4()),
            title=TaskTitle(title),
            priority=priority,
            is_completed=False,
            created_at=datetime.now(timezone.utc),
            completed_at=None
        )

    def mark_as_completed(self) -> None:
        """Business Invariant: Completed task cannot be completed again."""
        if self.is_completed:
            raise TaskAlreadyCompletedError(f"Todo with ID '{self.id}' is already completed.")
        self.is_completed = True
        self.completed_at = datetime.now(timezone.utc)