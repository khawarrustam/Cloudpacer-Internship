# TodoFlow Google Login — Complete Beginner-Friendly Guide

This guide explains the complete Google-login integration without requiring you
to open every code file during a presentation.

## 1. What was integrated?

TodoFlow now supports two login choices:

1. Email and password.
2. Continue with Google.

Google only proves who the person is. TodoFlow still stores the user and todos
inside the database selected by the `DATABASE` environment variable:

```text
DATABASE=firestore   -> user + todos in Firestore
DATABASE=mongodb     -> user + todos in MongoDB
DATABASE=postgresql  -> user + todos in PostgreSQL
```

Firebase Authentication is not used.

## 2. The most important idea: two different tokens

Google login uses two tokens at different moments:

| Token | Created by | Purpose | Lifetime in our flow |
|---|---|---|---|
| Google ID token | Google | Proves the Google account identity | Sent once to `/auth/google` |
| TodoFlow JWT | TodoFlow backend | Authenticates later todo requests | Kept in frontend memory |

Simple explanation:

```text
Google token says: “Google verified this person.”
TodoFlow JWT says: “This local database user may access these todos.”
```

The frontend never treats the Google token as a TodoFlow session token.

## 3. Google Cloud setup

In Google Auth Platform:

1. Configure **Branding** with app name and support email.
2. Select **External** audience for personal Gmail/testing accounts.
3. Create a client with type **Web application**.
4. Add these Authorized JavaScript origins:

```text
http://localhost:5173
http://127.0.0.1:5173
```

5. Copy only the public Client ID.

This flow does not require:

- Firebase Authentication;
- a Google client secret in frontend or backend;
- an authorized redirect URI;
- storing the downloaded client-secret JSON in the repository.

## 4. Environment configuration

The same public Client ID must be present in both local `.env` files:

```env
# backend/DDD/.env
GOOGLE_CLIENT_ID=your-id.apps.googleusercontent.com

# frontend/.env
VITE_GOOGLE_CLIENT_ID=your-id.apps.googleusercontent.com
```

Why is it in both places?

- Frontend needs it to render the correct Google button.
- Backend needs it as the expected `aud` value while verifying Google's token.

If the token was created for another application's Client ID, the backend
rejects it.

## 5. Complete flow in one diagram

```text
User clicks “Continue with Google”
        |
        v
Google Identity Services opens account chooser
        |
        v
Google returns ID token in `credential`
        |
        v
Frontend dispatches googleLoginUser
        |
        v
POST /auth/google  { credential }
        |
        v
GoogleLoginRequest validates HTTP body
        |
        v
GoogleLoginInput carries data to AuthService
        |
        v
AuthService.login_with_google
        |
        v
Selected AuthRepository.login_with_google
        |
        v
AuthSecurity.verify_google_credential
  - Google signature
  - expected Client ID / audience
  - issuer
  - expiry
  - verified email
        |
        v
Repository finds, links, or creates user
only inside the selected database
        |
        v
AuthSecurity creates database-bound TodoFlow JWT
        |
        v
Frontend keeps JWT in JavaScript memory
        |
        v
JWT is sent as Bearer token with todo requests
```

## 6. Frontend files and their jobs

### `frontend/src/components/GoogleSignInButton.jsx`

Purpose:

- Loads Google's official `gsi/client` browser script once.
- Uses `VITE_GOOGLE_CLIENT_ID`.
- Renders the official Continue with Google button.
- Receives `response.credential` after account selection.
- Passes the credential to the normal Redux authentication flow.

It does not decode or trust the credential.

### `frontend/src/components/AuthForm.jsx`

Purpose:

- Shows Google login and email/password login on the same screen.
- Displays success/error feedback.
- Keeps temporary form values in local React state.

### `frontend/src/features/auth/authSlice.js`

The `googleLoginUser` async thunk:

```text
credential
 -> authApi.loginWithGoogle
 -> backend response
 -> saveSession(response)
 -> Redux user state
```

### `frontend/src/api/authApi.js`

Adds this API call:

```http
POST /auth/google
Content-Type: application/json

{
  "credential": "Google ID token"
}
```

### `frontend/src/features/auth/authSession.js`

Stores only the TodoFlow JWT in JavaScript memory. Nothing is saved in
`localStorage`, so refreshing the page requires login again.

## 7. Backend files and their jobs

### `presentation/schemas.py`

`GoogleLoginRequest` validates that the HTTP request contains a credential.

### `presentation/routers/auth.py`

`POST /auth/google`:

1. Receives the request.
2. Creates `GoogleLoginInput`.
3. Calls `AuthService.login_with_google`.
4. Returns `AuthResponse`.
5. Maps expected invalid-login errors to HTTP 401.

### `application/dto.py`

`GoogleLoginInput` carries the credential from presentation to application
without importing FastAPI or Pydantic into the application layer.

### `application/auth_service.py`

`login_with_google` coordinates the use case. It does not contain Google,
MongoDB, Firestore, or SQL code.

### `domain/auth.py`

`AuthRepository.login_with_google` defines the operation that all three
database adapters must implement.

### `infrastructure/security.py`

`verify_google_credential` uses the official `google-auth` library. It returns
a trusted `GoogleProfile` containing:

```text
subject       = stable Google `sub`
email         = normalized verified email
display_name  = Google name or email prefix
can_link_existing_email = safe automatic-link decision
```

Why use `sub`?

Google email can change, but Google `sub` is the stable account identifier.

### Database auth repositories

Each repository implements the same operation using its own storage language:

| Database | Google-user lookup/storage |
|---|---|
| Firestore | `runQuery` by `google_sub`, then document PATCH |
| MongoDB | `find_one` by `google_sub`, then insert/update |
| PostgreSQL | `SELECT` by `google_sub`, then INSERT/UPDATE |

## 8. What is stored in each database?

### Firestore `auth_users` document

```text
uid
email
display_name
google_sub
password_hash  (only when password was configured)
```

### MongoDB `users` document

```text
_id             = local TodoFlow UUID
email
display_name
google_sub
password_hash   = optional
```

MongoDB creates unique indexes for `email` and sparse `google_sub`.

### PostgreSQL `users` row

```text
id              = local TodoFlow UUID
email
display_name
password_hash   = nullable
google_sub      = nullable and unique when present
```

The repository safely extends an existing password-only users table without
deleting old users.

## 9. Same email and database isolation

Suppose one Google account is `student@gmail.com`.

First login in each database creates:

| Selected database | Local UID | Account relationship |
|---|---|---|
| Firestore | UUID-A | Firestore-only local user |
| MongoDB | UUID-B | MongoDB-only local user |
| PostgreSQL | UUID-C | PostgreSQL-only local user |

`UUID-A`, `UUID-B`, and `UUID-C` are different even though Google `sub` and
email are the same.

Why?

The selected repository only reads/writes its own database. No shared global
users table exists.

The TodoFlow JWT also contains:

```text
database = firestore | mongodb | postgresql
```

A MongoDB token is therefore rejected after switching to PostgreSQL.

## 10. Existing password-account behavior

Inside one selected database:

- Existing Google `sub` -> login to the same local UID.
- New Google `sub` and unused email -> create a new local UID.
- Same Gmail/Google Workspace email as a password account -> safely link Google
  to that same local UID.
- Same non-Gmail third-party email as a password account -> require password
  login instead of automatic linking.

The Gmail/Workspace restriction avoids unsafe automatic account linking where
Google may not be the current authority for a third-party email address.

## 11. Request and response

Request:

```http
POST /auth/google
Content-Type: application/json

{
  "credential": "eyJ...Google-ID-token..."
}
```

Successful response:

```json
{
  "uid": "local-database-uuid",
  "email": "student@gmail.com",
  "token": "TodoFlow.database-bound.JWT",
  "message": "Google login successful"
}
```

The Google ID token is not returned or stored as the application session.

## 12. Logs you will see

```text
Presentation   | Google login request received.
Infrastructure | PostgreSQL/MongoDB/Firestore Google authentication succeeded.
Application    | Google login completed.
```

Tokens and passwords are never printed in logs.

## 13. How to switch and test databases

Stop the backend and select one database:

```powershell
$env:DATABASE = "firestore"
python -m uvicorn main:app --reload

$env:DATABASE = "mongodb"
python -m uvicorn main:app --reload

$env:DATABASE = "postgresql"
python -m uvicorn main:app --reload
```

Login with the same Google account after each restart. Then inspect:

- Firestore Console -> `auth_users`;
- MongoDB Compass -> `users`;
- pgAdmin -> `users` table.

You should see a different local UID in every database.

## 14. Security checklist

- Google ID token is verified on the backend.
- Expected Client ID/audience is checked.
- Stable Google `sub` is stored.
- Verified email is required.
- Database-specific local UUID is used for todo ownership.
- TodoFlow JWT is bound to the selected database.
- Client secret is not stored in frontend or backend.
- Downloaded client-secret JSON is not committed.
- TodoFlow JWT remains in memory, not browser local storage.

## 15. Common problems

### Google button says setup pending

Set the Client ID in both `.env` files, then restart both servers.

### `The given origin is not allowed`

Add the exact frontend URL to Authorized JavaScript origins. `localhost` and
`127.0.0.1` are different origins, so add both.

### Invalid Google login

Confirm frontend and backend use exactly the same Web Client ID.

### Account exists in one database but not another

This is expected. Login with Google once while each database is selected.

### Old database token returns 401 after switching

This is expected security behavior. Log in again in the newly selected
database.

## 16. Verification completed during implementation

The implementation was checked for:

- Google claim mapping and invalid-token rejection;
- Google-only account password rejection;
- password account + Google linking in all three real databases;
- repeat Google login returning the same UID in one database;
- different local UIDs across Firestore, MongoDB and PostgreSQL;
- cross-database JWT rejection;
- `/auth/google` HTTP/OpenAPI contract;
- backend compilation and dependency health;
- frontend lint and production build.

Temporary verification users were removed after the checks.

## 17. Presentation-ready answer

> “The frontend uses Google Identity Services to receive a Google ID token. It
> sends that credential to `POST /auth/google`. The backend verifies it with the
> official `google-auth` library and uses Google's stable `sub` identifier. The
> currently selected repository then finds or creates a local user only in its
> own database. That is why the same Google account receives different local
> UIDs in Firestore, MongoDB and PostgreSQL. Finally, TodoFlow issues its own
> database-bound JWT for protected todo requests. Google proves identity, but
> TodoFlow and the selected database own the application account and tasks.”

## 18. Important code links

- [Google button](../frontend/src/components/GoogleSignInButton.jsx)
- [Frontend authentication thunk](../frontend/src/features/auth/authSlice.js)
- [Auth HTTP route](../backend/DDD/app/presentation/routers/auth.py)
- [Auth application service](../backend/DDD/app/application/auth_service.py)
- [Auth contract](../backend/DDD/app/domain/auth.py)
- [Google/JWT security](../backend/DDD/app/infrastructure/security.py)
- [Firestore auth adapter](../backend/DDD/app/infrastructure/firestore/auth_repository.py)
- [MongoDB auth adapter](../backend/DDD/app/infrastructure/mongodb/auth_repository.py)
- [PostgreSQL auth adapter](../backend/DDD/app/infrastructure/postgresql/auth_repository.py)
