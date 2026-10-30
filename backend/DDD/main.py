"""TodoFlow DDD backend entry point.

Presentation flow: API -> Application -> Domain -> Infrastructure.
"""

import os
from pathlib import Path

import firebase_admin
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import credentials


def _load_env_file(env_path: Path) -> None:
    """Load key-value pairs from .env without requiring third-party packages."""
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


# Try python-dotenv first, fall back to built-in parser if not installed.
try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).with_name(".env"))
except ImportError:
    _load_env_file(Path(__file__).with_name(".env"))

from src.application.use_cases import AuthUseCases, TodoUseCases
from src.infrastructure.repositories import (
    FirebaseAuthRepository,
    FirestoreTodoRepository,
    InMemoryTodoRepository,
)
from src.logs import install_request_logging, log_step
from src.presentation.routes import (
    auth_router,
    configure_use_cases,
    todo_router,
)


def required_setting(name: str) -> str:
    """Return one required environment setting with a clear error."""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required setting: {name}")
    return value


def setting_is_true(name: str) -> bool:
    return required_setting(name).lower() == "true"


def create_app() -> FastAPI:
    """Start Firebase, select storage, and connect the four DDD layers."""
    app = FastAPI(title=required_setting("APP_NAME"))
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            origin.strip()
            for origin in required_setting("CORS_ORIGINS").split(",")
            if origin.strip()
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    install_request_logging(app)

    # Firebase Auth is used in both memory and Firestore modes.
    if not firebase_admin._apps:
        credential_file = Path(required_setting("FIREBASE_CREDENTIALS_PATH"))
        if not credential_file.is_absolute():
            credential_file = Path(__file__).parent / credential_file
        firebase_admin.initialize_app(
            credentials.Certificate(credential_file)
        )
        log_step(
            "Setup",
            "Firebase authentication connected.",
            "Firebase authentication connect ho gayi.",
        )

    # USE_FIREBASE=true stores todos permanently; default mode uses RAM.
    if setting_is_true("USE_FIREBASE"):
        firebase_app = firebase_admin.get_app()
        todo_repository = FirestoreTodoRepository(
            firebase_app.project_id,
            firebase_app.credential.get_credential(),
        )
        log_step(
            "Setup",
            "Todo storage: Firebase Firestore.",
            "Todo storage Firebase Firestore hai.",
        )
    else:
        todo_repository = InMemoryTodoRepository()
        log_step(
            "Setup",
            "Todo storage: temporary memory.",
            "Todo storage temporary memory hai.",
        )

    configure_use_cases(
        TodoUseCases(todo_repository),
        AuthUseCases(FirebaseAuthRepository()),
    )
    app.include_router(auth_router)
    app.include_router(todo_router)

    @app.get("/", tags=["Health"])
    def health_check():
        return {
            "status": "ok",
            "architecture": required_setting("APP_ARCHITECTURE"),
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

    uvicorn.run(
        "main:app",
        host=required_setting("BACKEND_HOST"),
        port=int(required_setting("BACKEND_PORT")),
        reload=setting_is_true("BACKEND_RELOAD"),
    )
