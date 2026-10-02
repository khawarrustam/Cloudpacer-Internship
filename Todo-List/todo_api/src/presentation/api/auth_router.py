from fastapi import APIRouter, Depends, status
from src.presentation.api.auth_schemas import SignupRequest, AuthResponse
from src.application.use_cases.signup_user import SignupUserUseCase, SignupCommand
from src.infrastructure.repositories.firebase_auth_repo import FirebaseAuthRepository

router = APIRouter(prefix="/auth", tags=["Auth"])

def get_signup_use_case() -> SignupUserUseCase:
    auth_repo = FirebaseAuthRepository()
    return SignupUserUseCase(auth_repo)

@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup(req: SignupRequest, use_case: SignupUserUseCase = Depends(get_signup_use_case)):
    cmd = SignupCommand(
        email=req.email,
        password=req.password,
        display_name=req.display_name
    )
    user_data = use_case.execute(cmd)
    
    return AuthResponse(
        uid=user_data.uid,
        email=user_data.email,
        message="User created successfully",
        token=user_data.token
    )
