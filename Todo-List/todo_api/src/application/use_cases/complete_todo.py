"""Use case for completing one todo."""

from src.application.dtos import CompleteTodoCommand, TodoDTO
from src.application.mappers import todo_to_dto
from src.domain.exceptions import TodoNotFoundError
from src.domain.repositories import ITodoRepository
from src.shared.console import module_file, print_error, print_flow, print_step


class CompleteTodoUseCase:
    def __init__(self, todo_repo: ITodoRepository):
        self.todo_repo = todo_repo

    def execute(self, command: CompleteTodoCommand) -> TodoDTO:
        print_flow(
            source="src/presentation/api/todo_router.py",
            destination="src/application/use_cases/complete_todo.py",
            data=f"todo_id={command.todo_id}, owner_uid={command.owner_uid}",
            english="The router sent a complete command to the use case.",
            roman_urdu="Router ne complete command use case ko bheji.",
        )
        print_flow(
            source="src/application/use_cases/complete_todo.py",
            destination=module_file(self.todo_repo),
            data=f"todo_id={command.todo_id}",
            english="Asking the repository to find the todo.",
            roman_urdu="Repository se todo dhoondnay ko kaha ja raha hai.",
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
        print_flow(
            source="src/application/use_cases/complete_todo.py",
            destination="src/domain/entities.py -> mark_as_completed",
            data=f"todo_id={todo.id}",
            english="Sending the todo to the domain completion rule.",
            roman_urdu="Todo domain ke completion rule ko ja raha hai.",
        )
        todo.mark_as_completed()

        print_flow(
            source="src/application/use_cases/complete_todo.py",
            destination=module_file(self.todo_repo),
            data=f"todo_id={todo.id}, is_completed={todo.is_completed}",
            english="Sending the updated todo back for saving.",
            roman_urdu="Updated todo dobara save honay ke liye ja raha hai.",
        )
        self.todo_repo.save(todo)

        print_step(
            "Application",
            "Todo marked as complete and saved.",
            "Todo complete karke save kar diya gaya.",
        )
        return todo_to_dto(todo)
