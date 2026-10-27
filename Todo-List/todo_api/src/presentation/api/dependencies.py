"""Authentication dependencies used by protected API routes."""

from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth

from src.shared.console import print_error, print_step

bearer_scheme = HTTPBearer(auto_error=True)


@dataclass(frozen=True)
class CurrentUser:
    uid: str
    email: str


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> CurrentUser:
    """Verify the Firebase token and return the signed-in user."""
    print_step(
        "Auth",
        "Checking the Firebase login token.",
        "Firebase login token check ho raha hai.",
    )

    try:
        decoded_token = auth.verify_id_token(
            credentials.credentials,
            clock_skew_seconds=60,
        )
        user = CurrentUser(
            uid=decoded_token["uid"],
            email=decoded_token.get("email", ""),
        )
        print_step(
            "Auth",
            f"Token is valid for {user.email}.",
            f"{user.email} ka token valid hai.",
        )
        return user
    except auth.ExpiredIdTokenError as error:
        print_error(
            "Auth",
            "The login token has expired.",
            "Login token expire ho gaya hai.",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please log in again.",
        ) from error
    except auth.InvalidIdTokenError as error:
        print_error(
            "Auth",
            "The login token is invalid.",
            "Login token valid nahi hai.",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
        ) from error
    except Exception as error:
        print_error(
            "Auth",
            f"Token check failed: {error}",
            f"Token check fail ho gaya: {error}",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed. Please log in again.",
        ) from error
