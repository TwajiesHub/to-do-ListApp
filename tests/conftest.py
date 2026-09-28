import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel

from api.db import get_session, make_engine
from api.index import app


@pytest.fixture
def client(tmp_path):
    """A test client backed by a fresh temporary SQLite file, never todos.db or Neon."""
    engine = make_engine(f"sqlite:///{tmp_path / 'test.db'}")
    SQLModel.metadata.create_all(engine)

    def override_get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    yield TestClient(app)
    app.dependency_overrides.clear()
