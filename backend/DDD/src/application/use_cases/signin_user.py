"""Use case for signing in a user."""

from dataclasses import dataclass

from src.domain.auth_repositories import IAuthRepository, LoginData
from src.shared.console import module_file, print_flow, print_step


@dataclass(frozen=True)
class SigninCommand:
    email: str
    password: str


class SigninUserUseCase:
    def __init__(self, auth_repo: IAuthRepository):
        self.auth_repo = auth_repo

    def execute(self, command: SigninCommand) -> LoginData:
        print_flow(
            source="src/presentation/api/auth_router.py",
            destination="src/application/use_cases/signin_user.py",
            data=f"email={command.email}, password=hidden",
            english="The router sent safe login data to the use case.",
            roman_urdu="Router ne safe login data use case ko bheja.",
        )
        print_flow(
            source="src/application/use_cases/signin_user.py",
            destination=module_file(self.auth_repo),
            data=f"email={command.email}, password=hidden",
            english="Sending login data to the authentication repository.",
            roman_urdu="Login data authentication repository ko ja raha hai.",
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
