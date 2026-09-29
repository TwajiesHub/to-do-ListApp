import { useEffect, useState } from 'react'
import { useSmartParse } from '../hooks/useSmartParse.js'
import PreviewChip from './PreviewChip.jsx'

const MAX_TITLE_LENGTH = 200
const SMART_PLACEHOLDER = 'Add a task, like "mark SS2 scripts by Friday"'
const PLAIN_PLACEHOLDER = 'Add a task'

// Where the current due date came from. Only the chip changes the title.
const FROM_NOWHERE = 'none'
const FROM_SMART = 'smart' // detected in the text, shown as a chip
const FROM_PICKER = 'picker' // chosen by hand, so the text is saved exactly as typed
const CHIP_DISMISSED = 'dismissed' // the chip was removed, so the text is saved as typed

export default function AddTask({ onAdd, today, smartDates }) {
  const [text, setText] = useState('')
  // The one place for the due date. The picker and Smart dates both set it.
  const [dueDate, setDueDate] = useState('')
  const [dateSource, setDateSource] = useState(FROM_NOWHERE)
  const [submitting, setSubmitting] = useState(false)
  const { preview, parseNow } = useSmartParse(text, today, smartDates)
  const title = text.trim()
  const canDetect = smartDates && (dateSource === FROM_NOWHERE || dateSource === FROM_SMART)

  // Follow the latest answer from the server, unless the user has taken over the date.
  // Only a new answer or the switch should move the date, not the source changing.
  useEffect(() => {
    if (dateSource === FROM_PICKER || dateSource === CHIP_DISMISSED) return
    if (smartDates && preview?.due_date) {
      setDueDate(preview.due_date)
      setDateSource(FROM_SMART)
    } else if (dateSource === FROM_SMART) {
      setDueDate('')
      setDateSource(FROM_NOWHERE)
    }
  }, [preview, smartDates])

  function handleTextChange(event) {
    const next = event.target.value
    setText(next)
    if (!next.trim() && (dateSource === FROM_SMART || dateSource === CHIP_DISMISSED)) {
      setDateSource(FROM_NOWHERE)
    }
  }

  function handlePickDate(event) {
    setDueDate(event.target.value)
    setDateSource(FROM_PICKER)
  }

  function handleRemoveChip() {
    setDueDate('')
    setDateSource(CHIP_DISMISSED)
  }

  // The title and date to save. The chip decides both, or the text and picker stand as typed.
  async function chooseWhatToSave() {
    if (!canDetect) return { saveTitle: title, saveDate: dueDate || null }
    const answer = preview?.text === title ? preview : await parseNow()
    if (answer?.due_date) return { saveTitle: answer.title, saveDate: answer.due_date }
    return { saveTitle: title, saveDate: null }
  }

  async function handleSubmit(event) {
    event.preventDefault()
    if (!title || submitting) return
    const typed = { dueDate, dateSource }
    setSubmitting(true)
    const { saveTitle, saveDate } = await chooseWhatToSave()
    setText('')
    setDueDate('')
    setDateSource(FROM_NOWHERE)
    setSubmitting(false)
    const saved = await onAdd(saveTitle, saveDate)
    // Never lose what the user typed: put it back if the save failed and they haven't typed anything new.
    if (!saved) {
      setText((current) => current || title)
      setDueDate((current) => current || typed.dueDate)
      setDateSource((current) => (current === FROM_NOWHERE ? typed.dateSource : current))
    }
  }

  const showChip = dateSource === FROM_SMART && preview?.due_date

  return (
    <form className="add-task" onSubmit={handleSubmit}>
      <div className="add-task-row">
        <input
          className="add-task-input"
          type="text"
          aria-label="New task"
          placeholder={smartDates ? SMART_PLACEHOLDER : PLAIN_PLACEHOLDER}
          maxLength={MAX_TITLE_LENGTH}
          value={text}
          onChange={handleTextChange}
        />
        <input
          className="add-task-date"
          type="date"
          aria-label="Due date"
          value={dueDate}
          onChange={handlePickDate}
        />
        <button className="button-primary" type="submit" disabled={!title || submitting}>
          Add task
        </button>
      </div>
      {/* Takes no space while empty. */}
      <div className="add-task-preview" aria-live="polite">
        {showChip && (
          <PreviewChip
            dueDate={preview.due_date}
            matched={preview.matched}
            onRemove={handleRemoveChip}
          />
        )}
      </div>
    </form>
  )
}
