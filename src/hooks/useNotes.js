import { useCallback, useEffect, useRef, useState } from 'react'
import * as api from '../api.js'

const CACHE_KEY = 'tick.notes.v1'
const SLOW_LOAD_MS = 1000
const SAVE_ERROR = "Couldn't save that change. Check your connection and try again."
const LOAD_ERROR = "Couldn't load your notes. Check your connection and try again."

// New notes get a negative id until the server replies with the real one.
let nextTempId = -1

export function isPending(note) {
  return note.id < 0
}

function readCache() {
  try {
    return JSON.parse(localStorage.getItem(CACHE_KEY)) ?? null
  } catch {
    return null
  }
}

function writeCache(notes) {
  try {
    localStorage.setItem(CACHE_KEY, JSON.stringify(notes.filter((n) => !isPending(n))))
  } catch {
    // Storage can be full or blocked. The cache is only a speed-up, so ignore it.
  }
}

// Most recently edited first, like the server. Newer ids win a tie.
function newestFirst(notes) {
  return [...notes].sort((a, b) => Date.parse(b.updated_at) - Date.parse(a.updated_at) || b.id - a.id)
}

export function useNotes() {
  const cached = useRef(readCache())
  const [notes, setNotes] = useState(() => newestFirst(cached.current ?? []))
  const [loaded, setLoaded] = useState(cached.current !== null)
  const [waking, setWaking] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    const wakingTimer = setTimeout(() => setWaking(true), SLOW_LOAD_MS)
    api
      .getNotes()
      .then((serverNotes) => {
        setNotes(newestFirst(serverNotes))
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
    if (loaded) writeCache(notes)
  }, [notes, loaded])

  const replaceNote = useCallback((id, replacement) => {
    setNotes((current) => newestFirst(current.map((n) => (n.id === id ? replacement : n))))
  }, [])

  const add = useCallback(async (title, body) => {
    const tempId = nextTempId--
    const now = new Date().toISOString()
    setError(null)
    setNotes((current) =>
      newestFirst([{ id: tempId, title, body, created_at: now, updated_at: now }, ...current]),
    )
    try {
      const saved = await api.createNote({ title, body })
      replaceNote(tempId, saved)
      return true
    } catch {
      setNotes((current) => current.filter((n) => n.id !== tempId))
      setError(SAVE_ERROR)
      return false
    }
  }, [replaceNote])

  // `changes` holds only the fields that changed. The edited note jumps to the top at once,
  // and the server's own edit time replaces our guess when it replies.
  const edit = useCallback(
    async (note, changes) => {
      setError(null)
      replaceNote(note.id, { ...note, ...changes, updated_at: new Date().toISOString() })
      try {
        replaceNote(note.id, await api.updateNote(note.id, changes))
        return true
      } catch {
        replaceNote(note.id, note)
        setError(SAVE_ERROR)
        return false
      }
    },
    [replaceNote],
  )

  const remove = useCallback(async (note) => {
    setError(null)
    setNotes((current) => current.filter((n) => n.id !== note.id))
    try {
      await api.deleteNote(note.id)
      return true
    } catch {
      setNotes((current) => newestFirst([...current, note]))
      setError(SAVE_ERROR)
      return false
    }
  }, [])

  const dismissError = useCallback(() => setError(null), [])

  return { notes, loaded, waking, error, dismissError, add, edit, remove }
}
