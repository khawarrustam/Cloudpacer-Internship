"""Authentication application use cases."""

from app.application.dto import AuthOutput, LoginInput, SignupInput
from app.domain.auth import AuthRepository
from app.logging import log_step


class AuthService:
    """What: Coordinate signup, login, and token authentication.

    When: Presentation routes need an authentication use case.
    How: Delegate persistence/security work through AuthRepository.
    """

    def __init__(self, repository: AuthRepository) -> None:
        self.repository = repository

    def signup(self, data: SignupInput) -> AuthOutput:
        """Create a selected-database user and return safe auth output."""
        # Service database ka naam nahi jaanti; injected repository correct
        # adapter mein hashing, storage aur token creation complete karti hai.
        user = self.repository.signup(
            data.email,
            data.password,
            data.display_name,
        )
        log_step("Application", "Signup completed.", "Signup mukammal ho gaya.")
        return self._to_output(user.uid, user.email, user.token)

    def login(self, data: LoginInput) -> AuthOutput:
        """Verify selected-database credentials and return a standard JWT."""
        user = self.repository.login(data.email, data.password)
        log_step("Application", "Login completed.", "Login mukammal ho gaya.")
        return self._to_output(user.uid, user.email, user.token)

    def authenticate(self, token: str) -> AuthOutput:
        """Verify a token against the currently selected database."""
        # Repository token ke sath database user existence bhi confirm karti hai.
        user = self.repository.authenticate(token)
        return self._to_output(user.uid, user.email, user.token)

    @staticmethod
    def _to_output(uid: str, email: str, token: str) -> AuthOutput:
        """Convert repository user data into an application DTO."""
        return AuthOutput(uid=uid, email=email, token=token)
