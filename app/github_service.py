"""GitHub integration utilities for repository management and Pages deployment."""

from __future__ import annotations

import base64
import time
from dataclasses import dataclass
from typing import Optional

import httpx
from git import Repo

from app.config import settings
from app.logging import get_logger


logger = get_logger(__name__)


@dataclass
class PublishedRepo:
    """Descriptor for published repository metadata."""

    repo_url: str
    commit_sha: str
    pages_url: str


class GitHubService:
    """High-level GitHub automation using PAT."""

    def __init__(self, token: str | None = None, api_base: str | None = None) -> None:
        self.token = token or settings.github_token.get_secret_value()
        self.api_base = api_base or settings.github_api_url.rstrip("/")
        self.owner = settings.github_owner
        self.session = httpx.Client(
            base_url=self.api_base,
            headers={
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github+json",
            },
            timeout=30,
        )

    def _repo_exists(self, name: str) -> bool:
        response = self.session.get(f"/repos/{self.owner}/{name}")
        return response.status_code == 200

    def ensure_repo(self, name: str, description: str) -> None:
        if self._repo_exists(name):
            logger.info("GitHub repo already exists", repo=name)
            return

        response = self.session.post(
            f"/user/repos",
            json={
                "name": name,
                "description": description,
                "private": False,
                "auto_init": False,
            },
        )
        response.raise_for_status()
        logger.info("Created GitHub repository", repo=name)

    def push_repository(self, repo_name: str, local_path: str, default_branch: str) -> str:
        remote_url = f"https://{self.token}:x-oauth-basic@github.com/{self.owner}/{repo_name}.git"
        repo = Repo(local_path)
        repo.git.add(all=True)
        if repo.is_dirty():
            repo.index.commit("Automated build commit")
        origin = repo.remote(name="origin") if "origin" in repo.remotes else repo.create_remote("origin", remote_url)
        origin.push(refspec=f"HEAD:{default_branch}", force=True)
        commit_sha = repo.head.object.hexsha
        logger.info("Pushed repository", repo=repo_name, commit=commit_sha)
        return commit_sha

    def add_license(self, repo_name: str) -> None:
        license_text = _mit_license_template()
        encoded = base64.b64encode(license_text.encode("utf-8")).decode("utf-8")
        response = self.session.put(
            f"/repos/{self.owner}/{repo_name}/contents/LICENSE",
            json={
                "message": "Add MIT License",
                "content": encoded,
                "branch": settings.default_branch,
            },
        )
        if response.status_code not in {200, 201}:
            logger.warning("Failed to add license", repo=repo_name, status=response.status_code, body=response.text)
        else:
            logger.info("MIT License ensured", repo=repo_name)

    def ensure_pages(self, repo_name: str) -> str:
        payload = {
            "source": {
                "branch": settings.github_pages_branch,
                "path": "/",
            }
        }
        response = self.session.post(f"/repos/{self.owner}/{repo_name}/pages", json=payload)
        if response.status_code not in {201, 204}:
            logger.warning("GitHub Pages enablement failed", repo=repo_name, status=response.status_code, body=response.text)

        pages_url = f"https://{self.owner}.github.io/{repo_name}/"
        for attempt in range(10):
            status_resp = self.session.get(f"/repos/{self.owner}/{repo_name}/pages")
            if status_resp.status_code == 200:
                logger.info("GitHub Pages available", repo=repo_name)
                return status_resp.json().get("html_url", pages_url)
            time.sleep(5)
            logger.info("Waiting for GitHub Pages publishing", attempt=attempt + 1)
        logger.warning("Falling back to expected Pages URL", repo=repo_name)
        return pages_url

    def publish(self, repo_name: str, local_path: str, description: str) -> PublishedRepo:
        self.ensure_repo(repo_name, description)
        commit_sha = self.push_repository(repo_name, local_path, settings.default_branch)
        self.add_license(repo_name)
        pages_url = self.ensure_pages(repo_name)
        repo_url = f"https://github.com/{self.owner}/{repo_name}"
        return PublishedRepo(repo_url=repo_url, commit_sha=commit_sha, pages_url=pages_url)


def _mit_license_template() -> str:
    return """MIT License

Copyright (c) {year} {owner}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
""".format(year=time.strftime("%Y"), owner=settings.github_owner)

