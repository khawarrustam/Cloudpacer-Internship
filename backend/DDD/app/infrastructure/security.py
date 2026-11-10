"""Shared password hashing and signed-token implementation."""

import base64
import hashlib
import hmac
import json
import secrets
import time

from app.domain.auth import ValidationException


class AuthSecurity:
    """What: Hash passwords and sign database-bound login tokens.

    When: A concrete AuthRepository signs up, logs in, or verifies a user.
    How: PBKDF2 protects passwords and HMAC-SHA256 protects token payloads.
    """

    PASSWORD_ITERATIONS = 120_000

    def __init__(
        self,
        secret: str,
        database: str,
        token_expire_minutes: int,
    ) -> None:
        # Same object active database name token mein bind karta hai; isi liye
        # MongoDB token PostgreSQL/Firestore process mein accept nahi hota.
        self.secret = secret.encode("utf-8")
        self.database = database
        self.token_expire_seconds = token_expire_minutes * 60

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
        """Create a signed token containing user and selected database."""
        # Payload readable Base64 hota hai; HMAC signature modification detect karti hai.
        payload = {
            "uid": uid,
            "email": email,
            "database": self.database,
            "expires_at": int(time.time()) + self.token_expire_seconds,
        }
        payload_bytes = json.dumps(
            payload,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        encoded_payload = self._encode(payload_bytes)
        signature = self._sign(encoded_payload)
        # Final format: base64url(payload).base64url(signature)
        return f"{encoded_payload}.{self._encode(signature)}"

    def read_token(self, token: str) -> tuple[str, str]:
        """Verify signature, database, expiry, UID, and email."""
        payload = self._read_payload(token)
        # Signature valid hona enough nahi; token current database ka bhi hona chahiye.
        if payload.get("database") != self.database:
            raise ValidationException(
                f"Please log in or sign up in the {self.database} database."
            )
        if payload.get("expires_at", 0) < int(time.time()):
            raise ValidationException("Session expired. Please log in again.")

        uid = payload.get("uid")
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

    def _read_payload(self, token: str) -> dict:
        """Decode and verify the signed JSON payload."""
        try:
            encoded_payload, encoded_signature = token.split(".", 1)
            received_signature = self._decode(encoded_signature)
            # Payload ka aik character bhi change ho toh expected signature match nahi karegi.
            if not hmac.compare_digest(
                received_signature,
                self._sign(encoded_payload),
            ):
                raise ValidationException("Invalid session. Please log in again.")
            return json.loads(self._decode(encoded_payload).decode("utf-8"))
        except ValidationException:
            raise
        except Exception as error:
            raise ValidationException(
                "Invalid session. Please log in again."
            ) from error

    def _sign(self, encoded_payload: str) -> bytes:
        """Sign one encoded payload with the application secret."""
        return hmac.new(
            self.secret,
            encoded_payload.encode("utf-8"),
            hashlib.sha256,
        ).digest()

    @staticmethod
    def _encode(value: bytes) -> str:
        return base64.urlsafe_b64encode(value).rstrip(b"=").decode("utf-8")

    @staticmethod
    def _decode(value: str) -> bytes:
        padding = "=" * (-len(value) % 4)
        return base64.urlsafe_b64decode(value + padding)
