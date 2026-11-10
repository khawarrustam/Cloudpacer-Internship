"""HTTP routes for signup and login."""

from fastapi import APIRouter, HTTPException

from app.application.dto import LoginInput, SignupInput
from app.domain.auth import ValidationException
from app.logging import log_step
from app.presentation.dependencies import AuthServiceDep
from app.presentation.schemas import AuthResponse, LoginRequest, SignupRequest


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup", response_model=AuthResponse, status_code=201)
def signup(
    request: SignupRequest,
    auth_service: AuthServiceDep,
) -> AuthResponse:
    """What: Create an account in the selected database.

    When: The client submits POST /auth/signup.
    How: Validate HTTP data, call AuthService, and map errors to HTTP 400.
    """
    log_step("Presentation", "Signup request received.", "Signup request mil gayi.")
    try:
        # HTTP schema ko framework-independent application input DTO mein map karte hain.
        result = auth_service.signup(SignupInput(
            email=request.email,
            password=request.password,
            display_name=request.display_name,
        ))
        # Application output ko public HTTP response contract mein map karte hain.
        return AuthResponse(
            uid=result.uid,
            email=result.email,
            token=result.token,
            message="User created successfully",
        )
    except ValidationException as error:
        raise HTTPException(400, str(error)) from error


@router.post("/login", response_model=AuthResponse)
def login(
    request: LoginRequest,
    auth_service: AuthServiceDep,
) -> AuthResponse:
    """Authenticate from the selected database and return its token."""
    log_step("Presentation", "Login request received.", "Login request mil gayi.")
    try:
        # Route credentials verify nahi karti; use case ko delegate karti hai.
        result = auth_service.login(LoginInput(
            email=request.email,
            password=request.password,
        ))
        return AuthResponse(
            uid=result.uid,
            email=result.email,
            token=result.token,
            message="Login successful",
        )
    except ValidationException as error:
        raise HTTPException(401, str(error)) from error
