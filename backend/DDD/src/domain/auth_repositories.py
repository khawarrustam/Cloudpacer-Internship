"""Authentication contract and its plain result objects."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class UserData:
    uid: str
    email: str
    token: Optional[str] = None


@dataclass(frozen=True)
class LoginData:
    uid: str
    email: str
    id_token: str


class IAuthRepository(ABC):
    @abstractmethod
    def create_user(
        self,
        email: str,
        password: str,
        display_name: str,
    ) -> UserData:
        """Register and return a user."""

    @abstractmethod
    def sign_in(self, email: str, password: str) -> LoginData:
        """Check login details and return a Firebase token."""
