import { useCallback, useEffect, useRef, useState } from 'react'
import * as api from '../api.js'

const CACHE_KEY = 'tick.todos.v1'
const SLOW_LOAD_MS = 1000
const SAVE_ERROR = "Couldn't save that change. Check your connection and try again."
const LOAD_ERROR = "Couldn't load your tasks. Check your connection and try again."

// New tasks get a negative id until the server replies with the real one.
let nextTempId = -1

export function isPending(todo) {
  return todo.id < 0
}

function readCache() {
  try {
    return JSON.parse(localStorage.getItem(CACHE_KEY)) ?? null
  } catch {
    return null
  }
}

function writeCache(todos) {
  try {
    localStorage.setItem(CACHE_KEY, JSON.stringify(todos.filter((t) => !isPending(t))))
  } catch {
    // Storage can be full or blocked. The cache is only a speed-up, so ignore it.
  }
}

function sortByPosition(todos) {
  return [...todos].sort((a, b) => a.position - b.position)
}

export function useTodos() {
  const cached = useRef(readCache())
  const [todos, setTodos] = useState(cached.current ?? [])
  const [loaded, setLoaded] = useState(cached.current !== null)
  const [waking, setWaking] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    const wakingTimer = setTimeout(() => setWaking(true), SLOW_LOAD_MS)
    api
      .getTodos()
      .then((serverTodos) => {
        setTodos(serverTodos)
        setLoaded(true)
      })
      .catch(() => setError(LOAD_ERROR))
      .finally(() => {
        clearTimeout(wakingTimer)
        setWaking(false)
      })
    return () => clearTimeout(wakingTimer)
  }, [])

  useEffect(() => {
    if (loaded) writeCache(todos)
  }, [todos, loaded])

  const patchLocal = useCallback((id, fields) => {
    setTodos((current) => current.map((t) => (t.id === id ? { ...t, ...fields } : t)))
  }, [])

  // Update the screen first, send the request, and undo the screen if it fails.
  const optimistic = useCallback(async (apply, send, undo) => {
    setError(null)
    apply()
    try {
      await send()
      return true
    } catch {
      undo()
      setError(SAVE_ERROR)
      return false
    }
  }, [])

  const add = useCallback(async (title) => {
    const tempId = nextTempId--
    setError(null)
    setTodos((current) => {
      const position = Math.max(-1, ...current.map((t) => t.position)) + 1
      const temp = { id: tempId, title, done: false, position, due_date: null, created_at: '' }
      return [...current, temp]
    })
    try {
      const saved = await api.createTodo({ title })
      setTodos((current) => current.map((t) => (t.id === tempId ? saved : t)))
      return true
    } catch {
      setTodos((current) => current.filter((t) => t.id !== tempId))
      setError(SAVE_ERROR)
      return false
    }
  }, [])

  const toggle = useCallback(
    (todo) =>
      optimistic(
        () => patchLocal(todo.id, { done: !todo.done }),
        () => api.updateTodo(todo.id, { done: !todo.done }),
        () => patchLocal(todo.id, { done: todo.done }),
      ),
    [optimistic, patchLocal],
  )

  const rename = useCallback(
    (todo, title) =>
      optimistic(
        () => patchLocal(todo.id, { title }),
        () => api.updateTodo(todo.id, { title }),
        () => patchLocal(todo.id, { title: todo.title }),
      ),
    [optimistic, patchLocal],
  )

  const remove = useCallback(
    (todo) =>
      optimistic(
        () => setTodos((current) => current.filter((t) => t.id !== todo.id)),
        () => api.deleteTodo(todo.id),
        () => setTodos((current) => sortByPosition([...current, todo])),
      ),
    [optimistic],
  )

  const clearCompleted = useCallback(() => {
    const removed = todos.filter((t) => t.done)
    return optimistic(
      () => setTodos((current) => current.filter((t) => !t.done)),
      () => api.clearCompletedTodos(),
      () => setTodos((current) => sortByPosition([...current, ...removed])),
    )
  }, [todos, optimistic])

  const reorder = useCallback(
    (orderedTodos) => {
      const before = todos
      return optimistic(
        () => setTodos(orderedTodos.map((t, index) => ({ ...t, position: index }))),
        () => api.reorderTodos(orderedTodos.map((t) => t.id)),
        () => setTodos(before),
      )
    },
    [todos, optimistic],
  )

  const dismissError = useCallback(() => setError(null), [])

  return {
    todos,
    loaded,
    waking,
    error,
    dismissError,
    add,
    toggle,
    rename,
    remove,
    clearCompleted,
    reorder,
  }
}
