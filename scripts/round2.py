"""Instructor workflow to dispatch round 2 tasks."""

from __future__ import annotations

import httpx

from app.database import session_scope
from app.logging import configure_logging, get_logger
from app.models import RepoSubmission


configure_logging()
logger = get_logger(__name__)


def dispatch_round_two(task: RepoSubmission) -> None:
    payload = {
        "email": task.email,
        "secret": "placeholder",
        "task": task.task,
        "round": 2,
        "nonce": "nonce-placeholder",
        "brief": "Round two instructions placeholder",
        "checks": ["README updated"],
        "evaluation_url": task.pages_url,
        "attachments": [],
    }
    response = httpx.post(task.pages_url, json=payload, timeout=30)
    logger.info("Round two dispatched", task=task.task, status=response.status_code)


def main() -> None:
    with session_scope() as session:
        for submission in session.query(RepoSubmission).all():
            dispatch_round_two(submission)


if __name__ == "__main__":
    main()

