"""Structured logging setup for the service."""

from __future__ import annotations

import logging
import sys
from typing import Any, Dict

import structlog


def _configure_structlog() -> None:
    """Configure structlog processors and standard library integration."""

    timestamper = structlog.processors.TimeStamper(fmt="iso")

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        timestamper,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ]

    structlog.configure(
        processors=shared_processors,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.dev.ConsoleRenderer(colors=True),
        foreign_pre_chain=[timestamper],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    logging.basicConfig(
        level=logging.INFO,
        handlers=[handler],
        force=True,
    )


def configure_logging() -> None:
    """Public entrypoint to initialize structured logging."""

    _configure_structlog()


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Return a structlog logger with provided name."""

    return structlog.stdlib.get_logger(name)


def bind_request_context(request_id: str | None = None, **extra: Dict[str, Any]) -> None:
    """Bind contextual information for the current request lifecycle."""

    structlog.contextvars.clear_contextvars()
    if request_id:
        structlog.contextvars.bind_contextvars(request_id=request_id)
    if extra:
        structlog.contextvars.bind_contextvars(**extra)

