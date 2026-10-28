"""Small, consistent logging helpers for the DDD backend.

The default console shows request boundaries and important business events.
Detailed layer-to-layer flow remains available at DEBUG level for maintainers,
but normal local development requires no logging setup.
"""

from contextvars import ContextVar, Token
from http import HTTPStatus
from itertools import count
import logging
import os
import re
import sys


LOGGER_NAME = "todoflow.ddd"
DEFAULT_LOG_LEVEL = "INFO"
_request_numbers = count(1)
_current_request: ContextVar[str | None] = ContextVar(
    "todoflow_current_request",
    default=None,
)
_SENSITIVE_VALUE = re.compile(
    r"(?i)\b(password|token|authorization)\s*=\s*([^,\s]+)"
)


def _configured_level() -> int:
    """Read a safe logging level from the environment."""
    level_name = os.getenv("TODOFLOW_LOG_LEVEL", DEFAULT_LOG_LEVEL).upper()
    return getattr(logging, level_name, logging.INFO)


def _build_logger() -> logging.Logger:
    """Create one stdout handler without duplicating messages on reload."""
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(_configured_level())
    logger.propagate = False

    if not any(getattr(handler, "_todoflow_handler", False) for handler in logger.handlers):
        handler = logging.StreamHandler(sys.stdout)
        handler._todoflow_handler = True  # type: ignore[attr-defined]
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)-5s | %(message)s",
                datefmt="%H:%M:%S",
            )
        )
        logger.addHandler(handler)

    return logger


logger = _build_logger()


def module_file(instance: object) -> str:
    """Return the Python file path for an injected repository object."""
    module_path = instance.__class__.__module__.replace(".", "/")
    return f"{module_path}.py"


def find_layer(location: str) -> str:
    """Return a short architecture-layer name for a code location."""
    clean_location = location.lower().replace("\\", "/")

    if "src/presentation/" in clean_location or "fastapi" in clean_location:
        return "Presentation"
    if "src/application/" in clean_location:
        return "Application"
    if "src/domain/" in clean_location:
        return "Domain"
    if "src/infrastructure/" in clean_location:
        return "Infrastructure"
    if "frontend" in clean_location or "http authorization" in clean_location:
        return "Client"
    if "firebase" in clean_location or "firestore" in clean_location:
        return "Firebase"
    if "ram" in clean_location or "temporary memory" in clean_location:
        return "Memory"

    return "Backend"


def _short_location(location: str) -> str:
    """Make a file/service label compact enough for one console line."""
    normalized = location.replace("\\", "/")
    return normalized.removeprefix("src/")


def _safe_data(data: str) -> str:
    """Hide common secret values before any diagnostic data is logged."""
    return _SENSITIVE_VALUE.sub(lambda match: f"{match.group(1)}=hidden", data)


def _message(english: str, roman_urdu: str) -> str:
    """Put the translation on its own indented line for readability."""
    show_urdu = os.getenv("TODOFLOW_SHOW_URDU", "true").lower() == "true"
    if not show_urdu:
        return english
    return f"{english}\n         |       |      {roman_urdu}"


def _area(area: str) -> str:
    """Add the active HTTP request to important application events."""
    request_label = _current_request.get()
    return f"{request_label} | {area}" if request_label else area


def begin_request(method: str, path: str) -> Token[str | None]:
    """Open one readable HTTP request group and return its context token."""
    request_number = next(_request_numbers)
    request_label = f"#{request_number:03d} {method.upper()} {path}"
    token = _current_request.set(request_label)
    logger.info("REQUEST  | %s", request_label)
    return token


def finish_request(
    token: Token[str | None],
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
) -> None:
    """Close a successful HTTP request group."""
    request_label = _current_request.get() or f"{method.upper()} {path}"
    try:
        status_text = HTTPStatus(status_code).phrase
    except ValueError:
        status_text = "Unknown"
    logger.info(
        "RESPONSE | %s | %s %s | %.0f ms\n",
        request_label,
        status_code,
        status_text,
        duration_ms,
    )
    _current_request.reset(token)


def fail_request(
    token: Token[str | None],
    method: str,
    path: str,
    duration_ms: float,
) -> None:
    """Close a failed HTTP request group without exposing exception details."""
    request_label = _current_request.get() or f"{method.upper()} {path}"
    logger.exception(
        "RESPONSE | %s | 500 Internal Server Error | %.0f ms\n",
        request_label,
        duration_ms,
    )
    _current_request.reset(token)


def print_flow(
    source: str,
    destination: str,
    data: str,
    english: str,
    roman_urdu: str,
) -> None:
    """Log detailed layer-to-layer flow at DEBUG level only."""
    source_label = f"{find_layer(source)}:{_short_location(source)}"
    destination_label = f"{find_layer(destination)}:{_short_location(destination)}"
    logger.debug(
        "%s | FLOW | %s -> %s | %s | %s",
        _current_request.get() or "Background",
        source_label,
        destination_label,
        _safe_data(data),
        _message(english, roman_urdu),
    )


def print_step(area: str, english: str, roman_urdu: str) -> None:
    """Log a concise normal application event."""
    logger.info("%s | %s", _area(area), _message(english, roman_urdu))


def print_error(area: str, english: str, roman_urdu: str) -> None:
    """Log a concise application error."""
    logger.error("%s | %s", _area(area), _message(english, roman_urdu))
