"""HTTP routes for signup and login."""

from fastapi import APIRouter, Depends, HTTPException, status

from src.application.use_cases.signin_user import SigninCommand, SigninUserUseCase
from src.application.use_cases.signup_user import SignupCommand, SignupUserUseCase
from src.domain.exceptions import ValidationException
from src.presentation.api.auth_schemas import (
    AuthResponse,
    LoginRequest,
    LoginResponse,
    SignupRequest,
)
from src.shared.console import print_error, print_step

router = APIRouter(prefix="/auth", tags=["Auth"])


# English: bootstrap.py replaces these placeholders with real use cases.
# Roman Urdu: bootstrap.py in placeholders ki jagah real use cases deta hai.
def get_signup_use_case() -> SignupUserUseCase:
    raise NotImplementedError


def get_signin_use_case() -> SigninUserUseCase:
    raise NotImplementedError


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup(
    request: SignupRequest,
    use_case: SignupUserUseCase = Depends(get_signup_use_case),
):
    print_step(
        "API",
        f"Signup request received for {request.email}.",
        f"{request.email} ke liye signup request mili.",
    )
    command = SignupCommand(
        email=request.email,
        password=request.password,
        display_name=request.display_name,
    )

    try:
        user = use_case.execute(command)
        return AuthResponse(
            uid=user.uid,
            email=user.email,
            message="User created successfully",
            token=user.token,
        )
    except ValidationException as error:
        print_error("API", str(error), f"Signup fail hua: {error}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.post("/login", response_model=LoginResponse)
def login(
    request: LoginRequest,
    use_case: SigninUserUseCase = Depends(get_signin_use_case),
):
    print_step(
        "API",
        f"Login request received for {request.email}.",
        f"{request.email} ke liye login request mili.",
    )
    command = SigninCommand(email=request.email, password=request.password)

    try:
        login_data = use_case.execute(command)
        return LoginResponse(
            uid=login_data.uid,
            email=login_data.email,
            token=login_data.id_token,
            message="Login successful",
        )
    except ValidationException as error:
        print_error("API", str(error), f"Login fail hua: {error}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
        ) from error
