"""Use case for creating one todo."""

from src.application.dtos import CreateTodoCommand, TodoDTO
from src.application.mappers import todo_to_dto
from src.domain.entities import TodoItem
from src.domain.repositories import ITodoRepository
from src.domain.value_objects import Priority
from src.shared.console import print_step


class CreateTodoUseCase:
    def __init__(self, todo_repo: ITodoRepository):
        self.todo_repo = todo_repo

    def execute(self, command: CreateTodoCommand) -> TodoDTO:
        print_step(
            "Application",
            f"Creating todo: {command.title}",
            f"Naya todo ban raha hai: {command.title}",
        )

        # English: The domain creates and validates the todo.
        # Roman Urdu: Domain todo banata hai aur uski validation karta hai.
        todo = TodoItem.create(
            title=command.title,
            priority=Priority(command.priority.upper()),
            owner_uid=command.owner_uid,
        )

        # English: The repository hides the storage details.
        # Roman Urdu: Repository storage ki detail ko chhupa kar todo save karti hai.
        self.todo_repo.save(todo)

        print_step(
            "Application",
            f"Todo saved with id {todo.id}.",
            f"Todo id {todo.id} ke sath save ho gaya.",
        )
        return todo_to_dto(todo)
