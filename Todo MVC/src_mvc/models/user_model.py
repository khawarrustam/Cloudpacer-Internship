from firebase_admin import auth
from fastapi import HTTPException, status

def create_user_in_firebase(email: str, password: str, display_name: str) -> dict:
    try:
        user_record = auth.create_user(
            email=email,
            password=password,
            display_name=display_name
        )
        # Note: In a real flow, client logs in via Firebase SDK to get ID token. 
        # Here we return a custom token for demonstration purposes.
        custom_token = auth.create_custom_token(user_record.uid)
        
        return {
            "uid": user_record.uid,
            "email": user_record.email,
            "token": custom_token.decode("utf-8") if isinstance(custom_token, bytes) else custom_token
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
