import AddTask from './components/AddTask.jsx'
import Footer from './components/Footer.jsx'
import Header from './components/Header.jsx'
import TodoList from './components/TodoList.jsx'
import { useTodos } from './hooks/useTodos.js'
import { useToday } from './hooks/useToday.js'

export default function App() {
  const {
    todos,
    loaded,
    waking,
    error,
    dismissError,
    add,
    toggle,
    rename,
    setDueDate,
    remove,
    clearCompleted,
    reorder,
  } = useTodos()
  const today = useToday()

  return (
    <main className="page">
      <Header />
      <AddTask onAdd={add} />

      {error && (
        <p className="error-message" role="alert">
          {error}{' '}
          <button className="button-text" onClick={dismissError}>
            Dismiss
          </button>
        </p>
      )}

      {!loaded && waking && <p className="status-message">Waking up the server…</p>}
      {loaded && todos.length === 0 && (
        <p className="status-message">Nothing to do yet. Add your first task above.</p>
      )}

      <TodoList
        todos={todos}
        today={today}
        onToggle={toggle}
        onDelete={remove}
        onRename={rename}
        onSetDueDate={setDueDate}
        onReorder={reorder}
      />

      {loaded && todos.length > 0 && <Footer todos={todos} today={today} onClearCompleted={clearCompleted} />}
    </main>
  )
}
