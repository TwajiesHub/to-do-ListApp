from datetime import date, datetime, timezone

from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel

MAX_TITLE_LENGTH = 200


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Todo(SQLModel, table=True):
    __tablename__ = "todos"

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=MAX_TITLE_LENGTH)
    done: bool = Field(default=False)
    position: int
    due_date: date | None = Field(default=None)
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


class TodoRead(SQLModel):
    id: int
    title: str
    done: bool
    position: int
    due_date: date | None
    created_at: datetime
