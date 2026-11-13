"""Firestore implementation of the todo repository contract."""

from datetime import datetime
from urllib.parse import quote

from google.auth.transport.requests import AuthorizedSession

from app.domain.todo import TodoItem, TodoRepository
from app.infrastructure.firestore.todo_mapper import (
    document_to_todo,
    todo_to_document,
)
from app.logging import log_step


class FirestoreTodoRepository(TodoRepository):
    """What: Persist TodoItem entities in Firestore.

    When: Firestore is the selected application database.
    How: Use Firestore's authenticated REST API and per-user subcollections.
    """

    def __init__(
        self,
        session: AuthorizedSession,
        documents_url: str,
        user_collection: str,
        todo_collection: str,
        page_size: int,
    ) -> None:
        self.session = session
        self.documents_url = documents_url
        self.user_collection = user_collection
        self.todo_collection = todo_collection
        self.page_size = page_size
        # Collection-group query scheduler ko all users ke due reminders deti hai.
        self.run_query_url = f"{documents_url}:runQuery"
        self.use_indexed_reminder_query = True

    def save(self, todo: TodoItem) -> None:
        """Create or update one Firestore todo document."""
        # PATCH same URL par create ya latest entity state update dono handle karta hai.
        response = self.session.patch(
            self._document_url(todo.owner_uid, todo.id),
            json=todo_to_document(todo),
        )
        response.raise_for_status()
        log_step(
            "Infrastructure",
            "Saved todo in Firebase Firestore.",
            "Todo Firebase Firestore mein save hua.",
        )

    def get_by_id(self, todo_id: str, owner_uid: str) -> TodoItem | None:
        """Find one owned Firestore todo or return None."""
        # Owner UID document path ka part hai, so doosre user ka ID same path nahi banata.
        response = self.session.get(self._document_url(owner_uid, todo_id))
        if response.status_code == 404:
            log_step(
                "Infrastructure",
                "Firebase Firestore did not find the todo.",
                "Firebase Firestore ko todo nahi mila.",
            )
            return None
        response.raise_for_status()
        log_step(
            "Infrastructure",
            "Firebase Firestore found the todo.",
            "Firebase Firestore ko todo mil gaya.",
        )
        return document_to_todo(response.json())

    def get_by_owner(self, owner_uid: str) -> list[TodoItem]:
        """Read all Firestore todos for one user, including every page."""
        documents = []
        page_token = None
        # nextPageToken loop large collections ka sirf first page read hone se rokta hai.
        while True:
            params = {"pageSize": self.page_size}
            if page_token:
                params["pageToken"] = page_token
            response = self.session.get(
                self._collection_url(owner_uid),
                params=params,
            )
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
        return [document_to_todo(document) for document in documents]

    def get_due_reminders(
        self,
        now: datetime,
        limit: int,
    ) -> list[TodoItem]:
        """Read due reminders across every user's todo subcollection."""
        indexed_query = {
            "structuredQuery": {
                "from": [{
                    "collectionId": self.todo_collection,
                    "allDescendants": True,
                }],
                # One inequality avoids a custom composite index. Completed/sent
                # filtering happens in Python for this beginner-sized project.
                "where": {
                    "fieldFilter": {
                        "field": {"fieldPath": "reminder_at"},
                        "op": "LESS_THAN_OR_EQUAL",
                        "value": {"stringValue": now.isoformat()},
                    }
                },
            }
        }
        scan_query = {
            "structuredQuery": {
                "from": [{
                    "collectionId": self.todo_collection,
                    "allDescendants": True,
                }]
            }
        }
        query = indexed_query if self.use_indexed_reminder_query else scan_query
        response = self.session.post(self.run_query_url, json=query)
        if (
            response.status_code == 400
            and "COLLECTION_GROUP_ASC" in response.text
        ):
            # New Firestore projects may not have the collection-group field
            # index yet. Small demo data can still work through one full scan.
            self.use_indexed_reminder_query = False
            log_step(
                "Infrastructure",
                "Firestore reminder index missing; using collection scan.",
                "Firestore reminder index nahi; collection scan use ho raha hai.",
            )
            response = self.session.post(self.run_query_url, json=scan_query)
        response.raise_for_status()
        due_todos = []
        for result in response.json():
            document = result.get("document")
            if not document:
                continue
            todo = document_to_todo(document)
            if todo.reminder_is_due(now):
                due_todos.append(todo)
        due_todos.sort(key=lambda todo: todo.reminder.reminder_at)
        return due_todos[:limit]

    def delete(self, todo_id: str, owner_uid: str) -> None:
        """Delete one user's todo document from Firestore."""
        response = self.session.delete(self._document_url(owner_uid, todo_id))
        if response.status_code != 404:
            response.raise_for_status()
        log_step(
            "Infrastructure",
            "Deleted todo from Firebase Firestore.",
            "Todo Firebase Firestore se delete hua.",
        )

    def _collection_url(self, owner_uid: str) -> str:
        """Build the current user's private todo collection URL."""
        users = quote(self.user_collection, safe="")
        owner = quote(owner_uid, safe="")
        todos = quote(self.todo_collection, safe="")
        return f"{self.documents_url}/{users}/{owner}/{todos}"

    def _document_url(self, owner_uid: str, todo_id: str) -> str:
        """Build the URL for one todo document."""
        return f"{self._collection_url(owner_uid)}/{quote(todo_id, safe='')}"
