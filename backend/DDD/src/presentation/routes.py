"""Presentation layer: FastAPI routes and Firebase token verification."""

from dataclasses import dataclass

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth

from src.application.dto import (
    CreateTodoInput,
    LoginInput,
    SignupInput,
    TodoActionInput,
    TodoOutput,
)
from src.application.use_cases import AuthUseCases, TodoUseCases
from src.domain.models import DomainError, TodoNotFoundError, ValidationException
from src.logs import log_error, log_step
from src.presentation.dto import (
    AuthResponse,
    CreateTodoRequest,
    LoginRequest,
    SignupRequest,
    TodoResponse,
)


@dataclass(frozen=True)
class CurrentUser:
    """User identity extracted from a verified Firebase token."""
    uid: str
    email: str


auth_router = APIRouter(prefix="/auth", tags=["Auth"])
todo_router = APIRouter(prefix="/todos", tags=["Todos"])
bearer = HTTPBearer()
todo_use_cases: TodoUseCases | None = None
auth_use_cases: AuthUseCases | None = None


def configure_use_cases(todo: TodoUseCases, authentication: AuthUseCases) -> None:
    """Give the route functions their configured application use cases.

    Kyun: Routes repositories khud create nahi karti; main.py selected database
    ko use cases mein inject karke yahan pass karta hai.
    """
    global todo_use_cases, auth_use_cases
    todo_use_cases = todo
    auth_use_cases = authentication


def current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
) -> CurrentUser:
    """Verify the Bearer token and return the logged-in user's identity.

    Kyun: Har protected todo route ko trusted UID chahiye taa-ke aik user doosre
    user ke todos read ya change na kar sake.
    """
    try:
        token = auth.verify_id_token(
            credentials.credentials,
            clock_skew_seconds=60,
        )
        user = CurrentUser(
            uid=token["uid"],
            email=token.get("email", ""),
        )
        log_step(
            "Auth",
            f"Token is valid for {user.email}.",
            f"{user.email} ka token valid hai.",
        )
        return user
    except auth.ExpiredIdTokenError:
        log_step(
            "Auth",
            "Session expired. Re-authentication required.",
            "Session expire ho gaya. Dobara login karna hoga.",
        )
        raise HTTPException(401, "Session expired. Please log in again.")
    except Exception as error:
        log_error("Auth", f"Token verification failed: {error}")
        raise HTTPException(401, "Authentication failed. Please log in again.") from error


@auth_router.post("/signup", response_model=AuthResponse, status_code=201)
def signup(request: SignupRequest) -> AuthResponse:
    """Accept signup form data and call the signup application use case."""
    log_step("Presentation", "Signup request received.", "Signup request mil gayi.")
    try:
        signup_data = SignupInput(
            email=request.email,
            password=request.password,
            display_name=request.display_name,
        )
        result = auth_use_cases.signup(signup_data)
        return AuthResponse(
            uid=result.uid,
            email=result.email,
            token=result.token,
            message="User created successfully",
        )
    except ValidationException as error:
        raise HTTPException(400, str(error)) from error


@auth_router.post("/login", response_model=AuthResponse)
def login(request: LoginRequest) -> AuthResponse:
    """Accept email/password and return a Firebase authentication token."""
    log_step("Presentation", "Login request received.", "Login request mil gayi.")
    try:
        login_data = LoginInput(
            email=request.email,
            password=request.password,
        )
        result = auth_use_cases.login(login_data)
        return AuthResponse(
            uid=result.uid,
            email=result.email,
            token=result.token,
            message="Login successful",
        )
    except ValidationException as error:
        raise HTTPException(401, str(error)) from error


@todo_router.get("", response_model=list[TodoResponse])
def list_todos(
    user: CurrentUser = Depends(current_user),
) -> list[TodoOutput]:
    """Return todos belonging only to the verified current user."""
    log_step("Presentation", "Todo list requested.", "Todo list mangi gayi.")
    return todo_use_cases.list(user.uid)


@todo_router.post("", response_model=TodoResponse, status_code=201)
def create_todo(
    request: CreateTodoRequest,
    user: CurrentUser = Depends(current_user),
) -> TodoOutput:
    """Validate the HTTP body and ask the application layer to create a todo."""
    log_step(
        "Presentation",
        "Create todo request received.",
        "Create todo request mil gayi.",
    )
    try:
        todo_data = CreateTodoInput(
            title=request.title,
            priority=request.priority,
            owner_uid=user.uid,
        )
        return todo_use_cases.create(todo_data)
    except DomainError as error:
        raise HTTPException(400, str(error)) from error


@todo_router.patch("/{todo_id}/complete", response_model=TodoResponse)
def complete_todo(
    todo_id: str,
    user: CurrentUser = Depends(current_user),
) -> TodoOutput:
    """Complete one owned todo and convert domain errors into HTTP errors."""
    log_step(
        "Presentation",
        "Complete todo request received.",
        "Complete todo request mil gayi.",
    )
    try:
        todo_data = TodoActionInput(
            todo_id=todo_id,
            owner_uid=user.uid,
        )
        return todo_use_cases.complete(todo_data)
    except TodoNotFoundError as error:
        raise HTTPException(404, str(error)) from error
    except DomainError as error:
        raise HTTPException(400, str(error)) from error


@todo_router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(
    todo_id: str,
    user: CurrentUser = Depends(current_user),
) -> None:
    """Delete one owned todo or return HTTP 404 when it does not exist."""
    log_step(
        "Presentation",
        "Delete todo request received.",
        "Delete todo request mil gayi.",
    )
    try:
        todo_data = TodoActionInput(
            todo_id=todo_id,
            owner_uid=user.uid,
        )
        todo_use_cases.delete(todo_data)
    except TodoNotFoundError as error:
        raise HTTPException(404, str(error)) from error
    return None
