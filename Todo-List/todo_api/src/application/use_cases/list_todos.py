"""
=============================================================================
APPLICATION LAYER — List Todos Use Case (Clean Architecture / DDD)
=============================================================================
"""

from typing import List
from src.domain.repositories import ITodoRepository
from src.application.dtos import TodoDTO


class ListTodosUseCase:
    def __init__(self, todo_repo: ITodoRepository):
        self.todo_repo = todo_repo

    def execute(self) -> List[TodoDTO]:
        print(f"   📂 File    : src/application/use_cases/list_todos.py")
        print(f"   🔧 Function: ListTodosUseCase.execute()")
        print(f"   🏛️  Layer   : APPLICATION LAYER (Use Case / Orchestrator)")
        print(f"   ➡️  STEP A: Calling Infrastructure Layer — todo_repo.get_all()")
        print(f"              📂 File: src/infrastructure/repositories/ → get_all()")

        todos = self.todo_repo.get_all()

        print(f"   ✅ STEP B: Repository returned {len(todos)} entity(ies)")
        for i, t in enumerate(todos, 1):
            print(f"             [{i}] id={t.id[:8]}... | title={t.title.value} | completed={t.is_completed}")

        print(f"   ➡️  STEP C: Converting Domain Entities → TodoDTOs")
        print(f"              📂 File: src/application/dtos.py → TodoDTO")
        print(f"   ↩️  Returning List[TodoDTO] to Presentation Layer (todo_router.py)")

        return [
            TodoDTO(
                id=t.id,
                title=t.title.value,
                priority=t.priority.value,
                is_completed=t.is_completed,
                created_at=t.created_at.isoformat(),
                completed_at=t.completed_at.isoformat() if t.completed_at else None,
            )
            for t in todos
        ]
