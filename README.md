# TodoFlow

TodoFlow combines a React/Redux frontend with a FastAPI backend built using
Domain-Driven Design (DDD). Follow this guide to run the main application on
Windows with PowerShell.

## Project folders

```text
backend/
|-- DDD/        # Main FastAPI backend
`-- MVC/        # Architecture comparison backend

frontend/       # Main React + Redux Toolkit frontend
```

## Requirements

Install these before continuing:

- Python 3.10 or newer
- Node.js 18 or newer
- At least one todo database: Firestore, MongoDB, or PostgreSQL
- A Firebase project and service-account JSON file only when using Firestore

The DDD backend stores both users and todos in the selected database. Firestore,
MongoDB, and PostgreSQL accounts are separate from each other.

## First-time setup

### 1. Prepare your database

For Firestore, download a Firebase service-account JSON file and save it as
`backend/DDD/serviceAccountKey.json`. Firebase Authentication does not need to
be enabled because Firestore itself stores the selected database's accounts.

`serviceAccountKey.json` is excluded by `.gitignore`; never commit it.
For MongoDB or PostgreSQL, use the connection values in `backend/DDD/.env`.

### 2. Install the DDD backend

Open PowerShell in the repository root:

```powershell
cd backend\DDD
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### 3. Install the frontend

Open another PowerShell window in the repository root:

```powershell
cd frontend
npm ci
```

## Run the application

Keep two PowerShell terminals open.

### Terminal 1 — DDD backend

From the repository root:

```powershell
cd backend\DDD
.\.venv\Scripts\Activate.ps1

# Choose firestore, mongodb, or postgresql.
$env:DATABASE = "firestore"
python -m uvicorn main:app --reload
```

To switch databases, stop the backend, change only `DATABASE`, and start it
again. Connection settings can be kept in `backend/DDD/.env`:

```powershell
# MongoDB
$env:DATABASE = "mongodb"
python -m uvicorn main:app --reload

# PostgreSQL
$env:DATABASE = "postgresql"
python -m uvicorn main:app --reload
```

Copy `backend/DDD/.env.example` to `backend/DDD/.env` and add your MongoDB URI
or PostgreSQL URL. The PostgreSQL table and MongoDB collection/index are created
automatically.

Backend URLs:

- API: <http://127.0.0.1:8000>
- Swagger documentation: <http://127.0.0.1:8000/docs>
- ReDoc documentation: <http://127.0.0.1:8000/redoc>

### Terminal 2 — frontend

From the repository root:

```powershell
cd frontend
npm run dev
```

Open <http://localhost:5173> in the browser.

The frontend uses `http://127.0.0.1:8000` by default. If the backend runs on a
different URL, create `frontend/.env`:

```env
VITE_API_URL=http://127.0.0.1:8000
```

Restart `npm run dev` after changing `.env`.

## Verify the projects

Open the backend health check at <http://127.0.0.1:8000> and create a
production frontend build:

```powershell
cd frontend
npm run build
```

## Common problems

### PowerShell blocks virtual-environment activation

Run this once in the current terminal, then activate the environment again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### The frontend cannot connect

Confirm that the backend terminal is running on `http://127.0.0.1:8000` and
that `VITE_API_URL` is correct.

### Signup or login fails

Confirm which `DATABASE` is active. An account created in Firestore must sign up
again in MongoDB or PostgreSQL because each database has separate users.

## More documentation

- [Detailed DDD backend guide](backend/DDD/README.md)
- [Frontend architecture guide](frontend/README.md)
- [Redux Toolkit guide](frontend/REDUX_TOOLKIT_GUIDE.md)
- [DDD vs MVC comparison](docs/architecture.md)
- [Postman testing guide](docs/api-testing.md)
