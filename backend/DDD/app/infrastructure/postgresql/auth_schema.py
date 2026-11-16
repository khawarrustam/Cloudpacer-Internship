"""PostgreSQL users table creation and safe social-login migration."""

import psycopg


def ensure_auth_table(connection_url: str) -> None:
    """Create or extend users without deleting existing account data.

    What: Password, Google, aur GitHub login ke required columns banata hai.
    When: PostgreSQL auth repository application startup par create hoti hai.
    How: Safe CREATE/ALTER statements aur partial unique indexes use hotay hain.
    """
    create_table = """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            display_name TEXT NOT NULL,
            password_hash TEXT,
            google_sub TEXT,
            github_sub TEXT
        )
    """
    with psycopg.connect(connection_url) as connection:
        connection.execute(create_table)
        # Existing password-only table ko data loss ke baghair migrate karte hain.
        connection.execute(
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS google_sub TEXT"
        )
        connection.execute(
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS github_sub TEXT"
        )
        connection.execute(
            "ALTER TABLE users ALTER COLUMN password_hash DROP NOT NULL"
        )
        connection.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS users_google_sub_unique
            ON users (google_sub)
            WHERE google_sub IS NOT NULL
            """
        )
        connection.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS users_github_sub_unique
            ON users (github_sub)
            WHERE github_sub IS NOT NULL
            """
        )
