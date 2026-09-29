import { useNotes } from '../hooks/useNotes.js'
import AddNote from './AddNote.jsx'
import NoteItem from './NoteItem.jsx'

export default function NotesView() {
  const { notes, loaded, waking, error, dismissError, add, edit, remove } = useNotes()

  return (
    <>
      <AddNote onAdd={add} />

      {error && (
        <p className="error-message" role="alert">
          {error}{' '}
          <button className="button-text" onClick={dismissError}>
            Dismiss
          </button>
        </p>
      )}

      {!loaded && waking && <p className="status-message">Waking up the server…</p>}
      {loaded && notes.length === 0 && (
        <p className="status-message">No notes yet. Add your first note above.</p>
      )}

      <ul className="note-list">
        {notes.map((note) => (
          <NoteItem key={note.id} note={note} onEdit={edit} onDelete={remove} />
        ))}
      </ul>
    </>
  )
}
