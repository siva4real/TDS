"""Helpers for decoding and storing build attachments."""

from __future__ import annotations

import base64
import mimetypes
import os
from pathlib import Path
from typing import Iterable

from app.logging import get_logger


logger = get_logger(__name__)


def materialize_attachments(base_dir: Path, attachments: Iterable[dict]) -> list[Path]:
    """Write data-URI attachments to disk and return file paths."""

    written_files: list[Path] = []
    for attachment in attachments:
        name = attachment["name"]
        uri = attachment["url"]
        if not uri.startswith("data:"):
            logger.warning("Skipping non data URI attachment", name=name)
            continue

        header, encoded = uri.split(",", 1)
        encoding = "base64" if ";base64" in header else "utf-8"
        if encoding != "base64":
            logger.warning("Unsupported encoding, skipping attachment", name=name)
            continue

        data = base64.b64decode(encoded)
        file_path = base_dir / name
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(data)
        written_files.append(file_path)

        if mimetype := mimetypes.guess_type(name)[0]:
            logger.info("Attachment stored", name=name, mimetype=mimetype)
        else:
            logger.info("Attachment stored", name=name, mimetype="unknown")

    return written_files

