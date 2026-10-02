from firebase_admin import auth
from src.domain.auth_repositories import IAuthRepository, UserData
from src.domain.exceptions import ValidationException

class FirebaseAuthRepository(IAuthRepository):
    def create_user(self, email: str, password: str, display_name: str) -> UserData:
        try:
            user_record = auth.create_user(
                email=email,
                password=password,
                display_name=display_name
            )
            custom_token = auth.create_custom_token(user_record.uid)
            token_str = custom_token.decode("utf-8") if isinstance(custom_token, bytes) else custom_token
            return UserData(uid=user_record.uid, email=user_record.email, token=token_str)
        except Exception as e:
            raise ValidationException(f"Error creating user: {str(e)}")
