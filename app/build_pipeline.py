"""High-level orchestration for building, publishing, and notifying tasks."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

import httpx

from app.attachments import materialize_attachments
from app.config import settings
from app.github_service import GitHubService
from app.database import session_scope
from app.logging import get_logger
from app.llm_builder import LLMBuilder
from app.models import RepoSubmission
from app.security import run_security_checks
from app.utils import ensure_workspace, retry_backoff, slugify


logger = get_logger(__name__)


class BuildPipeline:
    def __init__(self) -> None:
        self.llm = LLMBuilder()
        self.github = GitHubService()

    def run(self, payload: Dict, attachments: List[Dict]) -> Dict:
        task_slug = slugify(payload["task"])
        workspace = ensure_workspace(task_slug)
        materialize_attachments(workspace, attachments)

        project_spec = self.llm.generate_project(payload, attachments)
        self._write_files(workspace, project_spec)
        self._ensure_readme(workspace, payload)
        run_security_checks(workspace)

        published = self.github.publish(
            repo_name=task_slug,
            local_path=str(workspace),
            description=payload["brief"],
        )

        notification_payload = {
            "email": payload["email"],
            "task": payload["task"],
            "round": payload["round"],
            "nonce": payload["nonce"],
            "repo_url": published.repo_url,
            "commit_sha": published.commit_sha,
            "pages_url": published.pages_url,
        }
        self._notify_evaluation(payload["evaluation_url"], notification_payload)
        self._record_submission(notification_payload)

        return notification_payload

    def _write_files(self, workspace: Path, project_spec: Dict) -> None:
        files = project_spec.get("files", [])
        for file_info in files:
            path = workspace / file_info["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(file_info["content"], encoding="utf-8")
            logger.info("Generated file", path=str(path.relative_to(workspace)))

    @retry_backoff
    def _notify_evaluation(self, url: str, payload: Dict) -> None:
        logger.info("Posting build results to evaluation endpoint", url=url)
        response = httpx.post(url, json=payload, timeout=settings.evaluation_timeout_seconds)
        response.raise_for_status()

    def _ensure_readme(self, workspace: Path, payload: Dict) -> None:
        readme = workspace / "README.md"
        if not readme.exists():
            readme.write_text(
                f"# {payload['task']}\n\n{payload['brief']}\n\n## Deployment\n\n"
                f"Published via automated pipeline for round {payload['round']}.\n",
                encoding="utf-8",
            )

    def _record_submission(self, payload: Dict) -> None:
        with session_scope() as session:
            submission = RepoSubmission(
                email=payload["email"],
                task=payload["task"],
                round=payload["round"],
                nonce=payload["nonce"],
                repo_url=payload["repo_url"],
                commit_sha=payload["commit_sha"],
                pages_url=payload["pages_url"],
            )
            session.add(submission)

