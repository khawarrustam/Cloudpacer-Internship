"""
=============================================================================
APPLICATION LAYER — Create Todo Use Case (Clean Architecture / DDD)
=============================================================================
"""

from src.domain.entities import TodoItem
from src.domain.value_objects import Priority
from src.domain.repositories import ITodoRepository
from src.application.dtos import CreateTodoCommand, TodoDTO


class CreateTodoUseCase:
    def __init__(self, todo_repo: ITodoRepository):
        self.todo_repo = todo_repo

    def execute(self, cmd: CreateTodoCommand) -> TodoDTO:
        print(f"   📂 File    : src/application/use_cases/create_todo.py")
        print(f"   🔧 Function: CreateTodoUseCase.execute()")
        print(f"   🏛️  Layer   : APPLICATION LAYER (Use Case / Orchestrator)")
        print(f"   📦 Command : title='{cmd.title}', priority='{cmd.priority}'")
        print(f"   ➡️  STEP A: Calling Domain Layer — TodoItem.create()")
        print(f"              📂 File: src/domain/entities.py → TodoItem.create()")
        print(f"              📂 File: src/domain/value_objects.py → Priority('{cmd.priority}')")

        # 1. Domain Entity create karo (Business rules validate honge)
        todo = TodoItem.create(title=cmd.title, priority=Priority(cmd.priority.upper()))

        print(f"   ✅ STEP B: Domain Entity created successfully!")
        print(f"              ID       : {todo.id}")
        print(f"              Title    : {todo.title.value}")
        print(f"              Priority : {todo.priority.value}")
        print(f"   ➡️  STEP C: Calling Infrastructure Layer — todo_repo.save(todo)")
        print(f"              📂 File: src/infrastructure/repositories/ (FirestoreTodoRepo or InMemoryTodoRepo)")

        # 2. Storage mein save karo
        self.todo_repo.save(todo)

        print(f"   ✅ STEP D: Repository saved entity to Database!")
        print(f"   ➡️  STEP E: Building TodoDTO (Output DTO)")
        print(f"              📂 File: src/application/dtos.py → TodoDTO")
        print(f"   ↩️  Returning TodoDTO to Presentation Layer (todo_router.py)")

        # 3. Output DTO wapis bhejo
        return TodoDTO(
            id=todo.id,
            title=todo.title.value,
            priority=todo.priority.value,
            is_completed=todo.is_completed,
            created_at=todo.created_at.isoformat(),
            completed_at=None,
        )
