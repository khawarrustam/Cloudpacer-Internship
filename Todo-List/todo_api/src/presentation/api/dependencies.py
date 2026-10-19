from dataclasses import dataclass
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth

# FastAPI's built-in Bearer token extractor
bearer_scheme = HTTPBearer(auto_error=True)


@dataclass(frozen=True)
class CurrentUser:
    """Verified user info injected into protected routes."""
    uid: str
    email: str


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> CurrentUser:
    """
    FastAPI dependency — verifies the Firebase ID token.
    Allows a small, bounded clock-skew tolerance while preserving signature verification.
    """
    token = credentials.credentials
    print(f"   🔐 [Auth] Verifying Firebase ID token...")

    try:
        decoded = auth.verify_id_token(token, clock_skew_seconds=60)
        uid = decoded["uid"]
        email = decoded.get("email", "")
        print(f"   ✅ [Auth] Token valid! uid={uid}, email={email}")
        return CurrentUser(uid=uid, email=email)

    except auth.InvalidIdTokenError as e:
        print(f"   ❌ [Auth] Invalid token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
        )

    except auth.ExpiredIdTokenError:
        print(f"   ❌ [Auth] Token expired!")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please log in again.",
        )
    except Exception as e:
        print(f"   ❌ [Auth] Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed. Please log in again.",
        )
