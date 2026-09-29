"""
=============================================================================
APPLICATION LAYER — Complete Todo Use Case (Clean Architecture / DDD)
=============================================================================
Yeh Use Case kisi mojooda Todo ko complete (mukammal) karne ka workflow chalata hai.

CompleteTodoUseCase ka Kaam:
1. Command se `todo_id` hasil karna.
2. Repository se entity fetch karna (agar na mile toh `TodoNotFoundError` dena).
3. Entity ka `mark_as_completed()` method call karna (business invariant check).
4. Updated entity ko repository ke zariye database mein save karwana.
5. Result ko `TodoDTO` mein pack karke wapis bhejna.

Kahan Connected Hai:
- Instantiation: `main.py` is class ko repository ke sath instantiate karta hai.
- Caller: `src/presentation/api/todo_router.py` ke `complete_todo` endpoint se call hota hai.
- Domain Call: `src/domain/entities.py` ke `todo.mark_as_completed()` ko call karta hai.
- Storage Call: `src/domain/repositories.py` ke `get_by_id()` aur `save()` ko call karta hai.
=============================================================================
"""

# ---------------------------------------------------------------------------
# LIBRARIES / IMPORTS (Kyun aur kis liye import ki gayi hain):
# ---------------------------------------------------------------------------
# REPOSITORY INTERFACE: Database ke operations access karne ke liye abstract contract.
from src.domain.repositories import ITodoRepository

# DOMAIN EXCEPTION: Jab database mein requested ID ka task na mile.
from src.domain.exceptions import TodoNotFoundError

# APPLICATION DTOs: Input command (id) aur output DTO.
from src.application.dtos import CompleteTodoCommand, TodoDTO


# ---------------------------------------------------------------------------
# USE CASE CLASS:
# ---------------------------------------------------------------------------
class CompleteTodoUseCase:
    """
    Kyun banaya gaya:
    - Single Responsibility: Todo ko complete karne ka poora workflow orchestrate karna.
    """

    def __init__(self, todo_repo: ITodoRepository):
        """
        Dependency Injection (DI):
        - Abstract repository interface inject hota hai.
        """
        self.todo_repo = todo_repo

    def execute(self, cmd: CompleteTodoCommand) -> TodoDTO:
        """
        Kyun use ho raha hai:
        - Task completion ka step-by-step workflow execute karne ke liye.

        Kaise kaam karta hai:
        1. `self.todo_repo.get_by_id(cmd.todo_id)` chala kar task dhoondta hai.
        2. Agar task nahi milta, toh `TodoNotFoundError` raise karta hai.
        3. Agar mil jaye, toh entity ka method `todo.mark_as_completed()` call karta hai.
           - Domain Entity khud check karegi ke agar already completed hai toh `TaskAlreadyCompletedError` degi.
        4. Entity update hone ke baad `self.todo_repo.save(todo)` chala kar DB mein update save karta hai.
        5. Updated data `TodoDTO` bana kar return karta hai.

        Kahan connected hai:
        - `src/presentation/api/todo_router.py` ke `complete_todo` PATCH route se call hota hai.
        """
        # 1. Repository se task nikaalo
        todo = self.todo_repo.get_by_id(cmd.todo_id)
        if not todo:
            raise TodoNotFoundError(f"Todo with ID '{cmd.todo_id}' was not found.")

        # 2. Business logic aggregate ke method se chalegi (Enforcing invariant)
        todo.mark_as_completed()

        # 3. Updated state ko save karo
        self.todo_repo.save(todo)

        # 4. Output DTO wapis karo
        return TodoDTO(
            id=todo.id,
            title=todo.title.value,
            priority=todo.priority.value,
            is_completed=todo.is_completed,
            created_at=todo.created_at.isoformat(),
            completed_at=todo.completed_at.isoformat() if todo.completed_at else None,
        )
