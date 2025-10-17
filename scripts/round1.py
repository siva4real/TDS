"""Instructor workflow to dispatch round 1 tasks."""

from __future__ import annotations

import csv
from pathlib import Path

import httpx

from app.config import settings
from app.database import session_scope
from app.logging import configure_logging, get_logger
from app.models import TaskRecord
from app.utils import dumps_json, hash_secret


configure_logging()
logger = get_logger(__name__)


def send_task(row: dict) -> None:
    # Placeholder payload creation
    payload = {
        "email": row["email"],
        "secret": row["secret"],
        "task": "template-12345",
        "round": 1,
        "nonce": "nonce-placeholder",
        "brief": "Placeholder brief",
        "checks": ["Repo has MIT license"],
        "evaluation_url": settings.github_api_url,
        "attachments": [],
    }

    response = httpx.post(row["endpoint"], json=payload, timeout=30)
    logger.info("Dispatched task", email=row["email"], status=response.status_code)
    with session_scope() as session:
        record = TaskRecord(
            email=row["email"],
            task=payload["task"],
            round=payload["round"],
            nonce=payload["nonce"],
            brief=payload["brief"],
            attachments_json=dumps_json(payload["attachments"]),
            checks_json=dumps_json(payload["checks"]),
            evaluation_url=payload["evaluation_url"],
            endpoint=row["endpoint"],
            status_code=response.status_code,
            secret_hash=hash_secret(row["secret"]),
        )
        session.add(record)


def main(submissions_csv: Path) -> None:
    with submissions_csv.open() as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            send_task(row)


if __name__ == "__main__":
    import typer

    typer.run(main)

