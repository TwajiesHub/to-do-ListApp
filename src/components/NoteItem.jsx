import { useEffect, useRef, useState } from 'react'
import { formatEdited } from '../dates.js'
import { isPending } from '../hooks/useNotes.js'

const MAX_TITLE_LENGTH = 200
const MAX_BODY_LENGTH = 5000

export default function NoteItem({ note, onEdit, onDelete }) {
  const [editing, setEditing] = useState(false)
  const [confirming, setConfirming] = useState(false)
  const [draftTitle, setDraftTitle] = useState(note.title)
  const [draftBody, setDraftBody] = useState(note.body)
  const pending = isPending(note)
  const trimmedTitle = draftTitle.trim()

  // Put focus back on the button that opened the form or the confirm step.
  const editButton = useRef(null)
  const deleteButton = useRef(null)
  const wasBusy = useRef(false)
  useEffect(() => {
    if (wasBusy.current && !editing && !confirming) {
      const target = wasBusy.current === 'editing' ? editButton : deleteButton
      target.current?.focus()
    }
    wasBusy.current = editing ? 'editing' : confirming ? 'confirming' : false
  }, [editing, confirming])

  function startEditing() {
    setDraftTitle(note.title)
    setDraftBody(note.body)
    setEditing(true)
  }

  function handleSave(event) {
    event.preventDefault()
    if (!trimmedTitle) return
    const changes = {}
    if (trimmedTitle !== note.title) changes.title = trimmedTitle
    if (draftBody !== note.body) changes.body = draftBody
    setEditing(false)
    if (Object.keys(changes).length > 0) onEdit(note, changes)
  }

  function handleFormKeyDown(event) {
    if (event.key === 'Escape') {
      event.preventDefault()
      setEditing(false)
    } else if (event.key === 'Enter' && (event.ctrlKey || event.metaKey)) {
      handleSave(event)
    }
  }

  function handleConfirmKeyDown(event) {
    if (event.key === 'Escape') {
      event.preventDefault()
      setConfirming(false)
    }
  }

  if (editing) {
    return (
      <li className="note-item">
        <form className="note-form" onSubmit={handleSave} onKeyDown={handleFormKeyDown}>
          <input
            className="text-field"
            type="text"
            aria-label={`Note title: ${note.title}`}
            maxLength={MAX_TITLE_LENGTH}
            autoFocus
            value={draftTitle}
            onChange={(event) => setDraftTitle(event.target.value)}
          />
          <textarea
            className="text-field note-body-field"
            aria-label={`Note text: ${note.title}`}
            rows={4}
            maxLength={MAX_BODY_LENGTH}
            value={draftBody}
            onChange={(event) => setDraftBody(event.target.value)}
          />
          <div className="note-actions">
            <button className="button-primary" type="submit" disabled={!trimmedTitle}>
              Save
            </button>
            <button className="button-text" type="button" onClick={() => setEditing(false)}>
              Cancel
            </button>
          </div>
        </form>
      </li>
    )
  }

  return (
    <li className={`note-item ${pending ? 'is-pending' : ''}`}>
      <h2 className="note-title">{note.title}</h2>
      {note.body && <p className="note-body">{note.body}</p>}
      <p className="note-edited">Edited {formatEdited(note.updated_at)}</p>
      <div className="note-actions" onKeyDown={handleConfirmKeyDown}>
        {confirming ? (
          <>
            <button
              className="button-text note-confirm"
              aria-label={`Confirm delete: ${note.title}`}
              autoFocus
              onClick={() => onDelete(note)}
            >
              Confirm delete
            </button>
            <button className="button-text" onClick={() => setConfirming(false)}>
              Cancel
            </button>
          </>
        ) : (
          <>
            <button
              ref={editButton}
              className="button-text"
              aria-label={`Edit note: ${note.title}`}
              disabled={pending}
              onClick={startEditing}
            >
              Edit
            </button>
            <button
              ref={deleteButton}
              className="button-text"
              aria-label={`Delete note: ${note.title}`}
              disabled={pending}
              onClick={() => setConfirming(true)}
            >
              Delete
            </button>
          </>
        )}
      </div>
    </li>
  )
}
