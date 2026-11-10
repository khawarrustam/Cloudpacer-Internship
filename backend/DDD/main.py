"""Beginner-compatible entrypoint for `uvicorn main:app` and `python main.py`."""

from app.config import get_settings
from app.main import app, create_app


__all__ = ["app", "create_app"]


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=settings.backend_reload,
    )
