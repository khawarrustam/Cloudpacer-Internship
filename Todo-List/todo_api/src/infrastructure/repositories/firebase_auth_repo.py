"""Firebase adapter for signup and email/password login."""

import os

import requests
from firebase_admin import auth

from src.domain.auth_repositories import IAuthRepository, LoginData, UserData
from src.domain.exceptions import ValidationException
from src.shared.console import print_error, print_flow, print_step

# English: Firebase Admin creates users, but the REST API checks passwords.
# Roman Urdu: Firebase Admin user banata hai, REST API password check karti hai.
FIREBASE_WEB_API_KEY = os.getenv(
    "FIREBASE_WEB_API_KEY",
    "AIzaSyARxYXqa3D0PpgEBuEXRZ8Wf6a_piEb-Ak",
)
SIGNIN_URL = (
    "https://identitytoolkit.googleapis.com/v1/"
    f"accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
)


class FirebaseAuthRepository(IAuthRepository):
    def create_user(
        self,
        email: str,
        password: str,
        display_name: str,
    ) -> UserData:
        print_flow(
            source="src/application/use_cases/signup_user.py",
            destination="Firebase Admin -> create_user",
            data=f"email={email}, display_name={display_name}, password=hidden",
            english="Sending safe signup fields to Firebase Admin.",
            roman_urdu="Safe signup fields Firebase Admin ko ja rahe hain.",
        )

        try:
            user_record = auth.create_user(
                email=email,
                password=password,
                display_name=display_name,
            )
            print_flow(
                source="Firebase Admin -> created user",
                destination="firebase_auth_repo.py",
                data=f"uid={user_record.uid}, email={user_record.email}",
                english="Firebase returned the new user's safe details.",
                roman_urdu="Firebase ne new user ki safe details wapas dein.",
            )
            login_data = self.sign_in(email, password)
            user_data = UserData(
                uid=user_record.uid,
                email=user_record.email,
                token=login_data.id_token,
            )
            print_flow(
                source="firebase_auth_repo.py",
                destination="src/application/use_cases/signup_user.py",
                data=f"uid={user_data.uid}, token=hidden",
                english="Returning safe user data to the signup use case.",
                roman_urdu="Safe user data signup use case ko wapas ja raha hai.",
            )
            return user_data
        except ValidationException:
            raise
        except Exception as error:
            print_error(
                "Infrastructure",
                f"Firebase could not create the user: {error}",
                f"Firebase user nahi bana saka: {error}",
            )
            raise ValidationException(
                f"Error creating user: {error}"
            ) from error

    def sign_in(self, email: str, password: str) -> LoginData:
        print_flow(
            source="Application auth use case",
            destination="Firebase Auth REST API",
            data=f"email={email}, password=hidden",
            english="Sending login details to Firebase for checking.",
            roman_urdu="Login details check honay ke liye Firebase ko ja rahe hain.",
        )

        try:
            response = requests.post(
                SIGNIN_URL,
                json={
                    "email": email,
                    "password": password,
                    "returnSecureToken": True,
                },
                timeout=10,
            )

            if response.status_code != 200:
                message = response.json().get("error", {}).get(
                    "message",
                    "Sign-in failed",
                )
                print_error(
                    "Infrastructure",
                    f"Firebase rejected the login: {message}",
                    f"Firebase ne login reject kiya: {message}",
                )
                raise ValidationException(f"Invalid credentials: {message}")

            data = response.json()
            print_step(
                "Infrastructure",
                "Firebase login succeeded.",
                "Firebase login kamyab ho gaya.",
            )
            login_data = LoginData(
                uid=data["localId"],
                email=data["email"],
                id_token=data["idToken"],
            )
            print_flow(
                source="Firebase Auth REST API",
                destination="Application auth use case",
                data=f"uid={login_data.uid}, token=hidden",
                english="Returning safe login data to the use case.",
                roman_urdu="Safe login data use case ko wapas ja raha hai.",
            )
            return login_data
        except ValidationException:
            raise
        except Exception as error:
            print_error(
                "Infrastructure",
                f"Firebase login failed: {error}",
                f"Firebase login fail ho gaya: {error}",
            )
            raise ValidationException(f"Sign-in failed: {error}") from error
