"""Infrastructure layer: memory, Firebase Auth, and Firestore adapters."""

from datetime import datetime
import os
from urllib.parse import quote

from firebase_admin import auth
from google.auth.transport.requests import AuthorizedSession
import requests

from src.domain.models import (
    AuthRepository,
    Priority,
    TaskTitle,
    TodoItem,
    TodoRepository,
    UserData,
    ValidationException,
)
from src.logs import log_error, log_step


class InMemoryTodoRepository(TodoRepository):
    def __init__(self):
        self.todos: dict[str, TodoItem] = {}

    def save(self, todo: TodoItem) -> None:
        self.todos[todo.id] = todo
        log_step("Infrastructure", "Saved todo in memory.", "Todo memory mein save hua.")

    def get_by_id(self, todo_id: str, owner_uid: str) -> TodoItem | None:
        todo = self.todos.get(todo_id)
        return todo if todo and todo.owner_uid == owner_uid else None

    def get_by_owner(self, owner_uid: str) -> list[TodoItem]:
        return [todo for todo in self.todos.values() if todo.owner_uid == owner_uid]

    def delete(self, todo_id: str, owner_uid: str) -> None:
        if self.get_by_id(todo_id, owner_uid):
            del self.todos[todo_id]


class FirebaseAuthRepository(AuthRepository):
    api_key = os.environ["FIREBASE_WEB_API_KEY"]
    login_url = f"{os.environ['FIREBASE_AUTH_URL']}?key={api_key}"
    request_timeout = int(os.environ["FIREBASE_REQUEST_TIMEOUT"])

    def signup(self, email: str, password: str, name: str) -> UserData:
        try:
            auth.create_user(email=email, password=password, display_name=name)
            return self.login(email, password)
        except ValidationException:
            raise
        except Exception as error:
            log_error("Infrastructure", f"Firebase signup failed: {error}")
            raise ValidationException(str(error)) from error

    def login(self, email: str, password: str) -> UserData:
        try:
            response = requests.post(
                self.login_url,
                json={
                    "email": email,
                    "password": password,
                    "returnSecureToken": True,
                },
                timeout=self.request_timeout,
            )
            if response.status_code != 200:
                message = response.json().get("error", {}).get(
                    "message",
                    "Invalid email or password",
                )
                raise ValidationException(message)
            data = response.json()
            log_step(
                "Infrastructure",
                "Firebase authentication succeeded.",
                "Firebase authentication kamyab ho gayi.",
            )
            return UserData(data["localId"], data["email"], data["idToken"])
        except ValidationException:
            raise
        except Exception as error:
            log_error("Infrastructure", f"Firebase login failed: {error}")
            raise ValidationException(str(error)) from error


class FirestoreTodoRepository(TodoRepository):
    """Persistent Firestore storage over HTTPS; no gRPC DLL is needed."""

    def __init__(self, project_id: str, credentials):
        self.session = AuthorizedSession(credentials)
        project = quote(project_id, safe="")
        database = quote(os.environ["FIRESTORE_DATABASE_ID"], safe="()")
        api_url = os.environ["FIRESTORE_API_URL"].rstrip("/")
        self.user_collection = os.environ["FIRESTORE_USER_COLLECTION"]
        self.todo_collection = os.environ["FIRESTORE_TODO_COLLECTION"]
        self.page_size = int(os.environ["FIRESTORE_PAGE_SIZE"])
        self.base_url = (
            f"{api_url}/projects/{project}/databases/"
            f"{database}/documents"
        )

    @staticmethod
    def _encode(value):
        if value is None:
            return {"nullValue": None}
        if isinstance(value, bool):
            return {"booleanValue": value}
        return {"stringValue": str(value)}

    @staticmethod
    def _decode(value):
        if "nullValue" in value:
            return None
        if "booleanValue" in value:
            return value["booleanValue"]
        return value.get("stringValue", "")

    def _collection_url(self, owner_uid: str) -> str:
        users = quote(self.user_collection, safe="")
        todos = quote(self.todo_collection, safe="")
        return (
            f"{self.base_url}/{users}/"
            f"{quote(owner_uid, safe='')}/{todos}"
        )

    def _document_url(self, owner_uid: str, todo_id: str) -> str:
        return f"{self._collection_url(owner_uid)}/{quote(todo_id, safe='')}"

    def _to_document(self, todo: TodoItem) -> dict:
        values = {
            "id": todo.id,
            "title": todo.title.value,
            "priority": todo.priority.value,
            "is_completed": todo.is_completed,
            "created_at": todo.created_at.isoformat(),
            "completed_at": (
                todo.completed_at.isoformat() if todo.completed_at else None
            ),
            "owner_uid": todo.owner_uid,
        }
        return {"fields": {key: self._encode(value) for key, value in values.items()}}

    def _to_entity(self, document: dict) -> TodoItem:
        values = {
            key: self._decode(value)
            for key, value in document.get("fields", {}).items()
        }
        return TodoItem(
            id=values["id"],
            title=TaskTitle(values["title"]),
            priority=Priority(values["priority"]),
            is_completed=values["is_completed"],
            created_at=datetime.fromisoformat(values["created_at"]),
            owner_uid=values["owner_uid"],
            completed_at=(
                datetime.fromisoformat(values["completed_at"])
                if values.get("completed_at")
                else None
            ),
        )

    def save(self, todo: TodoItem) -> None:
        response = self.session.patch(
            self._document_url(todo.owner_uid, todo.id),
            json=self._to_document(todo),
        )
        response.raise_for_status()
        log_step(
            "Infrastructure",
            "Saved todo in Firebase Firestore.",
            "Todo Firebase Firestore mein save hua.",
        )

    def get_by_id(self, todo_id: str, owner_uid: str) -> TodoItem | None:
        response = self.session.get(self._document_url(owner_uid, todo_id))
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return self._to_entity(response.json())

    def get_by_owner(self, owner_uid: str) -> list[TodoItem]:
        documents = []
        page_token = None
        while True:
            params = {"pageSize": self.page_size}
            if page_token:
                params["pageToken"] = page_token
            response = self.session.get(self._collection_url(owner_uid), params=params)
            response.raise_for_status()
            data = response.json()
            documents.extend(data.get("documents", []))
            page_token = data.get("nextPageToken")
            if not page_token:
                break
        log_step(
            "Infrastructure",
            f"Firestore returned {len(documents)} todo(s).",
            f"Firestore ne {len(documents)} todo diye.",
        )
        return [self._to_entity(document) for document in documents]

    def delete(self, todo_id: str, owner_uid: str) -> None:
        response = self.session.delete(self._document_url(owner_uid, todo_id))
        if response.status_code != 404:
            response.raise_for_status()
