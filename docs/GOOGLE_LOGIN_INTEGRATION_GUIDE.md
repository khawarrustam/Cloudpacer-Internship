# TodoFlow Google Login Integration Guide

## 1. Short explanation

The frontend obtains a signed Google ID token. The backend verifies that token,
finds or creates a local user in the active database, and returns a TodoFlow JWT.

```text
Google ID token -> backend verification -> active-database user -> TodoFlow JWT
```

Google proves identity only. Firebase Authentication is not used. Firestore,
MongoDB, or PostgreSQL stores the actual TodoFlow account.

## 2. Important terms

| Term | Meaning |
|---|---|
| Google ID token | Short-lived signed proof returned by Google Identity Services |
| `sub` / `google_sub` | Google's stable identifier for one Google account |
| TodoFlow JWT | The backend's access token for protected TodoFlow endpoints |
| Client ID | Public identifier shared by frontend and backend |
| Client Secret | Not required by the Google Identity Services ID-token flow used here |

The Google token is accepted only by `/auth/google`. The TodoFlow JWT is used
afterward in `Authorization: Bearer <token>` for todo requests.

## 3. Complete flow

```text
1. Google Identity Services renders the frontend button.
2. The user chooses a Google account.
3. Google returns a signed ID-token credential.
4. The frontend sends { credential } to POST /auth/google.
5. GoogleLoginRequest validates the HTTP shape.
6. The controller creates GoogleLoginInput.
7. AuthService calls AuthRepository.login_with_google.
8. AuthSecurity verifies signature, audience, issuer, expiry, and email.
9. The repository finds by google_sub, then falls back to verified email.
10. The domain policy validates whether an existing account may be linked.
11. The selected database creates or updates its local user.
12. The backend returns a database-bound TodoFlow JWT.
```

## 4. Database isolation

Each database owns independent users and todos:

```text
Same Google account + Firestore  -> Firestore local UID
Same Google account + MongoDB    -> MongoDB local UID
Same Google account + PostgreSQL -> PostgreSQL local UID
```

Changing `DATABASE` changes both authentication and todo storage. A JWT issued
for one database is rejected by another because its payload contains the active
database name.

Within one database, a matching password account may be linked only when Google
is authoritative for that address: Gmail or a Google Workspace hosted domain.
A conflicting `google_sub` is always rejected.

## 5. Frontend responsibilities

| File | Responsibility |
|---|---|
| `components/GoogleSignInButton.jsx` | Loads Google Identity Services and returns the credential |
| `components/AuthForm.jsx` | Displays the button and reports errors |
| `features/auth/authSlice.js` | Runs the async login and stores the session in memory |
| `api/authApi.js` | Sends `POST /auth/google` |
| `features/auth/authSession.js` | Keeps the TodoFlow JWT in memory only |

The frontend does not decode and trust the Google token. Verification belongs
to the backend.

## 6. Backend responsibilities

| Layer/file | Responsibility |
|---|---|
| `presentation/schemas.py` | Validates `GoogleLoginRequest` |
| `presentation/routers/auth.py` | Declares `POST /auth/google` |
| `presentation/controllers/auth_controller.py` | Maps HTTP data and safe errors |
| `application/dto.py` | Defines `GoogleLoginInput` |
| `application/auth_service.py` | Coordinates the login use case |
| `domain/auth.py` | Defines `GoogleIdentity` and `GoogleAccountPolicy` |
| `infrastructure/security.py` | Performs official token verification |
| Database auth repository | Finds, links, or creates the active-database user |

## 7. Stored user data

A provider-created local account contains values equivalent to:

```text
uid
email
display_name
google_sub
```

An account originally created with a password may also contain
`password_hash`. The raw Google token is never stored.

## 8. Google Cloud and environment setup

1. Open Google Cloud Console and configure the OAuth consent screen.
2. Create an OAuth Client ID of type **Web application**.
3. Add both development origins if both are used:

```text
http://localhost:5173
http://127.0.0.1:5173
```

4. Put the same public Client ID in both ignored `.env` files:

```env
# backend/DDD/.env
GOOGLE_CLIENT_ID=your-web-client-id.apps.googleusercontent.com

# frontend/.env
VITE_GOOGLE_CLIENT_ID=your-web-client-id.apps.googleusercontent.com
```

Restart the frontend and backend after changing environment values.

## 9. Switch databases

Stop the backend, select one database, and restart:

```powershell
$env:DATABASE = "firestore"   # or mongodb / postgresql
python -m uvicorn main:app --reload
```

Sign in with Google once in each database to demonstrate separate local users.

## 10. Request, response, and logs

```http
POST /auth/google
Content-Type: application/json

{ "credential": "signed-google-id-token" }
```

```json
{
  "uid": "local-database-uid",
  "email": "user@example.com",
  "token": "todoflow.jwt.value",
  "message": "Google login successful"
}
```

Logs show the Presentation, Application, and selected Infrastructure steps but
never print either token.

## 11. Common errors

- **Invalid audience:** The frontend and backend Client IDs differ.
- **Origin is not allowed:** Add the exact frontend origin in Google Cloud.
- **Expired/invalid credential:** Select the Google button again.
- **Use your password for this non-Google-managed email:** The domain policy
  refuses silent linking because Google is not authoritative for that domain.
- **Token rejected after database switch:** Sign in again to receive a JWT bound
  to the newly selected database.

## 12. Presentation answer

> Google Identity Services returns a signed ID token to the React frontend. The
> FastAPI backend verifies its signature, audience, issuer, expiry, and email.
> The selected repository then identifies the account using Google's stable
> `sub`, applies the domain linking policy, and creates or links a local user in
> Firestore, MongoDB, or PostgreSQL. Finally, the backend issues its own JWT
> restricted to that database. Google tokens are never stored or used as
> TodoFlow session tokens.
