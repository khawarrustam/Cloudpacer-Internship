"""PostgreSQL todo infrastructure."""

import psycopg
from psycopg.rows import dict_row

from src.domain.models import Priority, TaskTitle, TodoItem, TodoRepository
from src.logs import log_step


class PostgreSQLTodoRepository(TodoRepository):
    """Store todos in one simple PostgreSQL table."""

    def __init__(self, connection_url: str):
        """Remember the URL and automatically create the table if needed."""
        self.connection_url = connection_url
        self._create_table()

    def _create_table(self) -> None:
        """Create the todos table without changing an existing table."""
        query = """
            CREATE TABLE IF NOT EXISTS todos (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                priority TEXT NOT NULL,
                is_completed BOOLEAN NOT NULL,
                created_at TIMESTAMPTZ NOT NULL,
                completed_at TIMESTAMPTZ,
                owner_uid TEXT NOT NULL
            )
        """
        with psycopg.connect(self.connection_url) as connection:
            connection.execute(query)

    @staticmethod
    def _to_entity(row: dict) -> TodoItem:
        """Convert one named PostgreSQL result row into a TodoItem.

        Kyun: Column names (`row["title"]`) beginner ke liye numeric positions
        (`row[1]`) se zyada clear aur safe hain.
        """
        return TodoItem(
            id=row["id"],
            title=TaskTitle(row["title"]),
            priority=Priority(row["priority"]),
            is_completed=row["is_completed"],
            created_at=row["created_at"],
            completed_at=row["completed_at"],
            owner_uid=row["owner_uid"],
        )

    def save(self, todo: TodoItem) -> None:
        """Insert a todo or update it when the ID already exists."""
        query = """
            INSERT INTO todos (
                id, title, priority, is_completed,
                created_at, completed_at, owner_uid
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                title = EXCLUDED.title,
                priority = EXCLUDED.priority,
                is_completed = EXCLUDED.is_completed,
                completed_at = EXCLUDED.completed_at
        """
        values = (
            todo.id,
            todo.title.value,
            todo.priority.value,
            todo.is_completed,
            todo.created_at,
            todo.completed_at,
            todo.owner_uid,
        )
        with psycopg.connect(self.connection_url) as connection:
            connection.execute(query, values)
        log_step(
            "Infrastructure",
            "Saved todo in PostgreSQL.",
            "Todo PostgreSQL mein save hua.",
        )

    def get_by_id(self, todo_id: str, owner_uid: str) -> TodoItem | None:
        """Find one todo only when its ID and owner both match."""
        query = """
            SELECT id, title, priority, is_completed,
                   created_at, completed_at, owner_uid
            FROM todos
            WHERE id = %s AND owner_uid = %s
        """
        with psycopg.connect(
            self.connection_url,
            row_factory=dict_row,
        ) as connection:
            row = connection.execute(query, (todo_id, owner_uid)).fetchone()

        if row is None:
            log_step(
                "Infrastructure",
                "PostgreSQL did not find the todo.",
                "PostgreSQL ko todo nahi mila.",
            )
            return None

        log_step(
            "Infrastructure",
            "PostgreSQL found the todo.",
            "PostgreSQL ko todo mil gaya.",
        )
        return self._to_entity(row)

    def get_by_owner(self, owner_uid: str) -> list[TodoItem]:
        """Return one user's todos, newest first."""
        query = """
            SELECT id, title, priority, is_completed,
                   created_at, completed_at, owner_uid
            FROM todos
            WHERE owner_uid = %s
            ORDER BY created_at DESC
        """
        with psycopg.connect(
            self.connection_url,
            row_factory=dict_row,
        ) as connection:
            rows = connection.execute(query, (owner_uid,)).fetchall()

        log_step(
            "Infrastructure",
            f"PostgreSQL returned {len(rows)} todo(s).",
            f"PostgreSQL ne {len(rows)} todo diye.",
        )
        return [self._to_entity(row) for row in rows]

    def delete(self, todo_id: str, owner_uid: str) -> None:
        """Delete one owned todo using safe SQL parameters."""
        query = "DELETE FROM todos WHERE id = %s AND owner_uid = %s"
        with psycopg.connect(self.connection_url) as connection:
            connection.execute(query, (todo_id, owner_uid))
        log_step(
            "Infrastructure",
            "Deleted todo from PostgreSQL.",
            "Todo PostgreSQL se delete hua.",
        )
