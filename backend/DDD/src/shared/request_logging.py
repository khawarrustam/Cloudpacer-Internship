"""HTTP request logging that keeps terminal output grouped and readable."""

import logging
from time import perf_counter

from fastapi import FastAPI, Request

from src.shared.console import begin_request, fail_request, finish_request


def install_request_logging(application: FastAPI) -> None:
    """Replace duplicate Uvicorn access lines with one TodoFlow request group."""
    logging.getLogger("uvicorn.access").disabled = True

    @application.middleware("http")
    async def log_request(request: Request, call_next):
        # Browser CORS checks are implementation noise, not application actions.
        if request.method == "OPTIONS":
            return await call_next(request)

        started_at = perf_counter()
        token = begin_request(request.method, request.url.path)

        try:
            response = await call_next(request)
        except Exception:
            duration_ms = (perf_counter() - started_at) * 1000
            fail_request(
                token,
                request.method,
                request.url.path,
                duration_ms,
            )
            raise

        duration_ms = (perf_counter() - started_at) * 1000
        finish_request(
            token,
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response
