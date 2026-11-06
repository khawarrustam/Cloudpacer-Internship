"""Simple public imports for all infrastructure adapters.

main.py sirf is file se classes import karta hai. Har database ki actual
implementation apni separate file mein rehti hai.
"""

from src.infrastructure.firebase_auth import FirebaseAuthRepository
from src.infrastructure.firestore import FirestoreTodoRepository
from src.infrastructure.mongodb import MongoTodoRepository
from src.infrastructure.postgresql import PostgreSQLTodoRepository

__all__ = [
    "FirebaseAuthRepository",
    "FirestoreTodoRepository",
    "MongoTodoRepository",
    "PostgreSQLTodoRepository",
]
