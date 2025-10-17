"""Database utilities for SQLModel."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlmodel import Session, SQLModel, create_engine

from app.config import settings


engine = create_engine(settings.database_url, echo=False, connect_args={"check_same_thread": False})


def init_db() -> None:
    """Create all database tables."""

    SQLModel.metadata.create_all(engine)


@contextmanager
def session_scope() -> Iterator[Session]:
    """Provide a transactional scope around a series of operations."""

    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:  # noqa: BLE001
        session.rollback()
        raise
    finally:
        session.close()

