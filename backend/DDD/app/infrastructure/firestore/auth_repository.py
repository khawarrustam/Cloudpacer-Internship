"""Firestore implementation of the authentication repository contract."""

import hashlib
import uuid

from google.auth.transport.requests import AuthorizedSession

from app.domain.auth import AuthRepository, UserData, ValidationException
from app.infrastructure.security import AuthSecurity
from app.logging import log_error, log_step


class FirestoreAuthRepository(AuthRepository):
    """What: Store and authenticate users inside Firestore.

    When: Firestore is the selected database for users and todos.
    How: Use an email-derived document key, hashed password, and signed token.
    """

    def __init__(
        self,
        session: AuthorizedSession,
        users_url: str,
        security: AuthSecurity,
    ) -> None:
        self.session = session
        self.users_url = users_url
        self.security = security

    def signup(self, email: str, password: str, name: str) -> UserData:
        """Create a Firestore-only account and return its token."""
        clean_email = self.security.normalize_email(email)
        try:
            if self._find_user(clean_email) is not None:
                raise ValidationException(
                    "This email is already registered in Firestore."
                )
            uid = str(uuid.uuid4())
            user = {
                "uid": uid,
                "email": clean_email,
                "display_name": name.strip() or "User",
                "password_hash": self.security.hash_password(password),
            }
            response = self.session.patch(
                self._user_url(clean_email),
                json=self._to_document(user),
            )
            response.raise_for_status()
        except ValidationException:
            raise
        except Exception as error:
            log_error("Infrastructure", f"Firestore signup failed: {error}")
            raise ValidationException("Firestore signup failed.") from error

        token = self.security.create_token(uid, clean_email)
        log_step(
            "Infrastructure",
            "Firestore user account created.",
            "Firestore user account ban gaya.",
        )
        return UserData(uid=uid, email=clean_email, token=token)

    def login(self, email: str, password: str) -> UserData:
        """Verify credentials using only Firestore user data."""
        clean_email = self.security.normalize_email(email)
        try:
            user = self._find_user(clean_email)
        except Exception as error:
            log_error("Infrastructure", f"Firestore login failed: {error}")
            raise ValidationException("Firestore login failed.") from error

        if user is None or not self.security.password_matches(
            password,
            user["password_hash"],
        ):
            raise ValidationException("Invalid Firestore email or password.")

        token = self.security.create_token(user["uid"], user["email"])
        log_step(
            "Infrastructure",
            "Firestore authentication succeeded.",
            "Firestore authentication kamyab ho gayi.",
        )
        return UserData(
            uid=user["uid"],
            email=user["email"],
            token=token,
        )

    def authenticate(self, token: str) -> UserData:
        """Accept the token only if its Firestore user still exists."""
        uid, email = self.security.read_token(token)
        try:
            user = self._find_user(email)
        except Exception as error:
            log_error("Infrastructure", f"Firestore token check failed: {error}")
            raise ValidationException("Firestore session check failed.") from error
        if user is None or user["uid"] != uid:
            raise ValidationException("Firestore user no longer exists.")
        return UserData(uid=uid, email=email, token=token)

    def _find_user(self, email: str) -> dict | None:
        """Return one Firestore auth user by email, or None."""
        response = self.session.get(self._user_url(email))
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return self._from_document(response.json())

    def _user_url(self, email: str) -> str:
        """Build a private, stable document URL for a normalized email."""
        email_key = hashlib.sha256(email.encode("utf-8")).hexdigest()
        return f"{self.users_url}/{email_key}"

    @staticmethod
    def _to_document(user: dict) -> dict:
        """Convert simple user values into Firestore REST fields."""
        return {
            "fields": {
                key: {"stringValue": str(value)}
                for key, value in user.items()
            }
        }

    @staticmethod
    def _from_document(document: dict) -> dict:
        """Convert Firestore REST user fields into simple values."""
        return {
            key: value.get("stringValue", "")
            for key, value in document.get("fields", {}).items()
        }
