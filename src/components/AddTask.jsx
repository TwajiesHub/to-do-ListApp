import { useState } from 'react'

const MAX_TITLE_LENGTH = 200

export default function AddTask({ onAdd }) {
  const [text, setText] = useState('')
  // One place for the due date, so Smart dates (M3) can set it the same way the picker does.
  const [dueDate, setDueDate] = useState('')
  const title = text.trim()

  async function handleSubmit(event) {
    event.preventDefault()
    if (!title) return
    const typedDate = dueDate
    setText('')
    setDueDate('')
    const saved = await onAdd(title, typedDate || null)
    // Never lose what the user typed: put it back if the save failed and they haven't typed anything new.
    if (!saved) {
      setText((current) => current || title)
      setDueDate((current) => current || typedDate)
    }
  }

  return (
    <form className="add-task" onSubmit={handleSubmit}>
      <div className="add-task-row">
        <input
          className="add-task-input"
          type="text"
          aria-label="New task"
          placeholder="Add a task"
          maxLength={MAX_TITLE_LENGTH}
          value={text}
          onChange={(event) => setText(event.target.value)}
        />
        <input
          className="add-task-date"
          type="date"
          aria-label="Due date"
          value={dueDate}
          onChange={(event) => setDueDate(event.target.value)}
        />
        <button className="button-primary" type="submit" disabled={!title}>
          Add task
        </button>
      </div>
      {/* Reserved for the Smart dates preview chip (M3), so it can appear without moving the list. */}
      <div className="add-task-preview" aria-live="polite" />
    </form>
  )
}
