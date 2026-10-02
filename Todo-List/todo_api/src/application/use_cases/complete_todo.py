"""
=============================================================================
APPLICATION LAYER — Complete Todo Use Case (Clean Architecture / DDD)
=============================================================================
"""

from src.domain.repositories import ITodoRepository
from src.domain.exceptions import TodoNotFoundError
from src.application.dtos import CompleteTodoCommand, TodoDTO


class CompleteTodoUseCase:
    def __init__(self, todo_repo: ITodoRepository):
        self.todo_repo = todo_repo

    def execute(self, cmd: CompleteTodoCommand) -> TodoDTO:
        print(f"   📂 File    : src/application/use_cases/complete_todo.py")
        print(f"   🔧 Function: CompleteTodoUseCase.execute()")
        print(f"   🏛️  Layer   : APPLICATION LAYER (Use Case / Orchestrator)")
        print(f"   📦 Command : todo_id='{cmd.todo_id}'")
        print(f"   ➡️  STEP A: Calling Infrastructure Layer — todo_repo.get_by_id()")
        print(f"              📂 File: src/infrastructure/repositories/ → get_by_id('{cmd.todo_id}')")

        # 1. Repository se task nikaalo
        todo = self.todo_repo.get_by_id(cmd.todo_id)

        if not todo:
            print(f"   ❌ STEP B: Entity NOT FOUND in Repository!")
            print(f"      Raising: TodoNotFoundError")
            print(f"      📂 File: src/domain/exceptions.py → TodoNotFoundError")
            raise TodoNotFoundError(f"Todo with ID '{cmd.todo_id}' was not found.")

        print(f"   ✅ STEP B: Entity fetched from Repository!")
        print(f"              Title        : {todo.title.value}")
        print(f"              is_completed : {todo.is_completed}")
        print(f"   ➡️  STEP C: Calling Domain Layer — todo.mark_as_completed()")
        print(f"              📂 File: src/domain/entities.py → TodoItem.mark_as_completed()")
        print(f"              (Domain will enforce: cannot complete twice!)")

        # 2. Business logic aggregate ke method se chalegi
        todo.mark_as_completed()

        print(f"   ✅ STEP D: Domain Entity marked as completed!")
        print(f"              is_completed : {todo.is_completed}")
        print(f"              completed_at : {todo.completed_at}")
        print(f"   ➡️  STEP E: Calling Infrastructure Layer — todo_repo.save(todo)")
        print(f"              (Saving updated entity back to Database)")

        # 3. Updated state ko save karo
        self.todo_repo.save(todo)

        print(f"   ✅ STEP F: Repository saved updated entity!")
        print(f"   ➡️  STEP G: Building TodoDTO (Output DTO)")
        print(f"              📂 File: src/application/dtos.py → TodoDTO")
        print(f"   ↩️  Returning TodoDTO to Presentation Layer (todo_router.py)")

        # 4. Output DTO wapis karo
        return TodoDTO(
            id=todo.id,
            title=todo.title.value,
            priority=todo.priority.value,
            is_completed=todo.is_completed,
            created_at=todo.created_at.isoformat(),
            completed_at=todo.completed_at.isoformat() if todo.completed_at else None,
        )
