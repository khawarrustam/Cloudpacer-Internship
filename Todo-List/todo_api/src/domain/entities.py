"""
=============================================================================
DOMAIN LAYER — Entities
=============================================================================
Entities woh objects hotay hain jinki ek distinct identity (ID) hoti hai.
Bhalay unke baqi attributes change ho jayen, unki ID same rehti hai, isliye
unhe Entity kaha jata hai.

Kyun Zaroori Hain:
- Yeh application ka Core Business Logic aur Rules (Invariants) hold karte hain.
- Inhe bahar ki kisi layer (Database, API, UI) ka kuch pata nahi hota.
- Yeh apne state (data) ko khud manage karte hain taake data hamesha valid rahe.

Kahan Connected Hai:
- Use cases (jaise `CreateTodoUseCase`, `CompleteTodoUseCase`) in Entities ko
  create ya update karte hain.
- Repositories in Entities ko database mein save karte hain ya wahan se fetch karte hain.
=============================================================================
"""

# ---------------------------------------------------------------------------
# LIBRARIES / IMPORTS:
# ---------------------------------------------------------------------------
from dataclasses import dataclass
from datetime import datetime, timezone
import uuid

# Value Objects: Yeh chhotay objects hain jo validation rules carry karte hain.
from src.domain.value_objects import TaskTitle, Priority

# Domain Exceptions: Agar koi business rule toota toh yeh custom errors raise hotay hain.
from src.domain.exceptions import TaskAlreadyCompletedError

@dataclass
class TodoItem:
    """
    Aggregate Root: Yeh main Entity hai jo apne andar ke sub-components ko manage karti hai.
    Koi bahar ki class iske data ko direct modify na kare (bina rules follow kiye).
    """
    id: str
    title: TaskTitle
    priority: Priority
    is_completed: bool
    created_at: datetime
    owner_uid: str = ""        # Firebase user UID — empty string for legacy records
    completed_at: datetime | None = None

    @classmethod
    def create(cls, title: str, priority: Priority = Priority.MEDIUM, owner_uid: str = "") -> "TodoItem":
        """
        Factory method: Naya TodoItem bananane ka sahulati (helper) tarika.
        Isme naya ID auto-generate hota hai aur default values set hoti hain.
        """
        return cls(
            id=str(uuid.uuid4()),
            title=TaskTitle(title), # Title ki validation TaskTitle Value Object handle karega
            priority=priority,
            is_completed=False,
            created_at=datetime.now(timezone.utc),
            owner_uid=owner_uid,
            completed_at=None
        )

    def mark_as_completed(self) -> None:
        """
        Business Invariant (Rule): Ek task jo pehle se complete hai, 
        usey dobara complete nahi kiya ja sakta.
        Agar state valid hai toh status aur completed_at date update kar deta hai.
        """
        if self.is_completed:
            raise TaskAlreadyCompletedError(f"Todo with ID '{self.id}' is already completed.")
        self.is_completed = True
        self.completed_at = datetime.now(timezone.utc)