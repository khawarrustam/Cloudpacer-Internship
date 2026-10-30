# TodoFlow MVC API

This FastAPI service implements the TodoFlow backend with the traditional
Model-View-Controller (MVC) pattern. It exists beside the DDD service to make
the architectural trade-offs easy to compare using the same domain problem.

## Capabilities

- Firebase user signup
- Firestore-backed todo CRUD operations
- FastAPI request validation and generated API documentation
- Automatic Firebase credential discovery
- A compact codebase suitable for learning traditional MVC

## Architecture

```text
HTTP request
    |
    v
Controller       FastAPI routes and workflow coordination
    |       \
    v        v
Model          View
Rules/data     Pydantic request and response schemas
    |
    v
Database         Firebase Firestore connection
```

MVC uses fewer files than the DDD implementation, but controllers know more
about persistence and orchestration. See the
[architecture comparison](../../docs/architecture.md) for a detailed analysis.

## Project structure

```text
backend/MVC/
|-- main_mvc.py
|-- requirements.txt
`-- src_mvc/
    |-- controllers/
    |-- models/
    |-- views/
    `-- db/
```

## Requirements

- Python 3.10+
- A Firebase project with Firestore enabled
- `serviceAccountKey.json` in either `backend/MVC` or `backend/DDD`

The application checks both locations automatically. The credential file is
ignored by Git and must never be committed.

## Installation

From the repository root:

```powershell
cd backend\MVC
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Running locally

```powershell
python main_mvc.py
```

Service URLs:

- API: <http://127.0.0.1:8001>
- Swagger UI: <http://127.0.0.1:8001/docs>
- ReDoc: <http://127.0.0.1:8001/redoc>

No Firebase environment variable is required for the repository's current
folder layout. `FIREBASE_CREDENTIALS_PATH` remains available as an optional
override for deployments.

## API endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `POST` | `/auth/signup` | Create a Firebase user |
| `GET` | `/todos` | List todos |
| `GET` | `/todos/{todo_id}` | Get one todo |
| `POST` | `/todos` | Create a todo |
| `PATCH` | `/todos/{todo_id}/complete` | Complete a todo |
| `DELETE` | `/todos/{todo_id}` | Delete a todo |

## DDD comparison

| Concern | MVC | DDD/Clean Architecture |
|---|---|---|
| Business rules | Model helpers | Domain entities/value objects |
| Workflow | Controllers | Application use cases |
| Persistence | Controller/database layer | Repository interfaces and adapters |
| Dependency injection | Direct imports | Use cases connected in `main.py` |
| Test isolation | More infrastructure coupling | In-memory repository adapters |
| Best fit | Small, straightforward services | Complex and evolving business domains |

## Troubleshooting

- **Credential error:** confirm the JSON file exists in `backend/DDD` or
  `backend/MVC`.
- **Firestore request fails:** confirm Firestore is enabled for the project.
- **Port 8001 is busy:** change the port in `main_mvc.py` or run Uvicorn with an
  explicit port.

## Related documentation

- [Repository run guide](../../README.md)
- [DDD backend documentation](../DDD/README.md)
- [Architecture comparison](../../docs/architecture.md)
- [Postman collections](../../postman/)
