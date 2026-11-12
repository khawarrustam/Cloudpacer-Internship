"""MongoDB implementation of the authentication repository contract."""

import uuid

from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError

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


class MongoAuthRepository(AuthRepository):
    """What: Store and authenticate users inside MongoDB.

    When: MongoDB is the selected database for users and todos.
    How: Use a unique email index, hashed passwords, and database-bound JWTs.
    """

    def __init__(
        self,
        collection: Collection,
        security: AuthSecurity,
    ) -> None:
        self.collection = collection
        # Unique index selected Mongo database mein duplicate normalized email rokta hai.
        self.collection.create_index("email", unique=True)
        # Sparse index Google-only/link records par stable subject unique rakhta hai.
        self.collection.create_index("google_sub", unique=True, sparse=True)
        self.security = security

    def signup(self, email: str, password: str, name: str) -> UserData:
        """Create a MongoDB-only account and return its token."""
        clean_email = EmailAddress(email).value
        PasswordPolicy.validate_for_signup(password)
        clean_name = DisplayName(name).value
        uid = str(uuid.uuid4())
        # Application UUID ko Mongo _id banane se identity three DBs mein same format rakhti hai.
        user = {
            "_id": uid,
            "email": clean_email,
            "display_name": clean_name,
            "password_hash": self.security.hash_password(password),
        }
        try:
            self.collection.insert_one(user)
        except DuplicateKeyError as error:
            raise ValidationException(
                "This email is already registered in MongoDB."
            ) from error
        except Exception as error:
            log_error("Infrastructure", f"MongoDB signup failed: {error}")
            raise ValidationException("MongoDB signup failed.") from error

        token = self.security.create_token(uid, clean_email)
        log_step(
            "Infrastructure",
            "MongoDB user account created.",
            "MongoDB user account ban gaya.",
        )
        return UserData(uid=uid, email=clean_email, token=token)

    def login(self, email: str, password: str) -> UserData:
        """Verify credentials using only MongoDB user data."""
        clean_email = EmailAddress(email).value
        user = self.collection.find_one({"email": clean_email})
        if user is None or not self.security.password_matches(
            password,
            user.get("password_hash"),
        ):
            raise ValidationException("Invalid MongoDB email or password.")

        uid = str(user["_id"])
        token = self.security.create_token(uid, clean_email)
        log_step(
            "Infrastructure",
            "MongoDB authentication succeeded.",
            "MongoDB authentication kamyab ho gayi.",
        )
        return UserData(uid=uid, email=clean_email, token=token)

    def login_with_google(self, credential: str) -> UserData:
        """Verify Google, then find/create its user only in MongoDB."""
        profile = self.security.verify_google_credential(credential)
        try:
            # Stable Google subject first; email fallback existing password account links.
            user = self.collection.find_one({"google_sub": profile.subject})
            if user is None:
                user = self.collection.find_one({"email": profile.email.value})

            if user is None:
                user = {
                    "_id": str(uuid.uuid4()),
                    "email": profile.email.value,
                    "display_name": profile.display_name.value,
                    "google_sub": profile.subject,
                }
                self.collection.insert_one(user)
            else:
                saved_subject = user.get("google_sub")
                should_link = GoogleAccountPolicy.should_link(
                    saved_subject,
                    profile,
                )
                if should_link:
                    self.collection.update_one(
                        {"_id": user["_id"]},
                        {"$set": {"google_sub": profile.subject}},
                    )
                    user["google_sub"] = profile.subject
        except ValidationException:
            raise
        except DuplicateKeyError as error:
            raise ValidationException(
                "This Google account already exists in MongoDB."
            ) from error
        except Exception as error:
            log_error("Infrastructure", f"MongoDB Google login failed: {error}")
            raise ValidationException("MongoDB Google login failed.") from error

        uid = str(user["_id"])
        email = str(user["email"])
        token = self.security.create_token(uid, email)
        log_step(
            "Infrastructure",
            "MongoDB Google authentication succeeded.",
            "MongoDB Google authentication kamyab ho gayi.",
        )
        return UserData(uid=uid, email=email, token=token)

    def authenticate(self, token: str) -> UserData:
        """Accept the token only if its MongoDB user still exists."""
        uid, email = self.security.read_token(token)
        # UID aur email dono match karna stale/deleted account reuse ko avoid karta hai.
        user = self.collection.find_one({"_id": uid, "email": email})
        if user is None:
            raise ValidationException("MongoDB user no longer exists.")
        return UserData(uid=uid, email=email, token=token)
