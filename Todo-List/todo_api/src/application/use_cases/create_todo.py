"""
=============================================================================
APPLICATION LAYER — Create Todo Use Case (Clean Architecture / DDD)
=============================================================================
Application Layer business workflow (orchestration) ko lead karti hai.
Yeh layer framework (FastAPI) aur database se azaad hoti hai.

CreateTodoUseCase ka Kaam:
1. Command DTO se input data lena.
2. Domain Entity ka factory method (`TodoItem.create`) chala kar entity banana.
3. Repository interface ke zariye database mein save karwana.
4. Output DTO (`TodoDTO`) bana kar wapis karna.

Kahan Connected Hai:
- Instantiation: `main.py` is class ko repository ke sath initialize karta hai.
- Caller: `src/presentation/api/todo_router.py` is use case ka `execute()` method call karta hai.
- Domain Call: `src/domain/entities.py` ki `TodoItem.create()` factory ko call karta hai.
- Storage Call: `src/domain/repositories.py` ke `save()` method ko call karta hai.
=============================================================================
"""

# ---------------------------------------------------------------------------
# LIBRARIES / IMPORTS (Kyun aur kis liye import ki gayi hain):
# ---------------------------------------------------------------------------
# DOMAIN ENTITY: Naya aggregate root create karne ke liye.
from src.domain.entities import TodoItem

# VALUE OBJECT: Priority string ko domain Enum mein convert karne ke liye.
from src.domain.value_objects import Priority

# REPOSITORY INTERFACE: Data persistence ka abstract contract (DIP follow karne ke liye).
from src.domain.repositories import ITodoRepository

# APPLICATION DTOs: Input command aur output transfer object.
from src.application.dtos import CreateTodoCommand, TodoDTO


# ---------------------------------------------------------------------------
# USE CASE CLASS:
# ---------------------------------------------------------------------------
class CreateTodoUseCase:
    """
    Kyun banaya gaya:
    - Single Responsibility Principle (SRP): Naya Todo create karne ka workflow sirf is class mein hai.
    """

    def __init__(self, todo_repo: ITodoRepository):
        """
        Dependency Injection (DI):
        - Yeh use case kisi specific DB library par depend nahi karta, balki abstract `ITodoRepository` leta hai.
        """
        self.todo_repo = todo_repo

    def execute(self, cmd: CreateTodoCommand) -> TodoDTO:
        """
        Kyun use ho raha hai:
        - Task creation ka poora step-by-step workflow execute karta hai.

        Kaise kaam karta hai:
        1. `TodoItem.create()` ko call karke title aur priority deta hai.
           - Agar title invalid hoga toh yahin domain exception raise ho jayegi.
        2. `self.todo_repo.save(todo)` chala kar database mein save karwata hai.
        3. Domain entity ke data ko `TodoDTO` mein convert karke return karta hai.

        Kahan connected hai:
        - `src/presentation/api/todo_router.py` ke `create_todo` endpoint se call hota hai.
        """
        # 1. Domain Entity create karo (Business rules validate honge)
        todo = TodoItem.create(title=cmd.title, priority=Priority(cmd.priority.upper()))

        # 2. Storage mein save karo
        self.todo_repo.save(todo)

        # 3. Output DTO wapis bhejo
        return TodoDTO(
            id=todo.id,
            title=todo.title.value,
            priority=todo.priority.value,
            is_completed=todo.is_completed,
            created_at=todo.created_at.isoformat(),
            completed_at=None,
        )
