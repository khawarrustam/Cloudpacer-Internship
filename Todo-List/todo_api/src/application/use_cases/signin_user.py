"""Use case for signing in a user."""

from dataclasses import dataclass

from src.domain.auth_repositories import IAuthRepository, LoginData
from src.shared.console import print_step


@dataclass(frozen=True)
class SigninCommand:
    email: str
    password: str


class SigninUserUseCase:
    def __init__(self, auth_repo: IAuthRepository):
        self.auth_repo = auth_repo

    def execute(self, command: SigninCommand) -> LoginData:
        print_step(
            "Application",
            f"Signing in {command.email}.",
            f"{command.email} login kar raha hai.",
        )
        login_data = self.auth_repo.sign_in(
            email=command.email,
            password=command.password,
        )
        print_step(
            "Application",
            "Sign-in completed.",
            "Login mukammal ho gaya.",
        )
        return login_data
