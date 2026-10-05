"""
=============================================================================
PRESENTATION LAYER — FastAPI Auth Dependency (JWT Token Verification)
=============================================================================
Yeh file ek reusable FastAPI Dependency provide karti hai jo:
1. Request header se Bearer token extract karti hai.
2. Firebase Admin SDK se token verify karti hai.
3. Verified user info (uid, email) endpoint function ko inject karti hai.

Usage (in any route):
    from src.presentation.api.dependencies import get_current_user, CurrentUser

    @router.get("/protected")
    def my_route(user: CurrentUser = Depends(get_current_user)):
        return {"your_uid": user.uid}
=============================================================================
"""

from dataclasses import dataclass
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth

# FastAPI's built-in Bearer token extractor
# auto_error=True → returns 403 automatically if no Authorization header
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
    FastAPI dependency — verifies the Firebase ID token from the
    Authorization: Bearer <token> header.

    Raises:
        401 Unauthorized — if token is missing, invalid, or expired.
    """
    token = credentials.credentials
    print(f"   🔐 [Auth] Verifying Firebase ID token...")

    try:
        decoded = auth.verify_id_token(token)
        uid = decoded["uid"]
        email = decoded.get("email", "")
        print(f"   ✅ [Auth] Token valid! uid={uid}, email={email}")
        return CurrentUser(uid=uid, email=email)

    except auth.ExpiredIdTokenError:
        print(f"   ❌ [Auth] Token expired!")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please log in again.",
        )
    except auth.InvalidIdTokenError as e:
        print(f"   ❌ [Auth] Invalid token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
        )
    except Exception as e:
        print(f"   ❌ [Auth] Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed. Please log in again.",
        )
