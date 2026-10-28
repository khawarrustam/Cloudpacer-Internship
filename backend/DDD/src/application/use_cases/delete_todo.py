"""Use case for deleting one user-owned todo."""

from src.application.dtos import DeleteTodoCommand
from src.domain.exceptions import TodoNotFoundError
from src.domain.repositories import ITodoRepository
from src.shared.console import module_file, print_error, print_flow, print_step


class DeleteTodoUseCase:
    def __init__(self, todo_repo: ITodoRepository):
        self.todo_repo = todo_repo

    def execute(self, command: DeleteTodoCommand) -> None:
        print_flow(
            source="src/presentation/api/todo_router.py",
            destination="src/application/use_cases/delete_todo.py",
            data=f"todo_id={command.todo_id}, owner_uid={command.owner_uid}",
            english="The router sent a delete command to the use case.",
            roman_urdu="Router ne delete command use case ko bheji.",
        )
        print_flow(
            source="src/application/use_cases/delete_todo.py",
            destination=module_file(self.todo_repo),
            data=f"todo_id={command.todo_id}",
            english="Checking that the todo belongs to this user.",
            roman_urdu="Check ho raha hai ke todo isi user ka hai.",
        )
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

        print_flow(
            source="src/application/use_cases/delete_todo.py",
            destination=module_file(self.todo_repo),
            data=f"todo_id={command.todo_id}",
            english="Sending the confirmed todo id for deletion.",
            roman_urdu="Confirm todo id delete honay ke liye ja rahi hai.",
        )
        self.todo_repo.delete(command.todo_id, command.owner_uid)
        print_step(
            "Application",
            f"Todo {command.todo_id} deleted.",
            f"Todo {command.todo_id} delete ho gaya.",
        )
