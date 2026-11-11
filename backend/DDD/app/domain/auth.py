"""Authentication domain data and persistence contract."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


class ValidationException(Exception):
    """A safe authentication/input error that may be returned by the API."""


@dataclass(frozen=True)
class UserData:
    """Database-independent authenticated user returned by repositories."""

    uid: str
    email: str
    token: str


class AuthRepository(ABC):
    """What: Define storage-independent authentication operations.

    When: AuthService needs signup, password login, Google login, or token verification.
    How: Each selected database provides its own concrete implementation.
    """

    # Domain sirf required operations batata hai. Actual Firestore/Mongo/SQL
    # code infrastructure layer mein in methods ko implement karta hai.
    @abstractmethod
    def signup(self, email: str, password: str, name: str) -> UserData:
        """Create one account in the selected database."""
        raise NotImplementedError

    @abstractmethod
    def login(self, email: str, password: str) -> UserData:
        """Verify selected-database credentials."""
        raise NotImplementedError

    @abstractmethod
    def login_with_google(self, credential: str) -> UserData:
        """Verify Google and create or find a user in the selected database."""
        raise NotImplementedError

    @abstractmethod
    def authenticate(self, token: str) -> UserData:
        """Verify a token and confirm its selected-database user exists."""
        raise NotImplementedError
