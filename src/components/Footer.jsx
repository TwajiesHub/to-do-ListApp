export default function Footer({ todos, onClearCompleted }) {
  const left = todos.filter((t) => !t.done).length
  const hasDone = todos.some((t) => t.done)

  return (
    <footer className="footer">
      <p className="counter">{left} left</p>
      {hasDone && (
        <button className="button-text" onClick={onClearCompleted}>
          Clear completed
        </button>
      )}
    </footer>
  )
}
