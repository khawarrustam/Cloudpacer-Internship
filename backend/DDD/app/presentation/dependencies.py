"""FastAPI dependencies for services and the authenticated user."""

from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.application.auth_service import AuthService
from app.application.todo_service import TodoService
from app.domain.auth import ValidationException
from app.logging import log_error, log_step


@dataclass(frozen=True)
class CurrentUser:
    """Verified user identity passed into protected route functions."""

    uid: str
    email: str


bearer = HTTPBearer()


def get_auth_service(request: Request) -> AuthService:
    """What: Provide the configured AuthService to a request.

    When: Auth routes or current_user declare AuthServiceDep.
    How: Read the instance wired once on FastAPI app.state.
    """
    return request.app.state.auth_service


def get_todo_service(request: Request) -> TodoService:
    """Provide the configured TodoService to a request."""
    return request.app.state.todo_service


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
TodoServiceDep = Annotated[TodoService, Depends(get_todo_service)]
CredentialsDep = Annotated[HTTPAuthorizationCredentials, Depends(bearer)]


def current_user(
    credentials: CredentialsDep,
    auth_service: AuthServiceDep,
) -> CurrentUser:
    """What: Verify the Bearer token and return its database user.

    When: Any protected todo endpoint receives a request.
    How: Delegate token/user validation to the selected AuthRepository.
    """
    try:
        result = auth_service.authenticate(credentials.credentials)
        user = CurrentUser(uid=result.uid, email=result.email)
        log_step(
            "Auth",
            f"Token is valid for {user.email}.",
            f"{user.email} ka token valid hai.",
        )
        return user
    except ValidationException as error:
        log_step(
            "Auth",
            "Database session was rejected.",
            "Database session reject ho gaya.",
        )
        raise HTTPException(401, str(error)) from error
    except Exception as error:
        log_error("Auth", f"Token verification failed: {error}")
        raise HTTPException(
            401,
            "Authentication failed. Please log in again.",
        ) from error


CurrentUserDep = Annotated[CurrentUser, Depends(current_user)]
