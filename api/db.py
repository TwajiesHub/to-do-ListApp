import os
from collections.abc import Iterator

from sqlmodel import Session, create_engine

DEFAULT_DATABASE_URL = "sqlite:///./todos.db"


def normalize_database_url(url: str) -> str:
    """Point plain Postgres URLs (as Neon and Vercel supply them) at the psycopg 3 driver."""
    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix):]
    return url


def make_engine(url: str):
    """Build an engine for the given URL. SQLite needs a flag to allow FastAPI's threads."""
    url = normalize_database_url(url)
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, pool_pre_ping=True, connect_args=connect_args)


engine = make_engine(os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL))


def get_session() -> Iterator[Session]:
    """FastAPI dependency. Tests override this to use a temporary database."""
    with Session(engine) as session:
        yield session
