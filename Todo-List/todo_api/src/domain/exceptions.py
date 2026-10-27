"""Business errors used by the domain and application layers.

English: Named errors make failed business rules easy to understand.
Roman Urdu: Named errors se business rule ki ghalti asaani se samajh aati hai.
"""


class DomainError(Exception):
    """Base class for all todo business errors."""


class InvalidTaskTitleError(DomainError):
    """Raised when a todo title is too short or too long."""


class TaskAlreadyCompletedError(DomainError):
    """Raised when a completed todo is completed again."""


class TodoNotFoundError(DomainError):
    """Raised when a requested todo is not available for the user."""


class ValidationException(DomainError):
    """Raised when Firebase rejects authentication data."""
