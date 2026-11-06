"""Small terminal logger used by every backend layer."""

from contextvars import ContextVar
from http import HTTPStatus
from itertools import count
import logging
import os
import sys
from time import perf_counter

from fastapi import FastAPI, Request


# Aik named logger use hota hai taa-ke tamam DDD layers same format mein output
# dein aur root/Uvicorn logger ke sath duplicate lines print na hon.
logger = logging.getLogger("todoflow.ddd")
logger.setLevel(os.environ["LOG_LEVEL"].upper())
logger.propagate = False

if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)-5s | %(message)s",
        datefmt="%H:%M:%S",
    ))
    logger.addHandler(handler)

# Har request ko #001 jaisa number milta hai. ContextVar async/concurrent
# requests ke logs ko unki correct request identity ke sath rakhta hai.
_request_number = count(1)
_current_request = ContextVar("current_request", default=None)


def log_step(area: str, english: str, roman_urdu: str) -> None:
    """Print one bilingual step with its layer and request number.

    Kyun: Beginner terminal mein request ka Presentation se Infrastructure tak
    complete flow easily follow kar sake.
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
    """Print a short error without intentionally logging passwords or tokens.

    Kyun: Debugging information mile lekin authentication secrets logs mein na
    jayen.
    """
    request = _current_request.get()
    label = f"{request} | {area}" if request else area
    logger.error("%s | %s", label, message)


def install_request_logging(app: FastAPI) -> None:
    """Install middleware that logs every request, response, and duration.

    Kyun: Har layer ke messages ko clear start/end boundary aur timing milti hai.
    Uvicorn access log disable hota hai taa-ke same request twice print na ho.
    """
    logging.getLogger("uvicorn.access").disabled = True

    @app.middleware("http")
    async def request_logger(request: Request, call_next):
        """Wrap one HTTP request and keep its number in the logging context."""
        # Browser CORS preflight common background request hai; isko skip karne
        # se terminal main application flow par focused rehta hai.
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
            # Request finish hone par context reset karna zaroori hai, warna next
            # request ko previous request ka number mil sakta hai.
            _current_request.reset(token)
