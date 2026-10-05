import abc
from dataclasses import dataclass

@dataclass(frozen=True)
class UserData:
    uid: str
    email: str
    token: str = None

@dataclass(frozen=True)
class LoginData:
    uid: str
    email: str
    id_token: str           # Firebase ID token — verifiable server-side

class IAuthRepository(abc.ABC):
    @abc.abstractmethod
    def create_user(self, email: str, password: str, display_name: str) -> UserData:
        """Register a new user, return UserData with token."""
        pass

    @abc.abstractmethod
    def sign_in(self, email: str, password: str) -> LoginData:
        """Sign in existing user, return LoginData with verifiable ID token."""
        pass
