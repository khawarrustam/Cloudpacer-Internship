"""PostgreSQL todo table creation and safe reminder migration."""

import psycopg


def ensure_todo_table(connection_url: str) -> None:
    """Create or extend the todos table without deleting existing data."""
    create_table = """
        CREATE TABLE IF NOT EXISTS todos (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            priority TEXT NOT NULL,
            is_completed BOOLEAN NOT NULL,
            created_at TIMESTAMPTZ NOT NULL,
            completed_at TIMESTAMPTZ,
            owner_uid TEXT NOT NULL,
            due_at TIMESTAMPTZ,
            reminder_at TIMESTAMPTZ,
            reminder_email TEXT,
            reminder_sent_at TIMESTAMPTZ,
            reminder_option TEXT NOT NULL DEFAULT 'NONE'
        )
    """
    reminder_columns = [
        "ALTER TABLE todos ADD COLUMN IF NOT EXISTS due_at TIMESTAMPTZ",
        "ALTER TABLE todos ADD COLUMN IF NOT EXISTS reminder_at TIMESTAMPTZ",
        "ALTER TABLE todos ADD COLUMN IF NOT EXISTS reminder_email TEXT",
        "ALTER TABLE todos ADD COLUMN IF NOT EXISTS reminder_sent_at TIMESTAMPTZ",
        """
        ALTER TABLE todos
        ADD COLUMN IF NOT EXISTS reminder_option TEXT NOT NULL DEFAULT 'NONE'
        """,
    ]
    with psycopg.connect(connection_url) as connection:
        connection.execute(create_table)
        for statement in reminder_columns:
            connection.execute(statement)
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS todos_due_reminders_index
            ON todos (reminder_at)
            WHERE is_completed = FALSE AND reminder_sent_at IS NULL
            """
        )
