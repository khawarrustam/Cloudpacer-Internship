from fastapi import APIRouter, HTTPException, status

from src_mvc.views.auth_views import SignupRequest, AuthResponse
from src_mvc.models.user_model import create_user_in_firebase

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup(req: SignupRequest):
    """
    Sign up a new user in Firebase.
    Returns the generated UID and a custom JWT token.
    """
    print("\n" + "="*60)
    print("📥 [MVC] REQUEST RECEIVED")
    print("="*60)
    print(f"   📂 File    : src_mvc/controllers/auth_controller.py")
    print(f"   🔧 Function: signup()")
    print(f"   🌐 Route   : POST /auth/signup")
    print(f"   📧 Email   : {req.email}")
    print(f"   👤 Name    : {req.display_name}")
    print(f"   🔑 Password: {'*' * len(req.password)} ({len(req.password)} chars)")
    print("-"*60)
    print("   ➡️  STEP 1: Controller → calling Model (user_model.py)")
    print("              Function: create_user_in_firebase()")
    print("-"*60)

    try:
        user_data = create_user_in_firebase(
            email=req.email,
            password=req.password,
            display_name=req.display_name
        )

        print("-"*60)
        print("   ✅ STEP 2: Model returned user data to Controller")
        print(f"              UID   : {user_data['uid']}")
        print(f"              Email : {user_data['email']}")
        print(f"              Token : {user_data['token'][:30]}...")
        print("-"*60)
        print("   ➡️  STEP 3: Controller → building AuthResponse (View)")
        print("              File: src_mvc/views/auth_views.py → AuthResponse")

        response = AuthResponse(
            uid=user_data["uid"],
            email=user_data["email"],
            message="User created successfully",
            token=user_data["token"]
        )

        print("-"*60)
        print("   📤 STEP 4: Sending Response back to Client")
        print(f"              Status : 201 Created")
        print(f"              UID    : {response.uid}")
        print(f"              Message: {response.message}")
        print("="*60 + "\n")

        return response

    except HTTPException as e:
        print("-"*60)
        print(f"   ❌ ERROR caught in Controller!")
        print(f"      Status Code: {e.status_code}")
        print(f"      Detail     : {e.detail}")
        print("="*60 + "\n")
        raise
