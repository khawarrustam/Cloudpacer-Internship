from firebase_admin import auth
from src.domain.auth_repositories import IAuthRepository, UserData
from src.domain.exceptions import ValidationException


class FirebaseAuthRepository(IAuthRepository):
    def create_user(self, email: str, password: str, display_name: str) -> UserData:
        print(f"   📂 File    : src/infrastructure/repositories/firebase_auth_repo.py")
        print(f"   🔧 Function: FirebaseAuthRepository.create_user()")
        print(f"   🏛️  Layer   : INFRASTRUCTURE LAYER (Firebase Adapter)")
        print(f"   🌐 Implements: IAuthRepository (from domain/auth_repositories.py)")
        print(f"   📣 ACTION  : Calling Firebase Auth SDK → auth.create_user()")
        print(f"              email={email}, display_name={display_name}")

        try:
            user_record = auth.create_user(
                email=email,
                password=password,
                display_name=display_name
            )

            print(f"   ✅ Firebase Auth created user successfully!")
            print(f"              UID   : {user_record.uid}")
            print(f"              Email : {user_record.email}")
            print(f"   📣 ACTION  : Calling Firebase → auth.create_custom_token(uid)")

            custom_token = auth.create_custom_token(user_record.uid)
            token_str = custom_token.decode("utf-8") if isinstance(custom_token, bytes) else custom_token

            print(f"   ✅ JWT Custom Token generated!")
            print(f"   ➡️  Building UserData(uid, email, token)")
            print(f"      📂 Dataclass: src/domain/auth_repositories.py → UserData")
            print(f"   ↩️  Returning UserData to Application Layer (signup_user.py)")

            return UserData(uid=user_record.uid, email=user_record.email, token=token_str)

        except Exception as e:
            print(f"   ❌ Firebase Error in FirebaseAuthRepository!")
            print(f"      Exception Type: {type(e).__name__}")
            print(f"      Detail        : {str(e)}")
            print(f"   ➡️  Raising: ValidationException → Domain Layer Exception")
            raise ValidationException(f"Error creating user: {str(e)}")
