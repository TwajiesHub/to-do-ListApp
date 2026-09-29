from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import Session, select

from api.db import get_session
from api.models import Note, NoteCreate, NoteRead, NoteUpdate, utc_now

router = APIRouter(prefix="/api")


def get_note_or_404(session: Session, note_id: int) -> Note:
    note = session.get(Note, note_id)
    if note is None:
        raise HTTPException(status_code=404, detail=f"Note {note_id} not found")
    return note


@router.get("/notes", response_model=list[NoteRead])
def list_notes(session: Session = Depends(get_session)) -> list[Note]:
    """Return every note, most recently edited first."""
    newest_first = select(Note).order_by(Note.updated_at.desc(), Note.id.desc())
    return list(session.exec(newest_first))


@router.post("/notes", response_model=NoteRead, status_code=status.HTTP_201_CREATED)
def create_note(data: NoteCreate, session: Session = Depends(get_session)) -> Note:
    now = utc_now()
    note = Note(title=data.title, body=data.body, created_at=now, updated_at=now)
    session.add(note)
    session.commit()
    session.refresh(note)
    return note


@router.patch("/notes/{note_id}", response_model=NoteRead)
def update_note(
    note_id: int, data: NoteUpdate, session: Session = Depends(get_session)
) -> Note:
    """Change only the fields that were sent, and mark the note as edited just now."""
    note = get_note_or_404(session, note_id)
    changes = data.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(note, field, value)
    if changes:
        note.updated_at = utc_now()
    session.commit()
    session.refresh(note)
    return note


@router.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int, session: Session = Depends(get_session)) -> Response:
    """Delete one note."""
    note = get_note_or_404(session, note_id)
    session.delete(note)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
