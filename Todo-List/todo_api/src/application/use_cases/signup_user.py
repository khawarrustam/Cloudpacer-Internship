"""Use case for registering a user."""

from dataclasses import dataclass

from src.domain.auth_repositories import IAuthRepository, UserData
from src.shared.console import print_step


@dataclass(frozen=True)
class SignupCommand:
    email: str
    password: str
    display_name: str


class SignupUserUseCase:
    def __init__(self, auth_repo: IAuthRepository):
        self.auth_repo = auth_repo

    def execute(self, command: SignupCommand) -> UserData:
        print_step(
            "Application",
            f"Creating account for {command.email}.",
            f"{command.email} ka account ban raha hai.",
        )
        user = self.auth_repo.create_user(
            email=command.email,
            password=command.password,
            display_name=command.display_name,
        )
        print_step(
            "Application",
            "User account created.",
            "User account ban gaya.",
        )
        return user
