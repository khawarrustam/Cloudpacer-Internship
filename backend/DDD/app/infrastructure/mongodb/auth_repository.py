"""MongoDB implementation of the authentication repository contract."""

import uuid

from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError

from app.domain.auth import AuthRepository, UserData, ValidationException
from app.infrastructure.security import AuthSecurity
from app.logging import log_error, log_step


class MongoAuthRepository(AuthRepository):
    """What: Store and authenticate users inside MongoDB.

    When: MongoDB is the selected database for users and todos.
    How: Use a unique email index, hashed passwords, and database-bound tokens.
    """

    def __init__(
        self,
        collection: Collection,
        security: AuthSecurity,
    ) -> None:
        self.collection = collection
        self.collection.create_index("email", unique=True)
        self.security = security

    def signup(self, email: str, password: str, name: str) -> UserData:
        """Create a MongoDB-only account and return its token."""
        clean_email = self.security.normalize_email(email)
        uid = str(uuid.uuid4())
        user = {
            "_id": uid,
            "email": clean_email,
            "display_name": name.strip() or "User",
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
        clean_email = self.security.normalize_email(email)
        user = self.collection.find_one({"email": clean_email})
        if user is None or not self.security.password_matches(
            password,
            user["password_hash"],
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

    def authenticate(self, token: str) -> UserData:
        """Accept the token only if its MongoDB user still exists."""
        uid, email = self.security.read_token(token)
        user = self.collection.find_one({"_id": uid, "email": email})
        if user is None:
            raise ValidationException("MongoDB user no longer exists.")
        return UserData(uid=uid, email=email, token=token)
