from dataclasses import dataclass
from src.domain.auth_repositories import IAuthRepository, UserData

@dataclass(frozen=True)
class SignupCommand:
    email: str
    password: str
    display_name: str

class SignupUserUseCase:
    def __init__(self, auth_repo: IAuthRepository):
        self._auth_repo = auth_repo

    def execute(self, cmd: SignupCommand) -> UserData:
        return self._auth_repo.create_user(
            email=cmd.email,
            password=cmd.password,
            display_name=cmd.display_name
        )
