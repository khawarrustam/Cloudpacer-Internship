"""Use case for registering a user."""

from dataclasses import dataclass

from src.domain.auth_repositories import IAuthRepository, UserData
from src.shared.console import module_file, print_flow, print_step


@dataclass(frozen=True)
class SignupCommand:
    email: str
    password: str
    display_name: str


class SignupUserUseCase:
    def __init__(self, auth_repo: IAuthRepository):
        self.auth_repo = auth_repo

    def execute(self, command: SignupCommand) -> UserData:
        print_flow(
            source="src/presentation/api/auth_router.py",
            destination="src/application/use_cases/signup_user.py",
            data=f"email={command.email}, display_name={command.display_name}",
            english="The router sent safe signup data to the use case.",
            roman_urdu="Router ne safe signup data use case ko bheja.",
        )
        print_flow(
            source="src/application/use_cases/signup_user.py",
            destination=module_file(self.auth_repo),
            data=f"email={command.email}, password=hidden",
            english="Sending signup data to the authentication repository.",
            roman_urdu="Signup data authentication repository ko ja raha hai.",
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
