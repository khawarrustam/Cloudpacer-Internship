"""Thin HTTP routes for authentication endpoints."""

from fastapi import APIRouter

from app.presentation.controllers.auth_controller import (
    google_login_user,
    login_user,
    signup_user,
)
from app.presentation.dependencies import AuthServiceDep
from app.presentation.schemas import (
    AuthResponse,
    GoogleLoginRequest,
    LoginRequest,
    SignupRequest,
)


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup", response_model=AuthResponse, status_code=201)
def signup(request: SignupRequest, auth_service: AuthServiceDep) -> AuthResponse:
    """Delegate the signup endpoint to its presentation controller."""
    return signup_user(request, auth_service)


@router.post("/login", response_model=AuthResponse)
def login(request: LoginRequest, auth_service: AuthServiceDep) -> AuthResponse:
    """Delegate the password-login endpoint to its controller."""
    return login_user(request, auth_service)


@router.post("/google", response_model=AuthResponse)
def login_with_google(
    request: GoogleLoginRequest,
    auth_service: AuthServiceDep,
) -> AuthResponse:
    """Delegate the Google-login endpoint to its controller."""
    return google_login_user(request, auth_service)
