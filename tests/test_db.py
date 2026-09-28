import pytest

from api.db import normalize_database_url


@pytest.mark.parametrize(
    "url, expected",
    [
        ("postgres://u:p@host/db", "postgresql+psycopg://u:p@host/db"),
        ("postgresql://u:p@host/db", "postgresql+psycopg://u:p@host/db"),
        ("postgresql+psycopg://u:p@host/db", "postgresql+psycopg://u:p@host/db"),
        ("sqlite:///./todos.db", "sqlite:///./todos.db"),
    ],
)
def test_normalize_database_url_selects_psycopg_driver(url, expected):
    assert normalize_database_url(url) == expected
