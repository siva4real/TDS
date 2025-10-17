"""SQLModel ORM models for task, repo, and results tracking."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class TaskRecord(SQLModel, table=True):
    """Persistent record of task requests received by the platform."""

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    email: str = Field(index=True)
    task: str = Field(index=True)
    round: int
    nonce: str
    brief: str
    attachments_json: str | None = None
    checks_json: str | None = None
    evaluation_url: str
    endpoint: str | None = None
    status_code: int | None = None
    secret_hash: str


class RepoSubmission(SQLModel, table=True):
    """Stores submissions posted back to the evaluation URL."""

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    email: str = Field(index=True)
    task: str = Field(index=True)
    round: int
    nonce: str
    repo_url: str
    commit_sha: str
    pages_url: str


class EvaluationResult(SQLModel, table=True):
    """Tracks evaluation results produced by instructor workflows."""

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    email: str = Field(index=True)
    task: str = Field(index=True)
    round: int
    repo_url: str
    commit_sha: str
    pages_url: str
    check: str
    score: float
    reason: str | None = None
    logs: str | None = None

