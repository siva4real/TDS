"""Prototype evaluation workflow."""

from __future__ import annotations

from app.database import session_scope
from app.logging import configure_logging, get_logger
from app.models import RepoSubmission


configure_logging()
logger = get_logger(__name__)


def evaluate_submission(submission: RepoSubmission) -> None:
    logger.info(
        "Evaluating submission",
        task=submission.task,
        repo=submission.repo_url,
    )


def main() -> None:
    with session_scope() as session:
        for submission in session.query(RepoSubmission).all():
            evaluate_submission(submission)


if __name__ == "__main__":
    main()

