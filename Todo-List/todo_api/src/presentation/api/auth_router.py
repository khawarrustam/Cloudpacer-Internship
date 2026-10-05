from fastapi import APIRouter, Depends, HTTPException, status
from src.presentation.api.auth_schemas import (
    SignupRequest, AuthResponse, LoginRequest, LoginResponse
)
from src.application.use_cases.signup_user import SignupUserUseCase, SignupCommand
from src.application.use_cases.signin_user import SigninUserUseCase, SigninCommand
from src.infrastructure.repositories.firebase_auth_repo import FirebaseAuthRepository
from src.domain.exceptions import ValidationException

router = APIRouter(prefix="/auth", tags=["Auth"])


# ---------------------------------------------------------------------------
# DEPENDENCY PROVIDERS
# ---------------------------------------------------------------------------
def get_signup_use_case() -> SignupUserUseCase:
    print(f"   🔧 [DDD] Dependency Injection: get_signup_use_case()")
    print(f"           📂 File: src/presentation/api/auth_router.py")
    auth_repo = FirebaseAuthRepository()
    return SignupUserUseCase(auth_repo)


def get_signin_use_case() -> SigninUserUseCase:
    print(f"   🔧 [DDD] Dependency Injection: get_signin_use_case()")
    print(f"           📂 File: src/presentation/api/auth_router.py")
    auth_repo = FirebaseAuthRepository()
    return SigninUserUseCase(auth_repo)


# ---------------------------------------------------------------------------
# POST /auth/signup — Register new user
# ---------------------------------------------------------------------------
@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup(req: SignupRequest, use_case: SignupUserUseCase = Depends(get_signup_use_case)):
    print("\n" + "="*60)
    print("📥 [DDD] REQUEST RECEIVED — PRESENTATION LAYER")
    print("="*60)
    print(f"   📂 File    : src/presentation/api/auth_router.py")
    print(f"   🔧 Function: signup()")
    print(f"   🌐 Route   : POST /auth/signup")
    print(f"   📧 Email   : {req.email}")
    print(f"   👤 Name    : {req.display_name}")
    print(f"   🔑 Password: {'*' * len(req.password)} ({len(req.password)} chars)")
    print("-"*60)

    cmd = SignupCommand(
        email=req.email,
        password=req.password,
        display_name=req.display_name
    )

    try:
        user_data = use_case.execute(cmd)
        response = AuthResponse(
            uid=user_data.uid,
            email=user_data.email,
            message="User created successfully",
            token=user_data.token
        )
        print(f"   📤 Sending 201 Created | uid={user_data.uid}")
        print("="*60 + "\n")
        return response

    except ValidationException as e:
        print(f"   ❌ ValidationException: {str(e)}")
        print("="*60 + "\n")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        print(f"   ❌ Unexpected Error: {type(e).__name__} — {str(e)}")
        print("="*60 + "\n")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ---------------------------------------------------------------------------
# POST /auth/login — Sign in existing user
# ---------------------------------------------------------------------------
@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
def login(req: LoginRequest, use_case: SigninUserUseCase = Depends(get_signin_use_case)):
    print("\n" + "="*60)
    print("📥 [DDD] REQUEST RECEIVED — PRESENTATION LAYER")
    print("="*60)
    print(f"   📂 File    : src/presentation/api/auth_router.py")
    print(f"   🔧 Function: login()")
    print(f"   🌐 Route   : POST /auth/login")
    print(f"   📧 Email   : {req.email}")
    print("-"*60)

    cmd = SigninCommand(email=req.email, password=req.password)

    try:
        login_data = use_case.execute(cmd)
        response = LoginResponse(
            uid=login_data.uid,
            email=login_data.email,
            token=login_data.id_token,
            message="Login successful"
        )
        print(f"   📤 Sending 200 OK | uid={login_data.uid}")
        print("="*60 + "\n")
        return response

    except ValidationException as e:
        print(f"   ❌ ValidationException: {str(e)}")
        print("="*60 + "\n")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        print(f"   ❌ Unexpected Error: {type(e).__name__} — {str(e)}")
        print("="*60 + "\n")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
