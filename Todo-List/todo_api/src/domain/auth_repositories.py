import abc
from dataclasses import dataclass

@dataclass(frozen=True)
class UserData:
    uid: str
    email: str
    token: str = None

class IAuthRepository(abc.ABC):
    @abc.abstractmethod
    def create_user(self, email: str, password: str, display_name: str) -> UserData:
        pass
