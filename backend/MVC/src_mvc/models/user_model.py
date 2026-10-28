from firebase_admin import auth
from fastapi import HTTPException, status


def create_user_in_firebase(email: str, password: str, display_name: str) -> dict:
    print(f"   📂 File    : src_mvc/models/user_model.py")
    print(f"   🔧 Function: create_user_in_firebase()")
    print(f"   📣 ACTION  : Calling Firebase Auth SDK → auth.create_user()")
    print(f"              email={email}, display_name={display_name}")

    try:
        user_record = auth.create_user(
            email=email,
            password=password,
            display_name=display_name
        )

        print(f"   ✅ Firebase created user successfully!")
        print(f"              UID          : {user_record.uid}")
        print(f"              Email        : {user_record.email}")
        print(f"   📣 ACTION  : Calling Firebase Auth SDK → auth.create_custom_token(uid)")

        # Note: In a real flow, client logs in via Firebase SDK to get ID token.
        # Here we return a custom token for demonstration purposes.
        custom_token = auth.create_custom_token(user_record.uid)

        print(f"   ✅ Custom JWT token generated!")

        token_str = custom_token.decode("utf-8") if isinstance(custom_token, bytes) else custom_token

        print(f"   ↩️  RETURNING: user dict with uid, email, token to Controller")

        return {
            "uid": user_record.uid,
            "email": user_record.email,
            "token": token_str
        }

    except Exception as e:
        print(f"   ❌ Firebase Error in user_model.py!")
        print(f"      Exception: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
