"""FastAPI entry point.

English: This file creates the app and connects the main modules.
Roman Urdu: Yeh file app banati hai aur main modules ko connect karti hai.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.bootstrap import (
    create_todo_repository,
    initialize_firebase,
    wire_dependencies,
)
from src.presentation.api.auth_router import router as auth_router
from src.presentation.api.todo_router import router as todo_router
from src.shared.request_logging import install_request_logging


def health_check():
    """Small endpoint used to check that the server is running."""
    return {"status": "ok", "architecture": "DDD / Clean Architecture"}


def create_app() -> FastAPI:
    """Build and return the configured FastAPI application."""
    application = FastAPI(
        title="Todo DDD API",
        description="A beginner-friendly Todo API using DDD and Clean Architecture.",
    )

    # English: CORS lets the frontend call this API from another port.
    # Roman Urdu: CORS frontend ko doosre port se API call karne deta hai.
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    install_request_logging(application)

    initialize_firebase()
    todo_repo = create_todo_repository()
    wire_dependencies(application, todo_repo)

    application.include_router(auth_router)
    application.include_router(todo_router)
    application.add_api_route(
        "/",
        health_check,
        methods=["GET"],
        tags=["Health"],
    )
    return application


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
