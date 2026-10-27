"""Small domain values that validate themselves.

English: A value object keeps one business value valid.
Roman Urdu: Value object aik business value ko valid rakhta hai.
"""

from dataclasses import dataclass
from enum import Enum

from src.domain.exceptions import InvalidTaskTitleError


class Priority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


@dataclass(frozen=True)
class TaskTitle:
    """A cleaned todo title between 3 and 120 characters."""

    value: str

    def __post_init__(self):
        clean_value = self.value.strip() if self.value else ""

        if len(clean_value) < 3:
            raise InvalidTaskTitleError(
                "Title must be at least 3 characters long."
            )

        if len(clean_value) > 120:
            raise InvalidTaskTitleError(
                "Title cannot exceed 120 characters."
            )

        # English: frozen objects need object.__setattr__ during setup.
        # Roman Urdu: frozen object mein setup ke waqt yeh method value set karta hai.
        object.__setattr__(self, "value", clean_value)
