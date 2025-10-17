"""FastAPI application for handling build task requests.

This module exposes an endpoint that accepts build task definitions coming
from the client. The payload is validated using Pydantic models so later
processing (e.g. orchestrating an OpenAI powered build) can rely on a
well-defined structure.
"""

from __future__ import annotations

from typing import Optional

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request

from app import schemas
from app.build_pipeline import BuildPipeline
from app.config import settings
from app.database import init_db, session_scope
from app.logging import bind_request_context, configure_logging, get_logger
from app.models import RepoSubmission, TaskRecord
from app.utils import dumps_json, hash_secret


app = FastAPI(title="Task Build Orchestrator", version="0.1.0")
configure_logging()
logger = get_logger(__name__)
init_db()
pipeline = BuildPipeline()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = request.headers.get("x-request-id")
    bind_request_context(request_id=request_id, path=request.url.path)
    return await call_next(request)


def _verify_secret(secret: str) -> None:
    if settings.app_secret.get_secret_value() != secret:
        logger.warning("Secret mismatch")
        raise HTTPException(status_code=403, detail="Invalid secret")


def _persist_task(payload: schemas.BuildRequest) -> None:
    hash_ = hash_secret(payload.secret)
    with session_scope() as session:
        record = TaskRecord(
            email=payload.email,
            task=payload.task,
            round=payload.round,
            nonce=payload.nonce,
            brief=payload.brief,
            attachments_json=dumps_json([att.model_dump() for att in payload.attachments or []]),
            checks_json=dumps_json(payload.checks),
            evaluation_url=str(payload.evaluation_url),
            secret_hash=hash_,
        )
        session.add(record)


def _enqueue_build(background_tasks: BackgroundTasks, payload: schemas.BuildRequest) -> None:
    payload_dict = payload.model_dump()
    attachments = payload_dict.pop("attachments", [])
    background_tasks.add_task(pipeline.run, payload_dict, attachments)


@app.post("/build-task", response_model=schemas.BuildResponse)
async def receive_build_task(payload: schemas.BuildRequest, background_tasks: BackgroundTasks) -> schemas.BuildResponse:
    _verify_secret(payload.secret)
    _persist_task(payload)
    _enqueue_build(background_tasks, payload)

    logger.info("Build task accepted", task=payload.task, round=payload.round)
    return schemas.BuildResponse(status="accepted", task=payload.task, round=payload.round)


@app.get("/healthz")
async def health_check() -> dict:
    return {"status": "ok"}


@app.get("/tasks/{task_id}", response_model=Optional[schemas.BuildJobStatus])
async def get_task_status(task_id: str, round: Optional[int] = None) -> Optional[schemas.BuildJobStatus]:
    with session_scope() as session:
        query = session.query(RepoSubmission).filter(RepoSubmission.task == task_id)
        if round is not None:
            query = query.filter(RepoSubmission.round == round)
        submission = query.order_by(RepoSubmission.created_at.desc()).first()
        if submission is None:
            return None
        return schemas.BuildJobStatus(
            task=submission.task,
            round=submission.round,
            status="completed",
            repo_url=submission.repo_url,
            commit_sha=submission.commit_sha,
            pages_url=submission.pages_url,
        )

