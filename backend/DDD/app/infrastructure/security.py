"""Shared password hashing and standard JWT implementation."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import secrets

from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2 import id_token as google_id_token
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from app.domain.auth import ValidationException


@dataclass(frozen=True)
class GoogleProfile:
    """Verified Google identity values needed by database repositories."""

    subject: str
    email: str
    display_name: str
    can_link_existing_email: bool


class AuthSecurity:
    """What: Handle passwords, Google identity, and our database-bound JWTs.

    When: A concrete AuthRepository signs up, logs in, or verifies a user.
    How: PBKDF2, google-auth, and PyJWT provide the security operations.
    """

    PASSWORD_ITERATIONS = 120_000
    JWT_ALGORITHM = "HS256"

    def __init__(
        self,
        secret: str,
        database: str,
        token_expire_minutes: int,
        google_client_id: str,
    ) -> None:
        # JWT active database name se bind hoti hai; isi liye MongoDB token
        # PostgreSQL/Firestore process mein accept nahi hoti.
        self.secret = secret
        self.database = database
        self.token_expire_minutes = token_expire_minutes
        self.google_client_id = google_client_id.strip()
        # Reusing one transport object keeps the verification call easy to test.
        self.google_request = GoogleRequest()

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

    def password_matches(self, password: str, saved_hash: str | None) -> bool:
        """Compare a login password with its stored hash safely."""
        # Google-only accounts intentionally have no password hash.
        if not isinstance(saved_hash, str):
            return False
        try:
            salt, expected_hash = saved_hash.split(":", 1)
        except ValueError:
            return False
        actual_hash = self._derive_password_hash(password, salt)
        # compare_digest normal == ke timing differences ko avoid karta hai.
        return hmac.compare_digest(actual_hash, expected_hash)

    def verify_google_credential(self, credential: str) -> GoogleProfile:
        """Verify one Google ID token and return its trusted basic profile."""
        if (
            not self.google_client_id
            or self.google_client_id.startswith("replace-with-")
        ):
            raise ValidationException(
                "Google login is not configured. Add GOOGLE_CLIENT_ID."
            )

        try:
            # google-auth checks Google's signature, audience, issuer and expiry.
            claims = google_id_token.verify_oauth2_token(
                credential,
                self.google_request,
                self.google_client_id,
            )
        except ValueError as error:
            raise ValidationException(
                "Invalid Google login. Please try again."
            ) from error
        except Exception as error:
            raise ValidationException(
                "Google login is temporarily unavailable."
            ) from error

        # `sub` Google account ki stable identity hai; email display/contact value hai.
        subject = claims.get("sub")
        email = claims.get("email")
        if (
            not isinstance(subject, str)
            or not subject
            or not isinstance(email, str)
            or not email
            or claims.get("email_verified") is not True
        ):
            raise ValidationException("Google account email is not verified.")

        clean_email = self.normalize_email(email)
        display_name = str(claims.get("name") or clean_email.split("@", 1)[0])
        # Gmail/Workspace email par Google authoritative hota hai; sirf in cases
        # mein an existing password account ko automatically link karte hain.
        can_link_existing_email = (
            clean_email.endswith("@gmail.com") or bool(claims.get("hd"))
        )
        return GoogleProfile(
            subject=subject,
            email=clean_email,
            display_name=display_name,
            can_link_existing_email=can_link_existing_email,
        )

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
