from datetime import date, datetime, timezone

from pydantic import field_validator
from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel

MAX_TITLE_LENGTH = 200


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def clean_title(title: str) -> str:
    """Trim the title and check it is 1 to MAX_TITLE_LENGTH characters."""
    title = title.strip()
    if not 1 <= len(title) <= MAX_TITLE_LENGTH:
        raise ValueError(f"Title must be 1 to {MAX_TITLE_LENGTH} characters")
    return title


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


class TodoCreate(SQLModel):
    title: str
    due_date: date | None = None

    _trim_title = field_validator("title")(clean_title)


class TodoUpdate(SQLModel):
    """Only the fields that are sent change. `due_date: null` clears the date."""

    title: str | None = None
    done: bool | None = None
    due_date: date | None = None

    @field_validator("title")
    @classmethod
    def title_is_valid(cls, title: str | None) -> str:
        if title is None:
            raise ValueError("Title cannot be null")
        return clean_title(title)

    @field_validator("done")
    @classmethod
    def done_is_not_null(cls, done: bool | None) -> bool:
        if done is None:
            raise ValueError("Done cannot be null")
        return done


class TodoRead(SQLModel):
    id: int
    title: str
    done: bool
    position: int
    due_date: date | None
    created_at: datetime


class ReorderRequest(SQLModel):
    ids: list[int]


class ParseRequest(SQLModel):
    text: str
    today: date

    @field_validator("text")
    @classmethod
    def text_is_valid(cls, text: str) -> str:
        text = text.strip()
        if not 1 <= len(text) <= MAX_TITLE_LENGTH:
            raise ValueError(f"Text must be 1 to {MAX_TITLE_LENGTH} characters")
        return text


class ParseResult(SQLModel):
    title: str
    due_date: date | None
    matched: str | None


class DeletedCount(SQLModel):
    deleted: int
