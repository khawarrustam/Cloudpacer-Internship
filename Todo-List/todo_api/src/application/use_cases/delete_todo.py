"""Application use case for deleting a user-owned todo."""

from src.application.dtos import DeleteTodoCommand
from src.domain.exceptions import TodoNotFoundError
from src.domain.repositories import ITodoRepository


class DeleteTodoUseCase:
    def __init__(self, todo_repo: ITodoRepository):
        self.todo_repo = todo_repo

    def execute(self, cmd: DeleteTodoCommand) -> None:
        todo = self.todo_repo.get_by_id(cmd.todo_id, cmd.owner_uid)
        if not todo:
            raise TodoNotFoundError(f"Todo with ID '{cmd.todo_id}' was not found.")

        self.todo_repo.delete(cmd.todo_id, cmd.owner_uid)
