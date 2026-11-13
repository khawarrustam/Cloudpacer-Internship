"""Presentation controllers for authentication requests."""

from fastapi import HTTPException

from app.application.auth_service import AuthService
from app.application.dto import GoogleLoginInput, LoginInput, SignupInput
from app.domain.auth import ValidationException
from app.logging import log_step
from app.presentation.schemas import (
    AuthResponse,
    GoogleLoginRequest,
    LoginRequest,
    SignupRequest,
)


def signup_user(
    request: SignupRequest,
    auth_service: AuthService,
) -> AuthResponse:
    """Map an HTTP signup request to the application signup use case."""
    log_step("Presentation", "Signup request received.", "Signup request mil gayi.")
    try:
        result = auth_service.signup(SignupInput(
            email=request.email,
            password=request.password,
            display_name=request.display_name,
        ))
        return _auth_response(
            result.uid,
            result.email,
            result.token,
            "User created successfully",
        )
    except ValidationException as error:
        raise HTTPException(400, str(error)) from error


def login_user(
    request: LoginRequest,
    auth_service: AuthService,
) -> AuthResponse:
    """Map password-login HTTP data and translate its error to HTTP 401."""
    log_step("Presentation", "Login request received.", "Login request mil gayi.")
    try:
        result = auth_service.login(LoginInput(
            email=request.email,
            password=request.password,
        ))
        return _auth_response(
            result.uid,
            result.email,
            result.token,
            "Login successful",
        )
    except ValidationException as error:
        raise HTTPException(401, str(error)) from error


def google_login_user(
    request: GoogleLoginRequest,
    auth_service: AuthService,
) -> AuthResponse:
    """Pass a Google credential to the use case and build its HTTP response."""
    log_step(
        "Presentation",
        "Google login request received.",
        "Google login request mil gayi.",
    )
    try:
        result = auth_service.login_with_google(
            GoogleLoginInput(credential=request.credential)
        )
        return _auth_response(
            result.uid,
            result.email,
            result.token,
            "Google login successful",
        )
    except ValidationException as error:
        raise HTTPException(401, str(error)) from error


def _auth_response(
    uid: str,
    email: str,
    token: str,
    message: str,
) -> AuthResponse:
    """Keep application-output to HTTP-response mapping in one place."""
    return AuthResponse(uid=uid, email=email, token=token, message=message)
