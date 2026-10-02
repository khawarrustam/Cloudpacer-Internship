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
        print(f"   📂 File    : src/application/use_cases/signup_user.py")
        print(f"   🔧 Function: SignupUserUseCase.execute()")
        print(f"   🏛️  Layer   : APPLICATION LAYER (Use Case / Orchestrator)")
        print(f"   📦 Command : SignupCommand(email={cmd.email}, display_name={cmd.display_name})")
        print(f"   ➡️  Delegating to Infrastructure Layer")
        print(f"              Calling: self._auth_repo.create_user()")
        print(f"              📂 Repo : src/infrastructure/repositories/firebase_auth_repo.py")

        result = self._auth_repo.create_user(
            email=cmd.email,
            password=cmd.password,
            display_name=cmd.display_name
        )

        print(f"   ✅ Infrastructure returned UserData to Use Case")
        print(f"              UID   : {result.uid}")
        print(f"              Email : {result.email}")
        print(f"   ↩️  Returning UserData back to Presentation Layer (auth_router.py)")

        return result
