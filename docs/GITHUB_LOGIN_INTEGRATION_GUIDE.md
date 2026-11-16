# TodoFlow GitHub Login Integration Guide

## 1. Purpose

TodoFlow supports **Continue with GitHub**. GitHub proves the user's identity,
while the active TodoFlow database stores the local account and todos.

```text
GitHub identity -> local user in the active database -> TodoFlow JWT
```

The same GitHub account receives a different local UID in Firestore, MongoDB,
and PostgreSQL. Within one database, a verified matching email links password,
Google, and GitHub login methods to the same local user.

## 2. Create the GitHub OAuth App

Open **GitHub Settings > Developer settings > OAuth Apps > New OAuth App** and
use these values:

```text
Application name: TodoFlow Local
Homepage URL: http://127.0.0.1:5173
Application description: A task management application with database-specific accounts.
Authorization callback URL: http://127.0.0.1:5173/auth/github/callback
```

Keep wildcard matching, Device Flow, and expiring access tokens disabled for
this local web flow. After registration, copy the Client ID and generate a
Client Secret. GitHub displays the complete secret only when it is created.

Do not mix `localhost` with `127.0.0.1`; OAuth redirect URLs must match exactly.

## 3. Environment configuration

Backend: `backend/DDD/.env`

```env
GITHUB_CLIENT_ID=your-client-id
GITHUB_CLIENT_SECRET=your-client-secret
GITHUB_REDIRECT_URI=http://127.0.0.1:5173/auth/github/callback
```

Frontend: `frontend/.env`

```env
VITE_GITHUB_CLIENT_ID=your-client-id
VITE_GITHUB_REDIRECT_URI=http://127.0.0.1:5173/auth/github/callback
```

The Client ID is public and is used on both sides. The Client Secret belongs
only in the ignored backend `.env`; never place it in frontend code or Git.

## 4. Complete login flow

```text
1. The user selects Continue with GitHub.
2. The frontend creates a cryptographically random state value.
3. The browser opens GitHub's authorization page.
4. GitHub redirects back with a short-lived code and the state value.
5. The frontend validates state and sends the code to POST /auth/github.
6. The backend exchanges the code using its Client Secret.
7. The backend reads the GitHub profile and verified primary email.
8. The active repository finds, links, or creates the local user.
9. The backend returns its own database-bound TodoFlow JWT.
10. The temporary GitHub access token is discarded and never stored.
```

The temporary OAuth `state` is stored in `sessionStorage` to protect the
callback from login CSRF. The TodoFlow access token remains in application
memory and is not persisted in browser storage.

## 5. DDD file responsibilities

| File | Responsibility |
|---|---|
| `frontend/src/features/auth/githubOAuth.js` | Creates state, builds the redirect, and validates the callback |
| `frontend/src/components/GitHubSignInButton.jsx` | Starts GitHub authorization |
| `frontend/src/components/GitHubCallback.jsx` | Removes the code from the URL and calls the backend login thunk |
| `presentation/routers/auth.py` | Exposes `POST /auth/github` |
| `presentation/controllers/auth_controller.py` | Maps HTTP input to the application DTO and safe errors to 401 |
| `application/auth_service.py` | Coordinates the GitHub login use case |
| `domain/auth.py` | Defines identity, linking policy, and repository contract |
| `infrastructure/github_oauth.py` | Exchanges the code and obtains a verified profile |
| Database auth repositories | Find, link, or create the user in the selected database |

`github_sub` stores GitHub's stable numeric user ID as a string. A username can
change, so it is not used as the permanent account identity.

## 6. Run and test

Restart both applications after changing `.env` files:

```powershell
# Terminal 1
cd backend\DDD
.\.venv\Scripts\Activate.ps1
python -m uvicorn main:app --reload

# Terminal 2
cd frontend
npm run dev
```

Open `http://127.0.0.1:5173`, select **Continue with GitHub**, authorize the
app, and confirm that the selected database user contains `github_sub`.

## 7. Common errors

- **GitHub login setup pending:** Replace all OAuth placeholders and restart.
- **Invalid state:** Start a fresh login from the button; do not reuse an old
  callback URL.
- **Redirect URI mismatch:** Make the GitHub setting and both `.env` values
  identical, including host, port, path, and protocol.
- **Email could not be verified:** Add and verify an email in the GitHub account.
- **Code invalid or expired:** OAuth codes are short-lived and single-use; start
  the login again.

## 8. Security summary

- The Client Secret is backend-only.
- The callback `state` is checked before login.
- Only verified GitHub emails are accepted.
- A conflicting `github_sub` is rejected by the domain policy.
- The GitHub access token is not logged or persisted.
- The issued TodoFlow JWT is restricted to the active database.
