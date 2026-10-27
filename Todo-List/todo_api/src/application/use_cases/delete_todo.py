"""Use case for deleting one user-owned todo."""

from src.application.dtos import DeleteTodoCommand
from src.domain.exceptions import TodoNotFoundError
from src.domain.repositories import ITodoRepository
from src.shared.console import print_error, print_step


class DeleteTodoUseCase:
    def __init__(self, todo_repo: ITodoRepository):
        self.todo_repo = todo_repo

    def execute(self, command: DeleteTodoCommand) -> None:
        todo = self.todo_repo.get_by_id(command.todo_id, command.owner_uid)

        if not todo:
            print_error(
                "Application",
                "Todo was not found for this user.",
                "Is user ka todo nahi mila.",
            )
            raise TodoNotFoundError(
                f"Todo with ID '{command.todo_id}' was not found."
            )

        self.todo_repo.delete(command.todo_id, command.owner_uid)
        print_step(
            "Application",
            f"Todo {command.todo_id} deleted.",
            f"Todo {command.todo_id} delete ho gaya.",
        )
