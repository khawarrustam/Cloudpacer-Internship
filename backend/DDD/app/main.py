"""FastAPI composition root: configure and connect all application layers."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.application.auth_service import AuthService
from app.application.todo_service import TodoService
from app.config import Settings, get_settings
from app.infrastructure.repository_factory import create_repositories
from app.logging import install_request_logging, log_step
from app.presentation.routers.auth import router as auth_router
from app.presentation.routers.todos import router as todo_router


def create_app(settings: Settings | None = None) -> FastAPI:
    """What: Build and wire the complete FastAPI application.

    When: Uvicorn imports the app or a test needs an isolated application.
    How: Configure middleware, repositories, services, routers, and health.
    """
    settings = settings or get_settings()
    app = FastAPI(title=settings.app_name)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    install_request_logging(app)

    # Composition root concrete database choose karta hai. Domain, application,
    # aur presentation ko selected driver ka direct knowledge nahi hota.
    todo_repository, auth_repository = create_repositories(settings)
    app.state.todo_service = TodoService(todo_repository)
    app.state.auth_service = AuthService(auth_repository)
    app.state.settings = settings

    log_step(
        "Setup",
        f"Todo and auth database connected: {settings.selected_database}.",
        f"Todo aur auth database connect ho gaya: {settings.selected_database}.",
    )

    app.include_router(auth_router)
    app.include_router(todo_router)

    @app.get("/", tags=["Health"])
    def health_check() -> dict[str, str]:
        """Show that the API is ready and identify its selected database."""
        return {
            "status": "ok",
            "architecture": settings.app_architecture,
            "database": settings.selected_database,
        }

    log_step(
        "Setup",
        "API, services, and repositories are ready.",
        "API, services aur repositories ready hain.",
    )
    return app


app = create_app()
