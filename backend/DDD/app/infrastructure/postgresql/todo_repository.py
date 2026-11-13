"""PostgreSQL implementation of the todo repository contract."""

from datetime import datetime

import psycopg
from psycopg.rows import dict_row

from app.domain.reminder import ReminderSettings
from app.domain.todo import Priority, TaskTitle, TodoItem, TodoRepository
from app.infrastructure.postgresql.todo_schema import ensure_todo_table
from app.logging import log_step


class PostgreSQLTodoRepository(TodoRepository):
    """What: Persist TodoItem entities in a PostgreSQL table.

    When: PostgreSQL is the selected application database.
    How: Use parameterized SQL and named result rows.
    """

    def __init__(self, connection_url: str) -> None:
        self.connection_url = connection_url
        # Repository ready hone se pehle required todos table ensure hoti hai.
        ensure_todo_table(connection_url)

    def save(self, todo: TodoItem) -> None:
        """Insert a todo or update it when its ID already exists."""
        # One upsert method new todo aur completed state update dono support karta hai.
        query = """
            INSERT INTO todos (
                id, title, priority, is_completed,
                created_at, completed_at, owner_uid,
                due_at, reminder_at, reminder_email,
                reminder_sent_at, reminder_option
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                title = EXCLUDED.title,
                priority = EXCLUDED.priority,
                is_completed = EXCLUDED.is_completed,
                completed_at = EXCLUDED.completed_at,
                due_at = EXCLUDED.due_at,
                reminder_at = EXCLUDED.reminder_at,
                reminder_email = EXCLUDED.reminder_email,
                reminder_sent_at = EXCLUDED.reminder_sent_at,
                reminder_option = EXCLUDED.reminder_option
        """
        # Python datetime/boolean values Psycopg native PostgreSQL types mein bind karta hai.
        values = (
            todo.id,
            todo.title.value,
            todo.priority.value,
            todo.is_completed,
            todo.created_at,
            todo.completed_at,
            todo.owner_uid,
            todo.reminder.due_at,
            todo.reminder.reminder_at,
            todo.reminder.recipient_email,
            todo.reminder.sent_at,
            todo.reminder.option.value,
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
        # Owner condition security ko SQL query level tak enforce karti hai.
        query = """
            SELECT id, title, priority, is_completed,
                   created_at, completed_at, owner_uid,
                   due_at, reminder_at, reminder_email,
                   reminder_sent_at, reminder_option
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
        # Explicit ORDER BY PostgreSQL list ko deterministic newest-first banata hai.
        query = """
            SELECT id, title, priority, is_completed,
                   created_at, completed_at, owner_uid,
                   due_at, reminder_at, reminder_email,
                   reminder_sent_at, reminder_option
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

    def get_due_reminders(
        self,
        now: datetime,
        limit: int,
    ) -> list[TodoItem]:
        """Return due PostgreSQL reminders in earliest-first order."""
        query = """
            SELECT id, title, priority, is_completed,
                   created_at, completed_at, owner_uid,
                   due_at, reminder_at, reminder_email,
                   reminder_sent_at, reminder_option
            FROM todos
            WHERE is_completed = FALSE
              AND reminder_at IS NOT NULL
              AND reminder_at <= %s
              AND reminder_sent_at IS NULL
            ORDER BY reminder_at
            LIMIT %s
        """
        with psycopg.connect(
            self.connection_url,
            row_factory=dict_row,
        ) as connection:
            rows = connection.execute(query, (now, limit)).fetchall()
        return [self._to_entity(row) for row in rows]

    def delete(self, todo_id: str, owner_uid: str) -> None:
        """Delete one owned todo using safe SQL parameters."""
        # Parameter tuple SQL injection avoid karta hai; owner prevents cross-user delete.
        query = "DELETE FROM todos WHERE id = %s AND owner_uid = %s"
        with psycopg.connect(self.connection_url) as connection:
            connection.execute(query, (todo_id, owner_uid))
        log_step(
            "Infrastructure",
            "Deleted todo from PostgreSQL.",
            "Todo PostgreSQL se delete hua.",
        )

    @staticmethod
    def _to_entity(row: dict) -> TodoItem:
        """Convert one named PostgreSQL result row into TodoItem."""
        # Domain types restore karne se database data bhi same invariants follow karta hai.
        return TodoItem(
            id=row["id"],
            title=TaskTitle(row["title"]),
            priority=Priority(row["priority"]),
            is_completed=row["is_completed"],
            created_at=row["created_at"],
            completed_at=row["completed_at"],
            owner_uid=row["owner_uid"],
            reminder=ReminderSettings.restore(
                due_at=row.get("due_at"),
                reminder_at=row.get("reminder_at"),
                recipient_email=row.get("reminder_email"),
                sent_at=row.get("reminder_sent_at"),
                option=row.get("reminder_option"),
            ),
        )
