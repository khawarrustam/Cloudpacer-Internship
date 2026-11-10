"""Beginner-compatible entrypoint for `uvicorn main:app` and `python main.py`."""

# Root file thin bridge hai: actual application wiring app/main.py mein rehti hai.
from app.config import get_settings
from app.main import app, create_app


__all__ = ["app", "create_app"]


if __name__ == "__main__":
    import uvicorn

    # Direct `python main.py` command bhi wahi typed host/port settings use kare.
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=settings.backend_reload,
    )
