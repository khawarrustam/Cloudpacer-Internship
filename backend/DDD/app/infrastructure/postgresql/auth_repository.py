"""PostgreSQL implementation of the authentication repository contract."""

import uuid

import psycopg
from psycopg.rows import dict_row

from app.domain.auth import AuthRepository, UserData, ValidationException
from app.infrastructure.security import AuthSecurity
from app.logging import log_error, log_step


class PostgreSQLAuthRepository(AuthRepository):
    """What: Store and authenticate users inside PostgreSQL.

    When: PostgreSQL is the selected database for users and todos.
    How: Use a unique email column, hashed passwords, and database-bound tokens.
    """

    def __init__(self, connection_url: str, security: AuthSecurity) -> None:
        self.connection_url = connection_url
        self.security = security
        # Beginner setup simple rakhne ke liye missing table startup par create hoti hai.
        self._create_table()

    def signup(self, email: str, password: str, name: str) -> UserData:
        """Create a PostgreSQL-only account and return its token."""
        clean_email = self.security.normalize_email(email)
        uid = str(uuid.uuid4())
        query = """
            INSERT INTO users (id, email, display_name, password_hash)
            VALUES (%s, %s, %s, %s)
        """
        # Values query string mein concatenate nahi hoti; driver placeholders bind karta hai.
        values = (
            uid,
            clean_email,
            name.strip() or "User",
            self.security.hash_password(password),
        )
        try:
            # Context manager success par commit, error par rollback/cleanup handle karta hai.
            with psycopg.connect(self.connection_url) as connection:
                connection.execute(query, values)
        except psycopg.errors.UniqueViolation as error:
            raise ValidationException(
                "This email is already registered in PostgreSQL."
            ) from error
        except Exception as error:
            log_error("Infrastructure", f"PostgreSQL signup failed: {error}")
            raise ValidationException("PostgreSQL signup failed.") from error

        token = self.security.create_token(uid, clean_email)
        log_step(
            "Infrastructure",
            "PostgreSQL user account created.",
            "PostgreSQL user account ban gaya.",
        )
        return UserData(uid=uid, email=clean_email, token=token)

    def login(self, email: str, password: str) -> UserData:
        """Verify credentials using only PostgreSQL user data."""
        clean_email = self.security.normalize_email(email)
        query = """
            SELECT id, email, password_hash
            FROM users
            WHERE email = %s
        """
        # dict_row readable column names deta hai instead of fragile numeric indexes.
        with psycopg.connect(
            self.connection_url,
            row_factory=dict_row,
        ) as connection:
            user = connection.execute(query, (clean_email,)).fetchone()

        if user is None or not self.security.password_matches(
            password,
            user["password_hash"],
        ):
            raise ValidationException("Invalid PostgreSQL email or password.")

        token = self.security.create_token(user["id"], user["email"])
        log_step(
            "Infrastructure",
            "PostgreSQL authentication succeeded.",
            "PostgreSQL authentication kamyab ho gayi.",
        )
        return UserData(
            uid=user["id"],
            email=user["email"],
            token=token,
        )

    def authenticate(self, token: str) -> UserData:
        """Accept the token only if its PostgreSQL user still exists."""
        uid, email = self.security.read_token(token)
        # Valid signature ke baad current users table mein live account bhi required hai.
        query = "SELECT id FROM users WHERE id = %s AND email = %s"
        with psycopg.connect(self.connection_url) as connection:
            user = connection.execute(query, (uid, email)).fetchone()
        if user is None:
            raise ValidationException("PostgreSQL user no longer exists.")
        return UserData(uid=uid, email=email, token=token)

    def _create_table(self) -> None:
        """Create the users table without changing an existing table."""
        # IF NOT EXISTS existing table/data ko delete ya reset nahi karta.
        query = """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                display_name TEXT NOT NULL,
                password_hash TEXT NOT NULL
            )
        """
        with psycopg.connect(self.connection_url) as connection:
            connection.execute(query)
