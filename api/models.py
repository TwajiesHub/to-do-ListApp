from datetime import date, datetime, timezone
from typing import Annotated

from pydantic import AfterValidator, field_validator
from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel

MAX_TITLE_LENGTH = 200
MAX_BODY_LENGTH = 5000


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def as_utc(value: datetime) -> datetime:
    """SQLite drops the timezone, so a datetime with none came from UTC. Output always ends in Z."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


UtcDateTime = Annotated[datetime, AfterValidator(as_utc)]


def clean_title(title: str) -> str:
    """Trim the title and check it is 1 to MAX_TITLE_LENGTH characters."""
    title = title.strip()
    if not 1 <= len(title) <= MAX_TITLE_LENGTH:
        raise ValueError(f"Title must be 1 to {MAX_TITLE_LENGTH} characters")
    return title


def clean_body(body: str) -> str:
    """Use plain line breaks and check the body is at most MAX_BODY_LENGTH characters."""
    body = body.replace("\r\n", "\n").replace("\r", "\n")
    if len(body) > MAX_BODY_LENGTH:
        raise ValueError(f"Body must be at most {MAX_BODY_LENGTH} characters")
    return body


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
    created_at: UtcDateTime


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


class Note(SQLModel, table=True):
    __tablename__ = "notes"

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=MAX_TITLE_LENGTH)
    body: str = Field(default="", max_length=MAX_BODY_LENGTH)
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


class NoteCreate(SQLModel):
    title: str
    body: str = ""

    _trim_title = field_validator("title")(clean_title)
    _clean_body = field_validator("body")(clean_body)


class NoteUpdate(SQLModel):
    """Only the fields that are sent change. To clear the body, send an empty string."""

    title: str | None = None
    body: str | None = None

    @field_validator("title")
    @classmethod
    def title_is_valid(cls, title: str | None) -> str:
        if title is None:
            raise ValueError("Title cannot be null")
        return clean_title(title)

    @field_validator("body")
    @classmethod
    def body_is_valid(cls, body: str | None) -> str:
        if body is None:
            raise ValueError("Body cannot be null")
        return clean_body(body)


class NoteRead(SQLModel):
    id: int
    title: str
    body: str
    created_at: UtcDateTime
    updated_at: UtcDateTime
