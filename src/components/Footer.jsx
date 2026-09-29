import { isOverdue } from '../dates.js'

export default function Footer({ todos, today, onClearCompleted }) {
  const left = todos.filter((t) => !t.done).length
  const overdue = todos.filter((t) => isOverdue(t, today)).length
  const hasDone = todos.some((t) => t.done)

  return (
    <footer className="footer">
      <p className="counter">
        {left} left
        {overdue > 0 && (
          <>
            , <span className="overdue-count">{overdue} overdue</span>
          </>
        )}
      </p>
      {hasDone && (
        <button className="button-text" onClick={onClearCompleted}>
          Clear completed
        </button>
      )}
    </footer>
  )
}
