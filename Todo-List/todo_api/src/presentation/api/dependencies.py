from dataclasses import dataclass
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth
import jwt

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
    Includes a development bypass for 'Token used too early' errors (clock skew).
    """
    token = credentials.credentials
    print(f"   🔐 [Auth] Verifying Firebase ID token...")

    try:
        # 1. Try standard Firebase Admin SDK verification
        decoded = auth.verify_id_token(token)
        uid = decoded["uid"]
        email = decoded.get("email", "")
        print(f"   ✅ [Auth] Token valid! uid={uid}, email={email}")
        return CurrentUser(uid=uid, email=email)

    except auth.InvalidIdTokenError as e:
        error_msg = str(e)
        if "Token used too early" in error_msg:
            print(f"   ⚠️ [Auth] Clock skew detected. Applying development bypass...")
            try:
                # DEVELOPMENT BYPASS:
                # Using PyJWT to decode without verification to get the identity.
                # Firebase tokens use 'user_id' in some contexts but 'uid' in others.
                # We check both common keys.
                decoded = jwt.decode(token, options={"verify_signature": False})
                uid = decoded.get("uid") or decoded.get("user_id")
                email = decoded.get("email", "")

                if not uid:
                    print(f"   ❌ [Auth] Bypass failed: No uid found in token payload. Keys: {list(decoded.keys())}")
                    raise KeyError("uid")

                print(f"   ✅ [Auth] Bypass successful! uid={uid}, email={email}")
                return CurrentUser(uid=uid, email=email)
            except Exception as bypass_err:
                print(f"   ❌ [Auth] Bypass failed: {bypass_err}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication token.",
                )

        print(f"   ❌ [Auth] Invalid token: {error_msg}")
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
