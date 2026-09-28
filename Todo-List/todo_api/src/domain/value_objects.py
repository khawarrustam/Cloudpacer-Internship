from dataclasses import dataclass
from enum import Enum
from src.domain.exceptions import InvalidTaskTitleError


class Priority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


@dataclass(frozen=True)
class TaskTitle:
    value: str

    def __post_init__(self):
        clean = self.value.strip() if self.value else ""
        if len(clean) < 3:
            raise InvalidTaskTitleError("Title must be at least 3 characters long.")
        if len(clean) > 120:
            raise InvalidTaskTitleError("Title cannot exceed 120 characters.")
        object.__setattr__(self, "value", clean)
