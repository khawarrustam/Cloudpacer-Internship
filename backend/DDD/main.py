"""TodoFlow DDD backend entry point.

Presentation flow: API -> Application -> Domain -> Infrastructure.
"""

import os
from pathlib import Path

import firebase_admin
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import credentials


PROJECT_DIRECTORY = Path(__file__).parent
ENV_FILE = PROJECT_DIRECTORY / ".env"


def _load_env_file(env_path: Path) -> None:
    """Read settings from .env when python-dotenv is unavailable.

    Kyun: App ko required configuration mil jaye, even if the optional
    python-dotenv package is not installed.
    """
    if not env_path.is_file():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = value


# Pehle standard python-dotenv use karo. Agar package missing ho to upar wala
# simple parser use hoga, is liye app ka startup unnecessarily fail nahi hota.
try:
    from dotenv import load_dotenv

    load_dotenv(ENV_FILE)
except ImportError:
    _load_env_file(ENV_FILE)

from src.application.use_cases import AuthUseCases, TodoUseCases
from src.domain.models import TodoRepository
from src.infrastructure import (
    FirebaseAuthRepository,
    FirestoreTodoRepository,
    MongoTodoRepository,
    PostgreSQLTodoRepository,
)
from src.logs import install_request_logging, log_step
from src.presentation.routes import (
    auth_router,
    configure_use_cases,
    todo_router,
)


def required_setting(name: str) -> str:
    """Return a required setting or stop with a clear error.

    Kyun: Missing configuration ko baad mein confusing database/API error
    banne ke bajaye startup par hi beginner-friendly message mil jata hai.
    """
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required setting: {name}")
    return value


def setting_is_true(name: str) -> bool:
    """Convert a text setting such as 'true' into a Python boolean.

    Kyun: Environment variables hamesha text hoti hain, jabke Uvicorn ko
    reload ke liye True/False value chahiye hoti hai.
    """
    return required_setting(name).lower() == "true"


def connect_firebase() -> None:
    """Connect Firebase once for signup, login, and token verification.

    Kyun: Firebase authentication har database mode mein use hoti hai, is liye
    uska setup database selection se pehle hota hai.
    """
    if firebase_admin._apps:
        return

    credential_file = Path(required_setting("FIREBASE_CREDENTIALS_PATH"))
    if not credential_file.is_absolute():
        credential_file = PROJECT_DIRECTORY / credential_file

    firebase_admin.initialize_app(credentials.Certificate(credential_file))
    log_step(
        "Setup",
        "Firebase authentication connected.",
        "Firebase authentication connect ho gayi.",
    )


def get_selected_database() -> str:
    """Read and normalize the database selected in the terminal or .env.

    `firebase` ko `firestore` alias diya gaya hai taa-ke beginner command mein
    Firebase likhe to bhi uska Firestore database select ho jaye.
    """
    database = os.getenv("DATABASE", "firestore").strip().lower()
    if database == "firebase":
        return "firestore"
    return database


def create_todo_repository(database: str) -> TodoRepository:
    """Create the repository for the database selected in PowerShell.

    Kyun: Baqi application ko database details se independent rakhna hai.
    `DATABASE` change karne se Firestore, MongoDB, ya PostgreSQL select hota hai.
    """
    if database == "firestore":
        firebase_app = firebase_admin.get_app()
        return FirestoreTodoRepository(
            firebase_app.project_id,
            firebase_app.credential.get_credential(),
        )

    if database == "mongodb":
        return MongoTodoRepository(
            required_setting("MONGODB_URI"),
            required_setting("MONGODB_DATABASE"),
            required_setting("MONGODB_TODO_COLLECTION"),
        )

    if database == "postgresql":
        return PostgreSQLTodoRepository(required_setting("POSTGRESQL_URL"))

    raise RuntimeError(
        "DATABASE must be firestore (or firebase), mongodb, or postgresql."
    )


def create_app() -> FastAPI:
    """Build and configure the complete FastAPI application.

    Kya: CORS, request logs, Firebase Auth, selected database, use cases, aur
    routes ko connect karta hai.
    Kyun: Startup wiring aik jagah rahe aur har layer ki responsibility clear ho.
    """
    allowed_origins = [
        origin.strip()
        for origin in required_setting("CORS_ORIGINS").split(",")
        if origin.strip()
    ]

    app = FastAPI(title=required_setting("APP_NAME"))
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    install_request_logging(app)

    # Firebase sirf signup/login aur token verification ke liye use hota hai.
    # Todo Firestore, MongoDB, ya PostgreSQL kisi mein bhi save ho sakta hai.
    connect_firebase()

    # PowerShell mein DATABASE change karke DB switch hoti hai; Python code edit
    # karne ki zaroorat nahi. Value na mile to existing Firestore default hai.
    database = get_selected_database()
    todo_repository = create_todo_repository(database)
    log_step(
        "Setup",
        f"Todo database connected: {database}.",
        f"Todo database connect ho gaya: {database}.",
    )

    configure_use_cases(
        TodoUseCases(todo_repository),
        AuthUseCases(FirebaseAuthRepository()),
    )
    app.include_router(auth_router)
    app.include_router(todo_router)

    @app.get("/", tags=["Health"])
    def health_check():
        """Tell the caller that the API is running and show the active DB.

        Kyun: Browser/Postman se jaldi verify ho jata hai ke correct database
        select hua hai aur backend successfully start ho chuka hai.
        """
        return {
            "status": "ok",
            "architecture": required_setting("APP_ARCHITECTURE"),
            "database": database,
        }

    log_step(
        "Setup",
        "API, services, and repositories are ready.",
        "API, services aur repositories ready hain.",
    )
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    # Yeh block sirf `python main.py` par chalta hai. `uvicorn main:app` use
    # karne par Uvicorn directly upar banaya hua `app` object load karta hai.
    uvicorn.run(
        "main:app",
        host=required_setting("BACKEND_HOST"),
        port=int(required_setting("BACKEND_PORT")),
        reload=setting_is_true("BACKEND_RELOAD"),
    )
