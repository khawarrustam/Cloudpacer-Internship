# Todo DDD backend

A beginner-friendly FastAPI backend using Domain-Driven Design and Clean Architecture.

Roman Urdu: Backend ko chhoti layers mein divide kiya gaya hai. Har layer ka aik clear kaam hai, is liye code ko trace karna asaan hai.

## Start here

This API supports:

- signup and login with Firebase Authentication
- create a todo
- list the signed-in user's todos
- complete a todo
- delete a todo
- temporary in-memory storage or Firebase Firestore

## What DDD means here

DDD means the business rules live in the domain, away from FastAPI and Firebase.

Examples:

- a title must contain 3 to 120 characters
- priority must be LOW, MEDIUM, or HIGH
- a completed todo cannot be completed again
- one user cannot change another user's todo

Roman Urdu: Business rules `domain` folder mein hain. API aur database sirf bahar ki details hain.

## Easy architecture

```text
HTTP request
    |
    v
Presentation layer
FastAPI route and request schema
    |
    v
Application layer
Use case runs one workflow
    |
    v
Domain layer
Entity checks business rules
    |
    v
Repository interface
    |
    v
Infrastructure layer
Memory or Firestore saves data
```

The dependency direction stays simple:

```text
Presentation -> Application -> Domain
Infrastructure -------------> Domain
bootstrap.py connects the real objects
```

Roman Urdu: Andar wali domain layer ko FastAPI ya Firebase import nahi karna chahiye.

## Folder guide

```text
todo_api/
|-- main.py                    # Creates the FastAPI app
|-- requirements.txt
|-- clear_db.py                # Optional Firebase cleanup script
|-- reformat_logs.py           # Checks print lines for emojis
|
+-- src/
    |-- bootstrap.py           # Connects repositories and use cases
    |
    |-- domain/
    |   |-- entities.py        # TodoItem and complete rule
    |   |-- value_objects.py   # TaskTitle and Priority
    |   |-- exceptions.py      # Named business errors
    |   |-- repositories.py    # Todo storage contract
    |   +-- auth_repositories.py
    |
    |-- application/
    |   |-- dtos.py            # Commands and TodoDTO
    |   |-- mappers.py         # TodoItem -> TodoDTO
    |   +-- use_cases/         # Create, list, complete, delete, auth
    |
    |-- infrastructure/
    |   +-- repositories/
    |       |-- in_memory_todo_repo.py
    |       |-- firestore_todo_repo.py
    |       +-- firebase_auth_repo.py
    |
    |-- presentation/
    |   +-- api/
    |       |-- todo_router.py
    |       |-- auth_router.py
    |       |-- schemas.py
    |       |-- auth_schemas.py
    |       +-- dependencies.py
    |
    +-- shared/
        +-- console.py          # Easy English + Roman Urdu prints
```

## One request from start to finish

Example: `POST /todos`

1. `todo_router.py` receives JSON.
2. Pydantic validates the request.
3. The router creates `CreateTodoCommand`.
4. `CreateTodoUseCase` asks `TodoItem.create` to build a valid entity.
5. The use case calls the repository contract.
6. Memory or Firestore saves the entity.
7. `todo_to_dto` makes plain output data.
8. FastAPI returns JSON.

Roman Urdu: Request router se use case, phir domain, phir repository tak jati hai. Result isi flow se wapas aata hai.

## Requirements

- Python 3.10 or newer
- a Firebase project for signup and login
- a Firebase service account JSON file
- the Firebase Web API key

Important: `USE_FIREBASE=false` only changes todo storage to memory. Authentication still uses Firebase.

Roman Urdu: Memory mode mein todos temporary hotay hain, lekin login phir bhi Firebase se hota hai.

## Firebase setup

1. Open Firebase Console.
2. Enable Email/Password in Authentication.
3. Download a service account JSON file.
4. Save it in `todo_api` as `serviceAccountKey.json`.
5. Copy the Web API key from Project Settings.

The credentials file is ignored by Git. Never commit it.

## Install and run

Open PowerShell in this folder:

```powershell
cd "Todo-List\todo_api"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Set the Firebase values for the current PowerShell window:

```powershell
$env:FIREBASE_CREDENTIALS_PATH="serviceAccountKey.json"
$env:FIREBASE_WEB_API_KEY="your-firebase-web-api-key"
```

Choose todo storage.

### Easy local storage

```powershell
$env:USE_FIREBASE="false"
uvicorn main:app --reload
```

Todos disappear when the server stops.

### Firestore storage

```powershell
$env:USE_FIREBASE="true"
uvicorn main:app --reload
```

Open:

- API health: `http://127.0.0.1:8000/`
- Swagger docs: `http://127.0.0.1:8000/docs`

## API routes

| Method | Route | Login needed | Purpose |
|---|---|---:|---|
| POST | `/auth/signup` | No | Create an account |
| POST | `/auth/login` | No | Get a Firebase ID token |
| GET | `/todos` | Yes | List your todos |
| POST | `/todos` | Yes | Create a todo |
| PATCH | `/todos/{id}/complete` | Yes | Complete a todo |
| DELETE | `/todos/{id}` | Yes | Delete a todo |
| GET | `/` | No | Health check |

Protected routes need this header:

```text
Authorization: Bearer YOUR_FIREBASE_ID_TOKEN
```

Example create body:

```json
{
  "title": "Read the DDD flow",
  "priority": "HIGH"
}
```

## Print output

Backend runtime prints show the complete data direction:

```text
[DATA FLOW]
  FROM LAYER : PRESENTATION LAYER
  FROM       : src/presentation/api/todo_router.py
  TO LAYER   : APPLICATION LAYER
  TO         : src/application/use_cases/create_todo.py
  DATA       : title=Learn DDD, priority=HIGH
  English: The router sent a create command to the use case.
  Roman Urdu: Router ne create command use case ko bheji.
```

The flow continues through these labels:

- `CLIENT / HTTP`: React frontend or request headers
- `PRESENTATION LAYER`: FastAPI routers and dependencies
- `APPLICATION LAYER`: use cases, commands, DTOs, and mappers
- `DOMAIN LAYER`: entities, value objects, and business rules
- `INFRASTRUCTURE LAYER`: repository adapter files
- `INFRASTRUCTURE STORAGE`: temporary RAM storage
- `EXTERNAL SERVICE`: Firebase or Firestore

All prints are routed through `src/shared/console.py`. They use plain text and no emojis.

Passwords and tokens are always shown as `hidden`; their real values are never printed.

Roman Urdu: Har print layer aur file dono batata hai: data kahan se aaya aur kahan ja raha hai. Password aur token kabhi print nahi hotay.

Check print statements with:

```powershell
python reformat_logs.py
```

## Run tests

```powershell
python -m pytest -q
```

The use-case tests use `InMemoryTodoRepository`, so they do not write to Firestore.

## How to add a new todo action

Example: rename a todo.

1. Put the rename rule on `TodoItem`.
2. Add `RenameTodoCommand` in `application/dtos.py`.
3. Add `RenameTodoUseCase`.
4. Add any needed method to `ITodoRepository`.
5. Implement that method in both repositories.
6. Add the HTTP route.
7. Connect the use case in `bootstrap.py`.
8. Add a test.

Roman Urdu: Naya feature pehle business rule se start karo, phir bahar API tak jao.

## Common problems

### `Default app does not exist`

Make sure the app starts through `main.py` and the service account path is correct.

### Firebase says the API key is invalid

Set the correct `FIREBASE_WEB_API_KEY`, then restart Uvicorn.

### Login works but todos disappear

You are using `USE_FIREBASE=false`. Use Firestore mode to keep todos after a restart.

### Browser shows a CORS error

Use the Vite URL `http://localhost:5173` or `http://127.0.0.1:5173`. Add another allowed origin in `main.py` only if your frontend runs elsewhere.

### Port 8000 is busy

Run on another port and also update the frontend `VITE_API_URL`:

```powershell
uvicorn main:app --reload --port 8001
```

## Safe cleanup script

`clear_db.py` permanently deletes Firebase todos and authentication users. Run it only when you intentionally want to clear development data:

```powershell
python clear_db.py
```
