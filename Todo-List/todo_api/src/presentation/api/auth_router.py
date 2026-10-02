from fastapi import APIRouter, HTTPException, status
from src.presentation.api.auth_schemas import SignupRequest, AuthResponse
from src.application.use_cases.signup_user import SignupUserUseCase, SignupCommand
from src.infrastructure.repositories.firebase_auth_repo import FirebaseAuthRepository
from src.domain.exceptions import ValidationException

router = APIRouter(prefix="/auth", tags=["Auth"])


def get_signup_use_case() -> SignupUserUseCase:
    print(f"   🔧 [DDD] Dependency Injection: get_signup_use_case()")
    print(f"           📂 File: src/presentation/api/auth_router.py")
    print(f"           ➡️  Creating FirebaseAuthRepository()")
    print(f"              📂 File: src/infrastructure/repositories/firebase_auth_repo.py")
    auth_repo = FirebaseAuthRepository()
    print(f"           ➡️  Creating SignupUserUseCase(auth_repo)")
    print(f"              📂 File: src/application/use_cases/signup_user.py")
    return SignupUserUseCase(auth_repo)


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup(req: SignupRequest, use_case: SignupUserUseCase = get_signup_use_case()):
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
    print("   ➡️  STEP 1: Presentation → Application Layer")
    print("              Building SignupCommand (DTO)")
    print(f"              📂 File: src/application/use_cases/signup_user.py")

    cmd = SignupCommand(
        email=req.email,
        password=req.password,
        display_name=req.display_name
    )

    print(f"   ➡️  STEP 2: Calling SignupUserUseCase.execute(cmd)")

    try:
        user_data = use_case.execute(cmd)

        print("-"*60)
        print(f"   ✅ STEP 3: Use Case returned UserData to Router")
        print(f"              UID   : {user_data.uid}")
        print(f"              Email : {user_data.email}")
        print(f"              Token : {user_data.token[:30]}...")
        print("-"*60)
        print("   ➡️  STEP 4: Building AuthResponse (Presentation Schema)")
        print(f"              📂 File: src/presentation/api/auth_schemas.py → AuthResponse")

        response = AuthResponse(
            uid=user_data.uid,
            email=user_data.email,
            message="User created successfully",
            token=user_data.token
        )

        print("   📤 STEP 5: Sending Response to Client | Status: 201 Created")
        print("="*60 + "\n")

        return response

    except ValidationException as e:
        print(f"   ❌ ValidationException caught in Router!")
        print(f"      📂 Raised by: src/domain/exceptions.py → ValidationException")
        print(f"      Detail: {str(e)}")
        print("="*60 + "\n")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        print(f"   ❌ Unexpected Error caught in Router!")
        print(f"      Type  : {type(e).__name__}")
        print(f"      Detail: {str(e)}")
        print("="*60 + "\n")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
