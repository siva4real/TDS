"""Shared utility helpers."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Iterable

import orjson
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings


SLUG_PATTERN = re.compile(r"[^a-z0-9-]+")


def slugify(value: str) -> str:
    slug = SLUG_PATTERN.sub("-", value.lower()).strip("-")
    return slug or "task"


def hash_secret(secret: str) -> str:
    return hashlib.sha256(secret.encode("utf-8")).hexdigest()


def ensure_workspace(task_id: str) -> Path:
    path = settings.work_dir / task_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def dumps_json(data: dict | Iterable) -> str:
    return orjson.dumps(data).decode("utf-8")


def retry_backoff(fn):  # type: ignore[valid-type]
    return retry(
        stop=stop_after_attempt(settings.evaluation_retry_attempts),
        wait=wait_exponential(multiplier=1, min=1, max=16),
    )(fn)

