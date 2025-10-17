"""Pydantic schemas for inbound/outbound API payloads."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class Attachment(BaseModel):
    """Represents a single attachment provided with the build request."""

    name: str = Field(..., description="Filename of the attachment")
    url: HttpUrl = Field(
        ..., description="Data URI or remote URL containing attachment contents"
    )


class BuildRequest(BaseModel):
    """Schema for the incoming build request payload."""

    email: str = Field(..., description="Student email ID")
    secret: str = Field(..., description="Student-provided secret")
    task: str = Field(..., description="Unique task identifier")
    round: int = Field(..., ge=0, description="Round index for the task")
    nonce: str = Field(..., description="Nonce to return to evaluation endpoint")
    brief: str = Field(..., description="Short description of what to build")
    checks: List[str] = Field(
        default_factory=list,
        description="List of checks describing how the build is evaluated",
    )
    evaluation_url: HttpUrl = Field(
        ..., description="Endpoint to notify with repo & commit details"
    )
    attachments: Optional[List[Attachment]] = Field(
        default=None,
        description="Optional attachments encoded as data URIs",
    )


class BuildResponse(BaseModel):
    """Response returned once the build request is accepted."""

    status: str = Field(..., description="Outcome of request acceptance")
    task: str = Field(..., description="Task identifier that was received")
    round: int = Field(..., description="Round index that was received")


class BuildJobStatus(BaseModel):
    """Represents build job progress for clients polling status endpoints."""

    task: str
    round: int
    status: str
    repo_url: Optional[str] = None
    commit_sha: Optional[str] = None
    pages_url: Optional[str] = None
    error: Optional[str] = None

