"""Small bilingual terminal logger shared by every backend layer."""

from contextvars import ContextVar
from http import HTTPStatus
from itertools import count
import logging
import sys
from time import perf_counter

from fastapi import FastAPI, Request

from app.config import get_settings


# Aik named logger tamam layers ko same format deta hai aur duplicate Uvicorn
# access lines ko avoid karta hai.
logger = logging.getLogger("todoflow.ddd")
logger.setLevel(get_settings().log_level.upper())
logger.propagate = False

if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)-5s | %(message)s",
        datefmt="%H:%M:%S",
    ))
    logger.addHandler(handler)

# ContextVar concurrent requests ke logs ko unki correct request identity ke
# sath rakhta hai.
_request_number = count(1)
_current_request = ContextVar("current_request", default=None)


def log_step(area: str, english: str, roman_urdu: str) -> None:
    """What: Print one bilingual application step.

    When: A layer completes an important request action.
    How: Attach the current request number without logging sensitive values.
    """
    request = _current_request.get()
    label = f"{request} | {area}" if request else area
    logger.info(
        "%s | %s\n         |       |      %s",
        label,
        english,
        roman_urdu,
    )


def log_error(area: str, message: str) -> None:
    """What: Print a safe technical error.

    When: Infrastructure or authentication cannot complete an operation.
    How: Log the supplied message; callers never pass passwords or tokens.
    """
    request = _current_request.get()
    label = f"{request} | {area}" if request else area
    logger.error("%s | %s", label, message)


def install_request_logging(app: FastAPI) -> None:
    """What: Install request/response timing middleware.

    When: The composition root creates the FastAPI application.
    How: Give every non-OPTIONS request an ID and reset its context afterward.
    """
    logging.getLogger("uvicorn.access").disabled = True

    @app.middleware("http")
    async def request_logger(request: Request, call_next):
        """Wrap one HTTP request inside its logging context."""
        if request.method == "OPTIONS":
            return await call_next(request)

        label = (
            f"#{next(_request_number):03d} "
            f"{request.method} {request.url.path}"
        )
        token = _current_request.set(label)
        started = perf_counter()
        logger.info("REQUEST  | %s", label)

        try:
            response = await call_next(request)
            duration = (perf_counter() - started) * 1000
            try:
                status_text = HTTPStatus(response.status_code).phrase
            except ValueError:
                status_text = "Unknown"
            logger.info(
                "RESPONSE | %s | %s %s | %.0f ms\n",
                label,
                response.status_code,
                status_text,
                duration,
            )
            return response
        except Exception:
            duration = (perf_counter() - started) * 1000
            logger.exception(
                "RESPONSE | %s | 500 Internal Server Error | %.0f ms\n",
                label,
                duration,
            )
            raise
        finally:
            _current_request.reset(token)
