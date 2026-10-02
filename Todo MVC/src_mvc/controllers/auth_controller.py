from fastapi import APIRouter, status

from src_mvc.views.auth_views import SignupRequest, AuthResponse
from src_mvc.models.user_model import create_user_in_firebase

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup(req: SignupRequest):
    """
    Sign up a new user in Firebase.
    Returns the generated UID and a custom JWT token.
    """
    user_data = create_user_in_firebase(
        email=req.email,
        password=req.password,
        display_name=req.display_name
    )
    
    return AuthResponse(
        uid=user_data["uid"],
        email=user_data["email"],
        message="User created successfully",
        token=user_data["token"]
    )
