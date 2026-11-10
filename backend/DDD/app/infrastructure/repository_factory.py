"""Create matching auth and todo repositories for the selected database."""

from urllib.parse import quote

import firebase_admin
from firebase_admin import credentials
from google.auth.transport.requests import AuthorizedSession
from pymongo import MongoClient

from app.config import Settings
from app.domain.auth import AuthRepository
from app.domain.todo import TodoRepository
from app.infrastructure.firestore.auth_repository import FirestoreAuthRepository
from app.infrastructure.firestore.todo_repository import FirestoreTodoRepository
from app.infrastructure.mongodb.auth_repository import MongoAuthRepository
from app.infrastructure.mongodb.todo_repository import MongoTodoRepository
from app.infrastructure.postgresql.auth_repository import (
    PostgreSQLAuthRepository,
)
from app.infrastructure.postgresql.todo_repository import (
    PostgreSQLTodoRepository,
)
from app.infrastructure.security import AuthSecurity
from app.logging import log_step


def create_repositories(
    settings: Settings,
) -> tuple[TodoRepository, AuthRepository]:
    """What: Build todo and auth adapters for one selected database.

    When: The composition root starts the application.
    How: Create shared security, choose one driver, and return both contracts.
    """
    database = settings.selected_database
    security = AuthSecurity(
        secret=settings.auth_token_secret,
        database=database,
        token_expire_minutes=settings.auth_token_expire_minutes,
    )

    if database == "firestore":
        return _create_firestore_repositories(settings, security)
    if database == "mongodb":
        return _create_mongodb_repositories(settings, security)
    return _create_postgresql_repositories(settings, security)


def _create_firestore_repositories(
    settings: Settings,
    security: AuthSecurity,
) -> tuple[TodoRepository, AuthRepository]:
    """Connect Firestore once, then give both repositories one REST session."""
    if not firebase_admin._apps:
        firebase_admin.initialize_app(
            credentials.Certificate(settings.firebase_credential_file)
        )
        log_step(
            "Setup",
            "Firestore credentials connected.",
            "Firestore credentials connect ho gayin.",
        )

    firebase_app = firebase_admin.get_app()
    project = quote(firebase_app.project_id, safe="")
    database = quote(settings.firestore_database_id, safe="()")
    documents_url = (
        f"{settings.firestore_api_url.rstrip('/')}/projects/{project}/"
        f"databases/{database}/documents"
    )
    session = AuthorizedSession(firebase_app.credential.get_credential())
    auth_users_url = (
        f"{documents_url}/"
        f"{quote(settings.firestore_auth_collection, safe='')}"
    )
    todo_repository = FirestoreTodoRepository(
        session=session,
        documents_url=documents_url,
        user_collection=settings.firestore_user_collection,
        todo_collection=settings.firestore_todo_collection,
        page_size=settings.firestore_page_size,
    )
    auth_repository = FirestoreAuthRepository(
        session=session,
        users_url=auth_users_url,
        security=security,
    )
    return todo_repository, auth_repository


def _create_mongodb_repositories(
    settings: Settings,
    security: AuthSecurity,
) -> tuple[TodoRepository, AuthRepository]:
    """Connect MongoDB once and pass focused collections to repositories."""
    client = MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    database = client[settings.mongodb_database]
    todo_repository = MongoTodoRepository(
        database[settings.mongodb_todo_collection]
    )
    auth_repository = MongoAuthRepository(
        database[settings.mongodb_user_collection],
        security,
    )
    return todo_repository, auth_repository


def _create_postgresql_repositories(
    settings: Settings,
    security: AuthSecurity,
) -> tuple[TodoRepository, AuthRepository]:
    """Create both PostgreSQL repositories with the same connection URL."""
    if not settings.postgresql_url:
        raise RuntimeError("Missing required setting: POSTGRESQL_URL")
    return (
        PostgreSQLTodoRepository(settings.postgresql_url),
        PostgreSQLAuthRepository(settings.postgresql_url, security),
    )
