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
from src.shared.console import print_error, print_flow

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
    print_flow(
        source="Frontend -> POST /auth/signup",
        destination="src/presentation/api/auth_router.py -> signup",
        data=f"email={request.email}, password=hidden",
        english="The frontend sent signup data to the auth router.",
        roman_urdu="Frontend ne signup data auth router ko bheja.",
    )
    command = SignupCommand(
        email=request.email,
        password=request.password,
        display_name=request.display_name,
    )

    try:
        user = use_case.execute(command)
        response = AuthResponse(
            uid=user.uid,
            email=user.email,
            message="User created successfully",
            token=user.token,
        )
        print_flow(
            source="src/application/use_cases/signup_user.py",
            destination="Frontend <- HTTP 201 response",
            data=f"uid={user.uid}, token=hidden",
            english="Safe signup response is going back to the frontend.",
            roman_urdu="Safe signup response frontend ko wapas ja raha hai.",
        )
        return response
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
    print_flow(
        source="Frontend -> POST /auth/login",
        destination="src/presentation/api/auth_router.py -> login",
        data=f"email={request.email}, password=hidden",
        english="The frontend sent login data to the auth router.",
        roman_urdu="Frontend ne login data auth router ko bheja.",
    )
    command = SigninCommand(email=request.email, password=request.password)

    try:
        login_data = use_case.execute(command)
        response = LoginResponse(
            uid=login_data.uid,
            email=login_data.email,
            token=login_data.id_token,
            message="Login successful",
        )
        print_flow(
            source="src/application/use_cases/signin_user.py",
            destination="Frontend <- HTTP 200 response",
            data=f"uid={login_data.uid}, token=hidden",
            english="Safe login response is going back to the frontend.",
            roman_urdu="Safe login response frontend ko wapas ja raha hai.",
        )
        return response
    except ValidationException as error:
        print_error("API", str(error), f"Login fail hua: {error}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
        ) from error
