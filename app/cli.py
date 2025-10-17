"""CLI entrypoints for operational workflows."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from app.build_pipeline import BuildPipeline
from app.config import settings
from app.database import init_db
from app.logging import configure_logging, get_logger
from app.schemas import BuildRequest


configure_logging()
app = typer.Typer(help="Operational commands for the LLM build platform")
logger = get_logger(__name__)


@app.command()
def init_database() -> None:
    """Create database tables."""

    init_db()
    typer.echo("Database initialized")


@app.command()
def run_build(payload_path: Path) -> None:
    """Trigger a build using a JSON payload file."""

    payload_data = json.loads(payload_path.read_text("utf-8"))
    request = BuildRequest.model_validate(payload_data)
    pipeline = BuildPipeline()
    result = pipeline.run(request.model_dump(), [att.model_dump() for att in request.attachments or []])
    typer.echo(json.dumps(result, indent=2))


def main() -> None:
    app()


if __name__ == "__main__":
    main()

