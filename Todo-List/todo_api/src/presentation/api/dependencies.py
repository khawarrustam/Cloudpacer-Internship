"""Authentication dependencies used by protected API routes."""

from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth

from src.shared.console import print_error, print_flow, print_step

bearer_scheme = HTTPBearer(auto_error=True)


@dataclass(frozen=True)
class CurrentUser:
    uid: str
    email: str


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> CurrentUser:
    """Verify the Firebase token and return the signed-in user."""
    print_flow(
        source="HTTP Authorization header",
        destination="Firebase Admin -> verify_id_token",
        data="bearer_token=hidden",
        english="Sending the hidden token to Firebase for verification.",
        roman_urdu="Hidden token verification ke liye Firebase ko ja raha hai.",
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
        print_flow(
            source="Firebase verified token",
            destination="Protected FastAPI todo route",
            data=f"uid={user.uid}, email={user.email}",
            english="Verified user data is going to the requested route.",
            roman_urdu="Verified user data requested route ko ja raha hai.",
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
