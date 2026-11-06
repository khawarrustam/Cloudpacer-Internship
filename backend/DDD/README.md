# TodoFlow DDD Backend

A small FastAPI backend that keeps the important DDD layers without creating
dozens of files.

## Structure

```text
backend/DDD/
|-- main.py              Starts Firebase Auth, selects a database, creates the API
|-- requirements.txt     Python packages
`-- src/
    |-- presentation/
    |   |-- dto.py         HTTP request and response schemas
    |   `-- routes.py      FastAPI routes and token verification
    |-- application/
    |   |-- dto.py         Use-case input and output objects
    |   `-- use_cases.py   Todo and authentication workflows
    |-- domain/
    |   `-- models.py      Entities, value objects, rules, contracts
    |-- infrastructure/
    |   |-- firebase_auth.py  Firebase signup and login
    |   |-- firestore.py      Firestore todo adapter
    |   |-- mongodb.py        MongoDB todo adapter
    |   `-- postgresql.py     PostgreSQL todo adapter
    `-- logs.py             Readable terminal request flow
```

The request direction is:

```text
Frontend -> Presentation -> Application -> Domain -> Infrastructure -> Database
```

## Install

```powershell
cd backend\DDD
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Place `serviceAccountKey.json` inside `backend/DDD`. It is ignored by Git and
must never be committed.

## Choose a database from PowerShell

Copy `.env.example` to `.env`, fill in the connection settings you use, then
choose a database before starting the API:

```powershell
$env:DATABASE = "firestore"
python -m uvicorn main:app --reload

$env:DATABASE = "mongodb"
python -m uvicorn main:app --reload

$env:DATABASE = "postgresql"
python -m uvicorn main:app --reload
```

Stop the running backend before changing `DATABASE`. Firestore uses its HTTPS
API, MongoDB uses `MONGODB_URI`, and PostgreSQL uses `POSTGRESQL_URL`. There is
no local or in-memory todo storage mode.

## URLs

- API: <http://127.0.0.1:8000>
- Swagger: <http://127.0.0.1:8000/docs>
- ReDoc: <http://127.0.0.1:8000/redoc>

## Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | Health check |
| `POST` | `/auth/signup` | Create Firebase account |
| `POST` | `/auth/login` | Login and receive token |
| `GET` | `/todos` | List current user's todos |
| `POST` | `/todos` | Create todo |
| `PATCH` | `/todos/{id}/complete` | Complete todo |
| `DELETE` | `/todos/{id}` | Delete todo |

## Terminal flow

The logger automatically shows the complete presentation flow:

```text
REQUEST      GET /todos
Auth         Token is valid
Presentation Todo list requested
Infrastructure MongoDB returned 3 todos
Application  Found 3 todos
RESPONSE     200 OK
```

Each important step also includes a Roman Urdu explanation. The database name
in the log changes automatically with the selected database.
