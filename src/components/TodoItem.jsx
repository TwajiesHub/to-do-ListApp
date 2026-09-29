import { useRef, useState } from 'react'
import { useSortable } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { isPending } from '../hooks/useTodos.js'

export default function TodoItem({ todo, reorderLocked, onToggle, onDelete, onRename }) {
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState(todo.title)
  const pending = isPending(todo)

  const { attributes, listeners, setNodeRef, setActivatorNodeRef, transform, transition, isDragging } =
    useSortable({ id: todo.id, disabled: reorderLocked })

  // Enter and Esc both end the edit. Removing the input then triggers a blur, and
  // this flag stops that blur from saving after Esc has cancelled. It is a ref, not
  // state, so the blur handler sees the new value straight away.
  const finished = useRef(false)

  function startEditing() {
    if (pending) return
    setDraft(todo.title)
    finished.current = false
    setEditing(true)
  }

  function finishEditing(save) {
    if (finished.current) return
    finished.current = true
    setEditing(false)
    const title = draft.trim()
    if (save && title && title !== todo.title) onRename(todo, title)
  }

  function handleEditKeyDown(event) {
    if (event.key === 'Enter') {
      event.preventDefault()
      finishEditing(true)
    } else if (event.key === 'Escape') {
      event.preventDefault()
      finishEditing(false)
    }
  }

  function handleTitleKeyDown(event) {
    if (event.key === 'Enter') {
      event.preventDefault()
      startEditing()
    }
  }

  const style = { transform: CSS.Transform.toString(transform), transition }
  const className = [
    'todo-item',
    todo.done ? 'is-done' : '',
    pending ? 'is-pending' : '',
    isDragging ? 'is-dragging' : '',
  ].join(' ')

  return (
    <li className={className} ref={setNodeRef} style={style}>
      <button
        className="drag-handle"
        ref={setActivatorNodeRef}
        aria-label={`Reorder task: ${todo.title}`}
        aria-disabled={reorderLocked}
        {...attributes}
        {...listeners}
      >
        ⠿
      </button>

      <label className="check">
        <input
          className="check-input"
          type="checkbox"
          aria-label={todo.title}
          checked={todo.done}
          disabled={pending}
          onChange={() => onToggle(todo)}
        />
        <svg className="check-box" viewBox="0 0 24 24" aria-hidden="true">
          <rect className="check-outline" x="2" y="2" width="20" height="20" rx="5" />
          <path
            className="check-tick"
            pathLength="1"
            d="M5.5 13 C7 14.5 8.5 16 10 17.5 C12.5 12.5 15.5 8.5 20 4.5"
          />
        </svg>
      </label>

      {editing ? (
        <input
          className="edit-input"
          type="text"
          aria-label={`Edit task: ${todo.title}`}
          maxLength={200}
          autoFocus
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          onKeyDown={handleEditKeyDown}
          onBlur={() => finishEditing(true)}
        />
      ) : (
        <button
          className="todo-title"
          onDoubleClick={startEditing}
          onKeyDown={handleTitleKeyDown}
        >
          {todo.title}
        </button>
      )}

      <button
        className="delete-button"
        aria-label={`Delete task: ${todo.title}`}
        disabled={pending}
        onClick={() => onDelete(todo)}
      >
        ×
      </button>
    </li>
  )
}
