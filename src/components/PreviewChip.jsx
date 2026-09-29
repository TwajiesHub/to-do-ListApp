import { formatDue } from '../dates.js'

export default function PreviewChip({ dueDate, matched, onRemove }) {
  return (
    <p className="preview-chip">
      <span>
        Due {formatDue(dueDate)}, from &quot;{matched}&quot;
      </span>
      <button
        type="button"
        className="preview-chip-remove"
        aria-label="Remove due date"
        onClick={onRemove}
      >
        ×
      </button>
    </p>
  )
}
