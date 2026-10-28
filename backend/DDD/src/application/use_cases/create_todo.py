"""Use case for creating one todo."""

from src.application.dtos import CreateTodoCommand, TodoDTO
from src.application.mappers import todo_to_dto
from src.domain.entities import TodoItem
from src.domain.repositories import ITodoRepository
from src.domain.value_objects import Priority
from src.shared.console import module_file, print_flow, print_step


class CreateTodoUseCase:
    def __init__(self, todo_repo: ITodoRepository):
        self.todo_repo = todo_repo

    def execute(self, command: CreateTodoCommand) -> TodoDTO:
        print_flow(
            source="src/presentation/api/todo_router.py",
            destination="src/application/use_cases/create_todo.py",
            data=f"title={command.title}, priority={command.priority}",
            english="The router sent a create command to the use case.",
            roman_urdu="Router ne create command use case ko bheji.",
        )

        # English: The domain creates and validates the todo.
        # Roman Urdu: Domain todo banata hai aur uski validation karta hai.
        print_flow(
            source="src/application/use_cases/create_todo.py",
            destination="src/domain/entities.py -> TodoItem.create",
            data=f"title={command.title}, priority={command.priority}",
            english="Sending input to the domain for validation.",
            roman_urdu="Validation ke liye input domain ko ja raha hai.",
        )
        todo = TodoItem.create(
            title=command.title,
            priority=Priority(command.priority.upper()),
            owner_uid=command.owner_uid,
        )

        # English: The repository hides the storage details.
        # Roman Urdu: Repository storage ki detail ko chhupa kar todo save karti hai.
        print_flow(
            source="src/application/use_cases/create_todo.py",
            destination=module_file(self.todo_repo),
            data=f"todo_id={todo.id}, owner_uid={todo.owner_uid}",
            english="Sending the valid todo to the repository for saving.",
            roman_urdu="Valid todo save honay ke liye repository ko ja raha hai.",
        )
        self.todo_repo.save(todo)

        print_step(
            "Application",
            f"Todo saved with id {todo.id}.",
            f"Todo id {todo.id} ke sath save ho gaya.",
        )
        return todo_to_dto(todo)
