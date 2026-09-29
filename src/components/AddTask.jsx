import { useState } from 'react'

const MAX_TITLE_LENGTH = 200

export default function AddTask({ onAdd }) {
  const [text, setText] = useState('')
  const title = text.trim()

  async function handleSubmit(event) {
    event.preventDefault()
    if (!title) return
    setText('')
    const saved = await onAdd(title)
    // Never lose what the user typed: put it back if the save failed and they haven't typed anything new.
    if (!saved) setText((current) => current || title)
  }

  return (
    <form className="add-task" onSubmit={handleSubmit}>
      <input
        className="add-task-input"
        type="text"
        aria-label="New task"
        placeholder="Add a task"
        maxLength={MAX_TITLE_LENGTH}
        value={text}
        onChange={(event) => setText(event.target.value)}
      />
      <button className="button-primary" type="submit" disabled={!title}>
        Add task
      </button>
    </form>
  )
}
