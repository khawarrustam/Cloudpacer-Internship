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
- A Firebase project with Email/Password authentication enabled
- A Firebase service-account JSON file

The DDD backend can keep todos either temporarily in memory or permanently in
Firestore. Firebase is still required for signup and login in both modes.

## First-time setup

### 1. Prepare Firebase

1. Enable **Email/Password** in Firebase Authentication.
2. Download a service-account JSON file.
3. Save it as `backend/DDD/serviceAccountKey.json`.

`serviceAccountKey.json` is excluded by `.gitignore`; never commit it.
The backend already defaults to this filename and includes the configured Web
API key, so no Firebase environment variables are required.

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

$env:USE_FIREBASE = "false"

python -m uvicorn main:app --reload
```

`USE_FIREBASE=false` stores todos in memory, so they disappear when the backend
stops. To save todos in Firestore, use:

```powershell
$env:USE_FIREBASE = "true"
python -m uvicorn main:app --reload
```

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

Confirm that Email/Password authentication is enabled and that
`backend/DDD/serviceAccountKey.json` belongs to the configured Firebase project.

## More documentation

- [Detailed DDD backend guide](backend/DDD/README.md)
- [Frontend architecture guide](frontend/README.md)
- [Redux Toolkit guide](frontend/REDUX_TOOLKIT_GUIDE.md)
- [DDD vs MVC comparison](docs/architecture.md)
- [Postman testing guide](docs/api-testing.md)
