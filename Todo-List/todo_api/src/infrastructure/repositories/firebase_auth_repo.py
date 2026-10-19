import os
import requests
from firebase_admin import auth
from src.domain.auth_repositories import IAuthRepository, UserData, LoginData
from src.domain.exceptions import ValidationException

# ---------------------------------------------------------------------------
# Firebase Auth REST API endpoint (for email/password sign-in).
# The Admin SDK cannot verify passwords — only the client-side REST API can.
# Web API key comes from: Firebase Console → Project Settings → General
# ---------------------------------------------------------------------------
FIREBASE_WEB_API_KEY = os.getenv("FIREBASE_WEB_API_KEY", "AIzaSyARxYXqa3D0PpgEBuEXRZ8Wf6a_piEb-Ak")
SIGNIN_URL = (
    f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
    f"?key={FIREBASE_WEB_API_KEY}"
)


class FirebaseAuthRepository(IAuthRepository):

    # ------------------------------------------------------------------
    # SIGNUP
    # ------------------------------------------------------------------
    def create_user(self, email: str, password: str, display_name: str) -> UserData:
        print(f"   📂 File    : src/infrastructure/repositories/firebase_auth_repo.py")
        print(f"   🔧 Function: FirebaseAuthRepository.create_user()")
        print(f"   🏛️  Layer   : INFRASTRUCTURE LAYER (Firebase Adapter)")
        print(f"   🌐 Implements: IAuthRepository (from domain/auth_repositories.py)")
        print(f"   📣 ACTION  : Calling Firebase Auth SDK → auth.create_user()")
        print(f"              email={email}, display_name={display_name}")

        try:
            # 1. Create the user in Firebase Auth
            user_record = auth.create_user(
                email=email,
                password=password,
                display_name=display_name
            )
            print(f"   ✅ Firebase Auth created user! UID: {user_record.uid}")

            # 2. Sign in via REST API to get a real ID token (verifiable server-side)
            print(f"   📣 ACTION  : Signing in via REST API to get ID token")
            login_data = self.sign_in(email, password)

            print(f"   ✅ ID token obtained!")
            print(f"   ↩️  Returning UserData to Application Layer")
            return UserData(uid=user_record.uid, email=user_record.email, token=login_data.id_token)

        except ValidationException:
            raise
        except Exception as e:
            print(f"   ❌ Firebase Error: {type(e).__name__} — {str(e)}")
            raise ValidationException(f"Error creating user: {str(e)}")

    # ------------------------------------------------------------------
    # SIGN IN
    # ------------------------------------------------------------------
    def sign_in(self, email: str, password: str) -> LoginData:
        print(f"   📂 File    : src/infrastructure/repositories/firebase_auth_repo.py")
        print(f"   🔧 Function: FirebaseAuthRepository.sign_in()")
        print(f"   🏛️  Layer   : INFRASTRUCTURE LAYER (Firebase Adapter)")
        print(f"   📣 ACTION  : POST → identitytoolkit.googleapis.com signInWithPassword")
        print(f"              email={email}")

        try:
            response = requests.post(
                SIGNIN_URL,
                json={"email": email, "password": password, "returnSecureToken": True},
                timeout=10,
            )

            if response.status_code != 200:
                error_msg = response.json().get("error", {}).get("message", "Sign-in failed")
                print(f"   ❌ Firebase REST API error: {error_msg}")
                raise ValidationException(f"Invalid credentials: {error_msg}")

            data = response.json()
            print(f"   ✅ Sign-in successful! localId={data['localId']}")
            print(f"   ↩️  Returning LoginData to Application Layer")

            return LoginData(
                uid=data["localId"],
                email=data["email"],
                id_token=data["idToken"],
            )

        except ValidationException:
            raise
        except Exception as e:
            print(f"   ❌ Sign-in error: {type(e).__name__} — {str(e)}")
            raise ValidationException(f"Sign-in failed: {str(e)}")
