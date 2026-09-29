"""
=============================================================================
DOMAIN LAYER — Domain Exceptions (Clean Architecture / DDD)
=============================================================================
Domain layer mein business logic ke jo bhi errors hotay hain, unki custom
exception classes yahan define hoti hain.

Kyun Zaroori Hain:
- Standard Python errors ke bajaye specific domain errors banana zaroori hota hai
  taake pata chalay ke konsa business rule violate hua hai.
- Presentation layer (HTTP router) in errors ko pakar kar munassib HTTP Status
  Code (jaise 400 Bad Request ya 404 Not Found) mein convert karta hai.

Kahan Connected Hai:
- `InvalidTaskTitleError`: `src/domain/value_objects.py` mein title check karte waqt raise hota hai.
- `TaskAlreadyCompletedError`: `src/domain/entities.py` ke `mark_as_completed()` method mein raise hota hai.
- `TodoNotFoundError`: `src/application/use_cases/complete_todo.py` mein jab task na mile tab raise hota hai.
- Tamam exceptions: `src/presentation/api/todo_router.py` mein catch hoti hain.
=============================================================================
"""


class DomainError(Exception):
    """
    Kyun banaya gaya:
    - Tamam business rule errors ki parent (base) class hai.
    - Router mein sirf `except DomainError:` likh kar hum saare domain errors ko catch kar sakte hain.
    """
    pass


class InvalidTaskTitleError(DomainError):
    """
    Kyun banaya gaya:
    - Jab Todo ka title 3 characters se chota ho ya 120 se lamba ho, toh yeh raise hota hai.
    - Kahan raise hota hai: `src/domain/value_objects.py` mein.
    - HTTP Map: 400 Bad Request.
    """
    pass


class TaskAlreadyCompletedError(DomainError):
    """
    Kyun banaya gaya:
    - Business Invariant: Agar ek task pehle se mukammal ho chuka hai, toh usay dubara complete nahi kiya ja sakta.
    - Kahan raise hota hai: `src/domain/entities.py` ke `mark_as_completed()` method mein.
    - HTTP Map: 400 Bad Request.
    """
    pass


class TodoNotFoundError(DomainError):
    """
    Kyun banaya gaya:
    - Jab user aisi ID provide kare jo database/memory mein mojood na ho.
    - Kahan raise hota hai: `src/application/use_cases/complete_todo.py` mein.
    - HTTP Map: 404 Not Found.
    """
    pass
