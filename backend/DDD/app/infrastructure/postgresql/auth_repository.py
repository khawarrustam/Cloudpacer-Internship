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
    How: Use a unique email column, hashed passwords, and database-bound JWTs.
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
            user.get("password_hash"),
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

    def login_with_google(self, credential: str) -> UserData:
        """Verify Google, then find/create its user only in PostgreSQL."""
        profile = self.security.verify_google_credential(credential)
        try:
            with psycopg.connect(
                self.connection_url,
                row_factory=dict_row,
            ) as connection:
                # Stable Google subject first; email fallback links a password account.
                user = connection.execute(
                    "SELECT id, email, google_sub FROM users WHERE google_sub = %s",
                    (profile.subject,),
                ).fetchone()
                if user is None:
                    user = connection.execute(
                        "SELECT id, email, google_sub FROM users WHERE email = %s",
                        (profile.email,),
                    ).fetchone()

                if user is None:
                    uid = str(uuid.uuid4())
                    connection.execute(
                        """
                        INSERT INTO users (
                            id, email, display_name, password_hash, google_sub
                        ) VALUES (%s, %s, %s, NULL, %s)
                        """,
                        (
                            uid,
                            profile.email,
                            profile.display_name,
                            profile.subject,
                        ),
                    )
                    user = {
                        "id": uid,
                        "email": profile.email,
                        "google_sub": profile.subject,
                    }
                else:
                    saved_subject = user.get("google_sub")
                    if saved_subject and saved_subject != profile.subject:
                        raise ValidationException(
                            "This PostgreSQL email belongs to another Google account."
                        )
                    if not saved_subject and not profile.can_link_existing_email:
                        raise ValidationException(
                            "Use your PostgreSQL password for this non-Gmail account."
                        )
                    if not saved_subject:
                        connection.execute(
                            "UPDATE users SET google_sub = %s WHERE id = %s",
                            (profile.subject, user["id"]),
                        )
        except ValidationException:
            raise
        except psycopg.errors.UniqueViolation as error:
            raise ValidationException(
                "This Google account already exists in PostgreSQL."
            ) from error
        except Exception as error:
            log_error("Infrastructure", f"PostgreSQL Google login failed: {error}")
            raise ValidationException("PostgreSQL Google login failed.") from error

        token = self.security.create_token(user["id"], user["email"])
        log_step(
            "Infrastructure",
            "PostgreSQL Google authentication succeeded.",
            "PostgreSQL Google authentication kamyab ho gayi.",
        )
        return UserData(uid=user["id"], email=user["email"], token=token)

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
        """Create or safely extend the users table for both login methods."""
        # IF NOT EXISTS existing table/data ko delete ya reset nahi karta.
        create_table = """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                display_name TEXT NOT NULL,
                password_hash TEXT,
                google_sub TEXT
            )
        """
        with psycopg.connect(self.connection_url) as connection:
            connection.execute(create_table)
            # Existing password-only table ko data loss ke baghair migrate karte hain.
            connection.execute(
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS google_sub TEXT"
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
