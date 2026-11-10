# TodoFlow DDD Backend

A beginner-readable FastAPI backend with professional DDD boundaries. The same
selected database stores both accounts and todos.

The evidence, placement rules, and restructuring prompt are recorded in
[`ARCHITECTURE.md`](ARCHITECTURE.md).

For a complete file-by-file explanation, request flows, demo plan, limitations,
and viva preparation, read
[`BACKEND_PRESENTATION_GUIDE.md`](../../docs/BACKEND_PRESENTATION_GUIDE.md).

## Structure

```text
backend/DDD/
|-- main.py                    Beginner-compatible Uvicorn entrypoint
|-- app/
|   |-- main.py                Composition root and FastAPI app
|   |-- config.py              Typed environment settings
|   |-- logging.py             Bilingual request flow logs
|   |-- domain/                Business rules and repository contracts
|   |-- application/           Use-case services and DTOs
|   |-- infrastructure/        Database/security implementations
|   `-- presentation/          HTTP routes, dependencies, and schemas
|-- ARCHITECTURE.md            Research and layer placement contract
|-- requirements.txt
`-- .env.example
```

Detailed adapter modules remain small and explicit:

```text
app/infrastructure/
|-- security.py
|-- repository_factory.py
|-- firestore/
|   |-- auth_repository.py
|   `-- todo_repository.py
|-- mongodb/
|   |-- auth_repository.py
|   `-- todo_repository.py
`-- postgresql/
    |-- auth_repository.py
    `-- todo_repository.py
```

HTTP endpoints follow the same naming rule under
`app/presentation/routers/auth.py` and `app/presentation/routers/todos.py`.

## Dependency direction

```text
presentation -> application -> domain
infrastructure -------------> domain
app/main.py -> all outer layers for dependency wiring
```

- Domain contains no FastAPI, Pydantic, or database-driver imports.
- Application coordinates workflows without HTTP or database queries.
- Infrastructure implements repository contracts for external databases.
- Presentation handles HTTP validation, dependencies, and status codes.
- `app/main.py` is the only composition root that chooses concrete adapters.

## Install

```powershell
cd backend\DDD
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set the connection values for the databases
you use. Keep `AUTH_TOKEN_SECRET` private and change its example value.

## Select a database

Stop the backend before switching, then run one option:

```powershell
$env:DATABASE = "firestore"
python -m uvicorn main:app --reload

$env:DATABASE = "mongodb"
python -m uvicorn main:app --reload

$env:DATABASE = "postgresql"
python -m uvicorn main:app --reload
```

The command remains simple because root `main.py` delegates to the professional
`app.main` composition root.

## Database-specific accounts

Firestore, MongoDB, and PostgreSQL accounts are independent. The same email may
sign up in all three databases and receives a different UID in each database.
A token issued for one database is rejected after switching to another.

- Firestore accounts: `auth_users` collection
- MongoDB accounts: `users` collection
- PostgreSQL accounts: `users` table

Passwords are stored as salted hashes, never plain text.

## Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | Health check and active database |
| `POST` | `/auth/signup` | Create account in active database |
| `POST` | `/auth/login` | Login from active database |
| `GET` | `/todos` | List current user's todos |
| `POST` | `/todos` | Create todo |
| `PATCH` | `/todos/{id}/complete` | Complete todo |
| `DELETE` | `/todos/{id}` | Delete todo |

## URLs

- API: <http://127.0.0.1:8000>
- Swagger: <http://127.0.0.1:8000/docs>
- ReDoc: <http://127.0.0.1:8000/redoc>

## Run focused tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Logs and comments

Request logs still show Presentation, Auth, Application, and Infrastructure in
English plus Roman Urdu. Public boundary functions use concise What/When/How
docstrings so the reason and layer responsibility stay aligned with the code.
