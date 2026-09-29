import { useState } from 'react'

const MAX_TITLE_LENGTH = 200
const MAX_BODY_LENGTH = 5000

export default function AddNote({ onAdd }) {
  const [title, setTitle] = useState('')
  const [body, setBody] = useState('')
  const trimmedTitle = title.trim()

  async function handleSubmit(event) {
    event.preventDefault()
    if (!trimmedTitle) return
    const typed = { title, body }
    setTitle('')
    setBody('')
    const saved = await onAdd(trimmedTitle, body)
    // Never lose what the user typed: put it back if the save failed and they haven't typed anything new.
    if (!saved) {
      setTitle((current) => current || typed.title)
      setBody((current) => current || typed.body)
    }
  }

  function handleBodyKeyDown(event) {
    if (event.key === 'Enter' && (event.ctrlKey || event.metaKey)) handleSubmit(event)
  }

  return (
    <form className="add-note" onSubmit={handleSubmit}>
      <input
        className="text-field"
        type="text"
        aria-label="Note title"
        placeholder="Note title"
        maxLength={MAX_TITLE_LENGTH}
        value={title}
        onChange={(event) => setTitle(event.target.value)}
      />
      <textarea
        className="text-field note-body-field"
        aria-label="Note"
        placeholder="Write a note (optional)"
        rows={3}
        maxLength={MAX_BODY_LENGTH}
        value={body}
        onChange={(event) => setBody(event.target.value)}
        onKeyDown={handleBodyKeyDown}
      />
      <div className="add-note-actions">
        <button className="button-primary" type="submit" disabled={!trimmedTitle}>
          Add note
        </button>
      </div>
    </form>
  )
}
