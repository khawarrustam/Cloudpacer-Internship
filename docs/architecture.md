# TodoFlow Architecture

This repository contains the same Todo API in two styles:

- `backend/DDD` — business rules are separated from frameworks and storage.
- `backend/MVC` — controllers directly coordinate models, views, and Firebase.

## Minimal DDD flow

```text
Frontend HTTP request
        |
        v
presentation/       HTTP DTOs, routes, Firebase token check
        |
        v
application/        Use-case input/output DTOs and workflows
        |
        v
domain/models.py    Todo entity, title validation, completion rule
        |
        v
infrastructure/     Memory or Firebase Firestore implementation
```

`main.py` starts Firebase, chooses the repository, creates the application
services, and connects them to `presentation/routes.py`.

## DDD files

| File | Presentation answer |
|---|---|
| `main.py` | Starts and connects the application |
| `src/presentation/dto.py` | Defines HTTP request and response shapes |
| `src/presentation/routes.py` | Receives requests and returns responses |
| `src/application/dto.py` | Defines use-case input and output objects |
| `src/application/use_cases.py` | Runs the application's workflows |
| `src/domain/models.py` | Contains business data, rules, and contracts |
| `src/infrastructure/repositories.py` | Talks to RAM, Firebase Auth, and Firestore |
| `src/logs.py` | Shows the request flow in the terminal |

## Example: create todo

1. `POST /todos` reaches `presentation/routes.py`.
2. Firebase token identifies the current user.
3. `TodoUseCases.create()` runs in `application/use_cases.py`.
4. `TodoItem.create()` validates the title in `domain/models.py`.
5. The selected repository saves it through `infrastructure/repositories.py`.
6. FastAPI sends the created todo back to the frontend.

## Why repository contracts remain

`TodoRepository` in `domain/models.py` defines the four storage operations. Both
`InMemoryTodoRepository` and `FirestoreTodoRepository` follow that contract.
The application service therefore does not care which database is selected.

## DDD versus MVC

| Point | DDD backend | MVC backend |
|---|---|---|
| Business rules | `domain/models.py` | Model functions |
| Request handling | `presentation/routes.py` | Controllers |
| Storage access | Repository contract and implementation | Controller calls Firebase |
| File count | Four small layer folders | MVC folders |
| Best use | Clear rules and replaceable storage | Small direct applications |

## Terminal flow

`logs.py` keeps the architecture visible while the API runs:

```text
REQUEST      #001 POST /todos
Auth         Token is valid
Presentation Create todo request received
Infrastructure Saved todo in Firebase Firestore
Application  Todo created and saved
RESPONSE     201 Created
```
