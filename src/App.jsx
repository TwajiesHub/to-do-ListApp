import { useEffect, useState } from 'react'
import { getTodos } from './api.js'

export default function App() {
  const [todos, setTodos] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    getTodos().then(setTodos).catch((err) => setError(err.message))
  }, [])

  return (
    <main className="page">
      <h1>Tick</h1>
      {error && <p role="alert">{error}</p>}
      {!error && todos === null && <p>Loading…</p>}
      {todos && <p>{todos.length} tasks from the server</p>}
    </main>
  )
}
