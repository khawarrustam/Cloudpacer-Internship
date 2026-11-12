"""Firestore implementation of the authentication repository contract."""

import hashlib
import uuid
from urllib.parse import unquote

from google.auth.transport.requests import AuthorizedSession

from app.domain.auth import (
    AuthRepository,
    DisplayName,
    EmailAddress,
    GoogleAccountPolicy,
    PasswordPolicy,
    UserData,
    ValidationException,
)
from app.infrastructure.security import AuthSecurity
from app.logging import log_error, log_step


class FirestoreAuthRepository(AuthRepository):
    """What: Store and authenticate users inside Firestore.

    When: Firestore is the selected database for users and todos.
    How: Use an email-derived document key, hashed password, and JWT.
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
        # runQuery Google `sub` lookup deta hai; email ko identity key nahi banate.
        documents_url, encoded_collection = users_url.rsplit("/", 1)
        self.run_query_url = f"{documents_url}:runQuery"
        self.collection_id = unquote(encoded_collection)

    def signup(self, email: str, password: str, name: str) -> UserData:
        """Create a Firestore-only account and return its token."""
        # Domain values har database mein same email/password/name rules lagati hain.
        clean_email = EmailAddress(email).value
        PasswordPolicy.validate_for_signup(password)
        clean_name = DisplayName(name).value
        try:
            if self._find_user(clean_email) is not None:
                raise ValidationException(
                    "This email is already registered in Firestore."
                )
            uid = str(uuid.uuid4())
            # Plain password kabhi document mein nahi jata; sirf salt:hash save hota hai.
            user = {
                "uid": uid,
                "email": clean_email,
                "display_name": clean_name,
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
        clean_email = EmailAddress(email).value
        try:
            user = self._find_user(clean_email)
        except Exception as error:
            log_error("Infrastructure", f"Firestore login failed: {error}")
            raise ValidationException("Firestore login failed.") from error

        if user is None or not self.security.password_matches(
            password,
            user.get("password_hash"),
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

    def login_with_google(self, credential: str) -> UserData:
        """Verify Google, then find/create its user only in Firestore."""
        profile = self.security.verify_google_credential(credential)
        try:
            # Stable Google subject first; email may change during account lifetime.
            user = self._find_google_user(profile.subject)
            if user is None:
                user = self._find_user(profile.email.value)

            if user is None:
                user = {
                    "uid": str(uuid.uuid4()),
                    "email": profile.email.value,
                    "display_name": profile.display_name.value,
                    "google_sub": profile.subject,
                }
            else:
                saved_subject = user.get("google_sub")
                should_link = GoogleAccountPolicy.should_link(
                    saved_subject,
                    profile,
                )
                # Policy allow kare to existing password account Google se link hota hai.
                if should_link:
                    user["google_sub"] = profile.subject

            response = self.session.patch(
                self._user_url(user["email"]),
                json=self._to_document(user),
            )
            response.raise_for_status()
        except ValidationException:
            raise
        except Exception as error:
            log_error("Infrastructure", f"Firestore Google login failed: {error}")
            raise ValidationException("Firestore Google login failed.") from error

        token = self.security.create_token(user["uid"], user["email"])
        log_step(
            "Infrastructure",
            "Firestore Google authentication succeeded.",
            "Firestore Google authentication kamyab ho gayi.",
        )
        return UserData(uid=user["uid"], email=user["email"], token=token)

    def authenticate(self, token: str) -> UserData:
        """Accept the token only if its Firestore user still exists."""
        uid, email = self.security.read_token(token)
        try:
            user = self._find_user(email)
        except Exception as error:
            log_error("Infrastructure", f"Firestore token check failed: {error}")
            raise ValidationException("Firestore session check failed.") from error
        # Valid JWT ke baad live DB check deleted/replaced user ko reject karta hai.
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

    def _find_google_user(self, subject: str) -> dict | None:
        """Return one Firestore user by stable Google subject, or None."""
        query = {
            "structuredQuery": {
                "from": [{"collectionId": self.collection_id}],
                "where": {
                    "fieldFilter": {
                        "field": {"fieldPath": "google_sub"},
                        "op": "EQUAL",
                        "value": {"stringValue": subject},
                    }
                },
                "limit": 1,
            }
        }
        response = self.session.post(self.run_query_url, json=query)
        response.raise_for_status()
        for result in response.json():
            document = result.get("document")
            if document:
                return self._from_document(document)
        return None

    def _user_url(self, email: str) -> str:
        """Build a private, stable document URL for a normalized email."""
        # Deterministic hash direct lookup deta hai; raw email document path mein nahi jati.
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
