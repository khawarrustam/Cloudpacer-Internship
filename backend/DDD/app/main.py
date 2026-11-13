"""FastAPI composition root: configure and connect all application layers."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.application.auth_service import AuthService
from app.application.reminder_service import ReminderService
from app.application.todo_service import TodoService
from app.config import Settings, get_settings
from app.infrastructure.reminder_scheduler import ReminderScheduler
from app.infrastructure.repository_factory import create_repositories
from app.infrastructure.resend_email_sender import ResendEmailSender
from app.logging import install_request_logging, log_step
from app.presentation.routers.auth import router as auth_router
from app.presentation.routers.todos import router as todo_router


def create_app(settings: Settings | None = None) -> FastAPI:
    """What: Build and wire the complete FastAPI application.

    When: Uvicorn imports the app or a test needs an isolated application.
    How: Configure middleware, repositories, services, routers, and health.
    """
    # Normal run cached .env settings use karta hai; optional settings tests ya
    # alternate app instance ko explicit configuration dene deti hain.
    settings = settings or get_settings()
    # Composition root concrete database choose karta hai. Domain, application,
    # aur presentation ko selected driver ka direct knowledge nahi hota.
    todo_repository, auth_repository = create_repositories(settings)
    todo_service = TodoService(todo_repository)
    auth_service = AuthService(auth_repository)
    reminder_service = ReminderService(
        repository=todo_repository,
        email_sender=ResendEmailSender(
            api_key=settings.resend_api_key,
            sender=settings.reminder_email_from,
        ),
        batch_size=settings.reminder_batch_size,
    )
    reminder_scheduler = ReminderScheduler(
        service=reminder_service,
        interval_seconds=settings.reminder_scan_interval_seconds,
    )

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        """Start and stop the reminder scheduler with the API process."""
        reminder_scheduler.start()
        try:
            yield
        finally:
            reminder_scheduler.shutdown()

    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    install_request_logging(app)

    # Routes database objects directly create nahi karti. Ready services app.state
    # par rakhne se dependencies har request mein correct instances deti hain.
    app.state.todo_service = todo_service
    app.state.auth_service = auth_service
    app.state.reminder_scheduler = reminder_scheduler
    app.state.settings = settings

    log_step(
        "Setup",
        f"Todo and auth database connected: {settings.selected_database}.",
        f"Todo aur auth database connect ho gaya: {settings.selected_database}.",
    )

    # Feature routers mount karne ke baad public URLs /auth/* aur /todos/* banti hain.
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
