"""Shared password hashing and standard JWT implementation."""

from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import secrets

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from app.domain.auth import ValidationException


class AuthSecurity:
    """What: Hash passwords and create database-bound JWT access tokens.

    When: A concrete AuthRepository signs up, logs in, or verifies a user.
    How: PBKDF2 protects passwords and PyJWT handles standard HS256 tokens.
    """

    PASSWORD_ITERATIONS = 120_000
    JWT_ALGORITHM = "HS256"

    def __init__(
        self,
        secret: str,
        database: str,
        token_expire_minutes: int,
    ) -> None:
        # JWT active database name se bind hoti hai; isi liye MongoDB token
        # PostgreSQL/Firestore process mein accept nahi hoti.
        self.secret = secret
        self.database = database
        self.token_expire_minutes = token_expire_minutes

    @staticmethod
    def normalize_email(email: str) -> str:
        """Normalize email before storage and comparison."""
        return email.strip().lower()

    def hash_password(self, password: str) -> str:
        """Create a random-salt password hash; never store plain passwords."""
        # Har signup ka random salt same passwords ke hashes bhi different banata hai.
        salt = secrets.token_hex(16)
        password_hash = self._derive_password_hash(password, salt)
        return f"{salt}:{password_hash}"

    def password_matches(self, password: str, saved_hash: str) -> bool:
        """Compare a login password with its stored hash safely."""
        try:
            salt, expected_hash = saved_hash.split(":", 1)
        except ValueError:
            return False
        actual_hash = self._derive_password_hash(password, salt)
        # compare_digest normal == ke timing differences ko avoid karta hai.
        return hmac.compare_digest(actual_hash, expected_hash)

    def create_token(self, uid: str, email: str) -> str:
        """Create a standard JWT containing user, database, and expiry claims."""
        now = datetime.now(timezone.utc)
        payload = {
            # `sub` standard JWT subject claim hai aur current user UID rakhti hai.
            "sub": uid,
            "email": email,
            "database": self.database,
            "iat": now,
            "exp": now + timedelta(minutes=self.token_expire_minutes),
        }
        # PyJWT standard header.payload.signature format create karti hai.
        return jwt.encode(payload, self.secret, algorithm=self.JWT_ALGORITHM)

    def read_token(self, token: str) -> tuple[str, str]:
        """Verify the JWT and return its selected-database user identity."""
        try:
            payload = jwt.decode(
                token,
                self.secret,
                algorithms=[self.JWT_ALGORITHM],
                options={
                    "require": ["sub", "email", "database", "iat", "exp"]
                },
            )
        except ExpiredSignatureError as error:
            raise ValidationException(
                "Session expired. Please log in again."
            ) from error
        except InvalidTokenError as error:
            raise ValidationException(
                "Invalid session. Please log in again."
            ) from error

        # Signature valid hona enough nahi; token current database ka bhi hona chahiye.
        if payload.get("database") != self.database:
            raise ValidationException(
                f"Please log in or sign up in the {self.database} database."
            )

        uid = payload.get("sub")
        email = payload.get("email")
        if not isinstance(uid, str) or not isinstance(email, str):
            raise ValidationException("Invalid session. Please log in again.")
        return uid, email

    def _derive_password_hash(self, password: str, salt: str) -> str:
        """Run the shared PBKDF2 password derivation."""
        return hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            self.PASSWORD_ITERATIONS,
        ).hex()
