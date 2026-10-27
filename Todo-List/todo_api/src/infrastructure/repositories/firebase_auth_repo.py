"""Firebase adapter for signup and email/password login."""

import os

import requests
from firebase_admin import auth

from src.domain.auth_repositories import IAuthRepository, LoginData, UserData
from src.domain.exceptions import ValidationException
from src.shared.console import print_error, print_step

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
        print_step(
            "Infrastructure",
            f"Creating Firebase user {email}.",
            f"Firebase par {email} ka user ban raha hai.",
        )

        try:
            user_record = auth.create_user(
                email=email,
                password=password,
                display_name=display_name,
            )
            login_data = self.sign_in(email, password)
            return UserData(
                uid=user_record.uid,
                email=user_record.email,
                token=login_data.id_token,
            )
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
        print_step(
            "Infrastructure",
            f"Checking Firebase login for {email}.",
            f"{email} ka Firebase login check ho raha hai.",
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
            return LoginData(
                uid=data["localId"],
                email=data["email"],
                id_token=data["idToken"],
            )
        except ValidationException:
            raise
        except Exception as error:
            print_error(
                "Infrastructure",
                f"Firebase login failed: {error}",
                f"Firebase login fail ho gaya: {error}",
            )
            raise ValidationException(f"Sign-in failed: {error}") from error
