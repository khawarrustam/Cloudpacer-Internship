"""Create real adapters and connect them to the use cases."""

import os

import firebase_admin
from fastapi import FastAPI
from firebase_admin import credentials, firestore

from src.application.use_cases.complete_todo import CompleteTodoUseCase
from src.application.use_cases.create_todo import CreateTodoUseCase
from src.application.use_cases.delete_todo import DeleteTodoUseCase
from src.application.use_cases.list_todos import ListTodosUseCase
from src.application.use_cases.signin_user import SigninUserUseCase
from src.application.use_cases.signup_user import SignupUserUseCase
from src.domain.repositories import ITodoRepository
from src.infrastructure.repositories.firebase_auth_repo import FirebaseAuthRepository
from src.infrastructure.repositories.firestore_todo_repo import FirestoreTodoRepository
from src.infrastructure.repositories.in_memory_todo_repo import InMemoryTodoRepository
from src.presentation.api.auth_router import get_signin_use_case, get_signup_use_case
from src.presentation.api.todo_router import (
    get_complete_use_case,
    get_create_use_case,
    get_delete_use_case,
    get_list_use_case,
)
from src.shared.console import print_step


def initialize_firebase() -> None:
    """Start Firebase Admin once for authentication and optional Firestore use."""
    if firebase_admin._apps:
        return

    credential_path = os.getenv(
        "FIREBASE_CREDENTIALS_PATH",
        "serviceAccountKey.json",
    )

    if os.path.exists(credential_path):
        firebase_admin.initialize_app(credentials.Certificate(credential_path))
        print_step(
            "Setup",
            "Firebase started with the service account file.",
            "Firebase service account file ke sath start ho gaya.",
        )
    else:
        firebase_admin.initialize_app()
        print_step(
            "Setup",
            "Firebase started with default credentials.",
            "Firebase default credentials ke sath start ho gaya.",
        )


def create_todo_repository() -> ITodoRepository:
    """Choose Firestore or temporary memory storage from USE_FIREBASE."""
    use_firestore = os.getenv("USE_FIREBASE", "false").lower() == "true"

    if use_firestore:
        print_step(
            "Setup",
            "Todo storage: Firebase Firestore.",
            "Todo data Firebase Firestore mein save hoga.",
        )
        return FirestoreTodoRepository(db=firestore.client())

    print_step(
        "Setup",
        "Todo storage: temporary in-memory storage.",
        "Todo data filhal memory mein save hoga.",
    )
    return InMemoryTodoRepository()


def wire_dependencies(app: FastAPI, todo_repo: ITodoRepository) -> None:
    """Build use cases and give them to FastAPI routes."""
    auth_repo = FirebaseAuthRepository()

    create_use_case = CreateTodoUseCase(todo_repo)
    complete_use_case = CompleteTodoUseCase(todo_repo)
    list_use_case = ListTodosUseCase(todo_repo)
    delete_use_case = DeleteTodoUseCase(todo_repo)
    signup_use_case = SignupUserUseCase(auth_repo)
    signin_use_case = SigninUserUseCase(auth_repo)

    app.dependency_overrides[get_create_use_case] = lambda: create_use_case
    app.dependency_overrides[get_complete_use_case] = lambda: complete_use_case
    app.dependency_overrides[get_list_use_case] = lambda: list_use_case
    app.dependency_overrides[get_delete_use_case] = lambda: delete_use_case
    app.dependency_overrides[get_signup_use_case] = lambda: signup_use_case
    app.dependency_overrides[get_signin_use_case] = lambda: signin_use_case

    print_step(
        "Setup",
        "Repositories and use cases are connected.",
        "Repositories aur use cases aapas mein connect ho gaye.",
    )
