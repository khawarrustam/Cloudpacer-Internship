"""Use case for completing one todo."""

from src.application.dtos import CompleteTodoCommand, TodoDTO
from src.application.mappers import todo_to_dto
from src.domain.exceptions import TodoNotFoundError
from src.domain.repositories import ITodoRepository
from src.shared.console import print_error, print_step


class CompleteTodoUseCase:
    def __init__(self, todo_repo: ITodoRepository):
        self.todo_repo = todo_repo

    def execute(self, command: CompleteTodoCommand) -> TodoDTO:
        print_step(
            "Application",
            f"Finding todo {command.todo_id}.",
            f"Todo {command.todo_id} dhoonda ja raha hai.",
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

        # English: The entity protects the rule against completing twice.
        # Roman Urdu: Entity aik todo ko do dafa complete honay se rokti hai.
        todo.mark_as_completed()
        self.todo_repo.save(todo)

        print_step(
            "Application",
            "Todo marked as complete and saved.",
            "Todo complete karke save kar diya gaya.",
        )
        return todo_to_dto(todo)
