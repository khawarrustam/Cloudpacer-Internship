class DomainError(Exception):
    """Base class for all business rule violations."""


class InvalidTaskTitleError(DomainError):
    pass


class TaskAlreadyCompletedError(DomainError):
    pass


class TodoNotFoundError(DomainError):
    pass
