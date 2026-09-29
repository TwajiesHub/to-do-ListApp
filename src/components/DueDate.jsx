import { useState } from 'react'
import { formatDue } from '../dates.js'

// A due date year below this is a half-typed value like "0002-10-02", so don't save it yet.
const MIN_SAVED_YEAR = 1000

function badgeLabel(dueDate, overdue, dueToday) {
  if (overdue) return 'Overdue'
  if (dueToday) return 'Today'
  return formatDue(dueDate)
}

export default function DueDate({ todo, overdue, dueToday, disabled, onChange }) {
  const [editing, setEditing] = useState(false)

  function handleDateChange(event) {
    const { value, validity } = event.target
    if (value && validity.valid && Number(value.slice(0, 4)) >= MIN_SAVED_YEAR) {
      onChange(value)
    }
  }

  function handleKeyDown(event) {
    if (event.key === 'Escape' || event.key === 'Enter') {
      event.preventDefault()
      setEditing(false)
    }
  }

  function handleClear() {
    onChange(null)
    setEditing(false)
  }

  if (editing) {
    return (
      <div className="due-editor">
        <input
          className="due-input"
          type="date"
          aria-label={`Due date: ${todo.title}`}
          autoFocus
          // Uncontrolled on purpose: a controlled date input would reset half-typed dates.
          defaultValue={todo.due_date ?? ''}
          onChange={handleDateChange}
          onKeyDown={handleKeyDown}
          onBlur={() => setEditing(false)}
        />
        {todo.due_date && (
          <button
            className="button-text due-clear"
            aria-label={`Clear due date: ${todo.title}`}
            // Keep focus in the date input, so its blur doesn't close the editor before the click lands.
            onMouseDown={(event) => event.preventDefault()}
            onClick={handleClear}
          >
            Clear
          </button>
        )}
      </div>
    )
  }

  if (!todo.due_date) {
    return (
      <button
        className="add-date-button"
        aria-label={`Add due date: ${todo.title}`}
        disabled={disabled}
        onClick={() => setEditing(true)}
      >
        Add date
      </button>
    )
  }

  const kind = overdue ? 'is-overdue' : dueToday ? 'is-today' : ''
  return (
    <button
      className={`due-badge ${kind}`}
      aria-label={`Change due date: ${todo.title}, ${formatDue(todo.due_date)}`}
      disabled={disabled}
      onClick={() => setEditing(true)}
    >
      {badgeLabel(todo.due_date, overdue, dueToday)}
    </button>
  )
}
