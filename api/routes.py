from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import func
from sqlmodel import Session, select

from api.db import get_session
from api.models import (
    DeletedCount,
    ReorderRequest,
    Todo,
    TodoCreate,
    TodoRead,
    TodoUpdate,
)

router = APIRouter(prefix="/api")


def ordered_todos(session: Session) -> list[Todo]:
    return list(session.exec(select(Todo).order_by(Todo.position)))


def get_todo_or_404(session: Session, todo_id: int) -> Todo:
    todo = session.get(Todo, todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail=f"Todo {todo_id} not found")
    return todo


@router.get("/todos", response_model=list[TodoRead])
def list_todos(session: Session = Depends(get_session)) -> list[Todo]:
    """Return every todo, in list order."""
    return ordered_todos(session)


@router.post("/todos", response_model=TodoRead, status_code=status.HTTP_201_CREATED)
def create_todo(data: TodoCreate, session: Session = Depends(get_session)) -> Todo:
    """Add a todo at the end of the list."""
    highest = session.exec(select(func.max(Todo.position))).one()
    position = 0 if highest is None else highest + 1
    todo = Todo(title=data.title, due_date=data.due_date, position=position)
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo


# Declared before /todos/{todo_id}, or "completed" would be read as an id.
@router.delete("/todos/completed", response_model=DeletedCount)
def clear_completed(session: Session = Depends(get_session)) -> DeletedCount:
    """Delete every todo that is done."""
    done_todos = session.exec(select(Todo).where(Todo.done)).all()
    for todo in done_todos:
        session.delete(todo)
    session.commit()
    return DeletedCount(deleted=len(done_todos))


# Declared before /todos/{todo_id} for the same reason.
@router.put("/todos/order", response_model=list[TodoRead])
def reorder_todos(
    data: ReorderRequest, session: Session = Depends(get_session)
) -> list[Todo]:
    """Rewrite every position to match the given order of ids."""
    todos = {todo.id: todo for todo in ordered_todos(session)}
    if sorted(data.ids) != sorted(todos):
        raise HTTPException(
            status_code=422,
            detail="ids must contain every current todo id exactly once",
        )
    for position, todo_id in enumerate(data.ids):
        todos[todo_id].position = position
    session.commit()
    return ordered_todos(session)


@router.patch("/todos/{todo_id}", response_model=TodoRead)
def update_todo(
    todo_id: int, data: TodoUpdate, session: Session = Depends(get_session)
) -> Todo:
    """Change only the fields that were sent."""
    todo = get_todo_or_404(session, todo_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(todo, field, value)
    session.commit()
    session.refresh(todo)
    return todo


@router.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int, session: Session = Depends(get_session)) -> Response:
    """Delete one todo."""
    todo = get_todo_or_404(session, todo_id)
    session.delete(todo)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
