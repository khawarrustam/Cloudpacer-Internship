"""
=============================================================================
APPLICATION LAYER — Sign In Use Case (Clean Architecture / DDD)
=============================================================================
"""

from dataclasses import dataclass
from src.domain.auth_repositories import IAuthRepository, LoginData


@dataclass(frozen=True)
class SigninCommand:
    email: str
    password: str


class SigninUserUseCase:
    def __init__(self, auth_repo: IAuthRepository):
        self._auth_repo = auth_repo

    def execute(self, cmd: SigninCommand) -> LoginData:
        print(f"   📂 File    : src/application/use_cases/signin_user.py")
        print(f"   🔧 Function: SigninUserUseCase.execute()")
        print(f"   🏛️  Layer   : APPLICATION LAYER (Use Case / Orchestrator)")
        print(f"   📦 Command : SigninCommand(email={cmd.email})")
        print(f"   ➡️  Delegating to Infrastructure Layer")
        print(f"              Calling: self._auth_repo.sign_in()")

        result = self._auth_repo.sign_in(
            email=cmd.email,
            password=cmd.password,
        )

        print(f"   ✅ Infrastructure returned LoginData to Use Case")
        print(f"              UID   : {result.uid}")
        print(f"              Email : {result.email}")
        print(f"   ↩️  Returning LoginData back to Presentation Layer (auth_router.py)")
        return result
