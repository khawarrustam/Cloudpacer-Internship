# TodoFlow DDD API

The primary TodoFlow backend is a FastAPI service organized with
Domain-Driven Design (DDD) and Clean Architecture. Business rules remain
independent of FastAPI, Firebase, and storage implementation details.

## Capabilities

- Firebase email/password signup and login
- Authenticated todo creation, listing, completion, and deletion
- In-memory storage for local development
- Firestore storage for persistent environments
- Dependency injection through a single composition root
- Focused unit tests for use cases and API handlers
- Concise production-style logs with optional architecture tracing

## Architecture

```text
HTTP request
    |
    v
Presentation      FastAPI routers and request/response schemas
    |
    v
Application       Use cases, commands, DTOs, and mapping
    |
    v
Domain            Entities, value objects, rules, and repository contracts
    ^
    |
Infrastructure    Firebase, Firestore, and in-memory repository adapters
```

Dependencies point toward the domain. `src/bootstrap.py` is the composition
root that selects adapters and connects them to application use cases.

## Project structure

```text
backend/DDD/
|-- main.py
|-- requirements.txt
|-- requirements-dev.txt
|-- scripts/
|   |-- check_prints.py
|   `-- clear_firebase.py
|-- src/
|   |-- application/
|   |   |-- use_cases/
|   |   |-- dtos.py
|   |   `-- mappers.py
|   |-- domain/
|   |   |-- entities.py
|   |   |-- value_objects.py
|   |   |-- exceptions.py
|   |   `-- repositories.py
|   |-- infrastructure/repositories/
|   |-- presentation/api/
|   |-- shared/console.py
|   `-- bootstrap.py
`-- tests/
```

## Requirements

- Python 3.10+
- A Firebase project with Email/Password authentication enabled
- `serviceAccountKey.json` stored in `backend/DDD`

The credential file is ignored by Git and must never be committed.

## Installation

From the repository root:

```powershell
cd backend\DDD
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

## Running locally

Use in-memory todo storage during development:

```powershell
$env:USE_FIREBASE = "false"
python -m uvicorn main:app --reload
```

Use Firestore for persistent todo storage:

```powershell
$env:USE_FIREBASE = "true"
python -m uvicorn main:app --reload
```

Firebase Authentication is used in both modes. `USE_FIREBASE` changes only the
todo repository.

Service URLs:

- API: <http://127.0.0.1:8000>
- Swagger UI: <http://127.0.0.1:8000/docs>
- ReDoc: <http://127.0.0.1:8000/redoc>

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `USE_FIREBASE` | `false` | Select in-memory or Firestore todo storage |
| `FIREBASE_CREDENTIALS_PATH` | `serviceAccountKey.json` | Optional credential-path override |
| `FIREBASE_WEB_API_KEY` | Project default | Optional Firebase Web API-key override |

Only `USE_FIREBASE` is normally required.

## API endpoints

| Method | Endpoint | Authentication | Description |
|---|---|---:|---|
| `GET` | `/` | No | Health check |
| `POST` | `/auth/signup` | No | Create a Firebase user and return a token |
| `POST` | `/auth/login` | No | Authenticate and return a token |
| `GET` | `/todos` | Yes | List the current user's todos |
| `POST` | `/todos` | Yes | Create a todo |
| `PATCH` | `/todos/{todo_id}/complete` | Yes | Complete a todo |
| `DELETE` | `/todos/{todo_id}` | Yes | Delete a todo |

Protected routes expect:

```text
Authorization: Bearer <firebase-id-token>
```

## Logging

Logging works automatically without additional PowerShell commands. Every
meaningful request is shown as a small group; browser `OPTIONS` checks,
duplicate Uvicorn access lines, mapper loops, and low-level layer noise are
hidden from the default output:

```text
10:42:11 | INFO  | REQUEST  | #001 GET /todos
10:42:11 | INFO  | #001 GET /todos | Auth | Token is valid.
         |       |      Token valid hai.
10:42:12 | INFO  | #001 GET /todos | Application | Found 3 todo(s).
         |       |      3 todo milay.
10:42:12 | INFO  | RESPONSE | #001 GET /todos | 200 OK | 184 ms
```

Common password, token, and authorization values are redacted before any
diagnostic data is written.

## Tests and checks

```powershell
python -m pytest -q
python scripts/check_prints.py
```

Tests use the in-memory repository and do not write todo data to Firestore.

## Maintenance utility

The following command permanently deletes Firebase users and todos. Run it
only against a disposable development project:

```powershell
python scripts/clear_firebase.py
```

## Troubleshooting

- **Frontend cannot connect:** confirm the API is running on port `8000`.
- **Login fails:** confirm Email/Password authentication is enabled.
- **Todos disappear after restart:** use `USE_FIREBASE=true` for persistence.
- **Port 8000 is busy:** use another Uvicorn port and update `VITE_API_URL`.

## Related documentation

- [Repository run guide](../../README.md)
- [Architecture comparison](../../docs/architecture.md)
- [Postman testing guide](../../docs/api-testing.md)
- [Frontend documentation](../../frontend/README.md)
