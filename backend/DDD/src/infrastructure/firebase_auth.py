"""Firebase signup and login infrastructure."""

import os

from firebase_admin import auth
import requests

from src.domain.models import AuthRepository, UserData, ValidationException
from src.logs import log_error, log_step


class FirebaseAuthRepository(AuthRepository):
    """Use Firebase for account creation and email/password login."""

    # Values startup par .env se read hoti hain. Inko aik jagah rakhne se
    # signup/login methods mein URLs aur timeout repeat nahi hote.
    def __init__(self) -> None:
        """Prepare the Firebase login URL and request timeout."""
        api_key = os.environ["FIREBASE_WEB_API_KEY"]
        auth_url = os.environ["FIREBASE_AUTH_URL"]

        self.login_url = f"{auth_url}?key={api_key}"
        self.request_timeout = int(os.environ["FIREBASE_REQUEST_TIMEOUT"])

    def signup(self, email: str, password: str, name: str) -> UserData:
        """Create a Firebase user and immediately log that user in.

        Kyun: Signup response mein bhi token chahiye taa-ke frontend user ko
        account banane ke foran baad authenticated screen dikha sake.
        """
        try:
            auth.create_user(email=email, password=password, display_name=name)
            return self.login(email, password)
        except ValidationException:
            raise
        except Exception as error:
            log_error("Infrastructure", f"Firebase signup failed: {error}")
            raise ValidationException(str(error)) from error

    def login(self, email: str, password: str) -> UserData:
        """Send credentials to Firebase and return UID, email, and ID token.

        Kyun: Firebase Admin SDK password login provide nahi karta, is liye
        official Identity Toolkit REST endpoint use hota hai.
        """
        try:
            response = requests.post(
                self.login_url,
                json={
                    "email": email,
                    "password": password,
                    "returnSecureToken": True,
                },
                timeout=self.request_timeout,
            )
            if response.status_code != 200:
                message = response.json().get("error", {}).get(
                    "message",
                    "Invalid email or password",
                )
                raise ValidationException(message)

            response_data = response.json()
            log_step(
                "Infrastructure",
                "Firebase authentication succeeded.",
                "Firebase authentication kamyab ho gayi.",
            )
            return UserData(
                uid=response_data["localId"],
                email=response_data["email"],
                token=response_data["idToken"],
            )
        except ValidationException:
            raise
        except Exception as error:
            log_error("Infrastructure", f"Firebase login failed: {error}")
            raise ValidationException(str(error)) from error
