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

    def execute(self, owner_uid: str = "") -> List[TodoDTO]:
        print(f"   📂 File    : src/application/use_cases/list_todos.py")
        print(f"   🔧 Function: ListTodosUseCase.execute()")
        print(f"   🏛️  Layer   : APPLICATION LAYER (Use Case / Orchestrator)")

        if owner_uid:
            print(f"   🔐 Filtering by owner_uid: {owner_uid}")
            print(f"   ➡️  STEP A: Calling todo_repo.get_by_owner('{owner_uid}')")
            todos = self.todo_repo.get_by_owner(owner_uid)
        else:
            print(f"   ➡️  STEP A: Calling todo_repo.get_all() (no owner filter)")
            todos = self.todo_repo.get_all()

        print(f"   ✅ STEP B: Repository returned {len(todos)} entity(ies)")
        for i, t in enumerate(todos, 1):
            print(f"             [{i}] id={t.id[:8]}... | title={t.title.value} | owner={t.owner_uid}")

        print(f"   ➡️  STEP C: Converting Domain Entities → TodoDTOs")
        print(f"   ↩️  Returning List[TodoDTO] to Presentation Layer (todo_router.py)")

        return [
            TodoDTO(
                id=t.id,
                title=t.title.value,
                priority=t.priority.value,
                is_completed=t.is_completed,
                created_at=t.created_at.isoformat(),
                completed_at=t.completed_at.isoformat() if t.completed_at else None,
                owner_uid=t.owner_uid,
            )
            for t in todos
        ]
