import { useEffect, useState } from 'react'
import Header from './components/Header.jsx'
import NotesView from './components/NotesView.jsx'
import TasksView from './components/TasksView.jsx'
import Tabs, { panelId, tabId } from './components/Tabs.jsx'
import { useHashTab } from './hooks/useHashTab.js'
import { useSmartDatesSetting } from './hooks/useSmartDatesSetting.js'

export default function App() {
  const tab = useHashTab()
  const [smartDates, toggleSmartDates] = useSmartDatesSetting()

  // Notes load the first time the tab is opened. After that the tab stays mounted
  // (just hidden), so switching back is instant and nothing is lost.
  const [notesOpened, setNotesOpened] = useState(tab === 'notes')
  useEffect(() => {
    if (tab === 'notes') setNotesOpened(true)
  }, [tab])

  return (
    <main className="page">
      <Header showSmartDates={tab === 'tasks'} smartDates={smartDates} onToggleSmartDates={toggleSmartDates} />
      <Tabs current={tab} />

      <section id={panelId('tasks')} role="tabpanel" aria-labelledby={tabId('tasks')} hidden={tab !== 'tasks'}>
        <TasksView smartDates={smartDates} />
      </section>

      {notesOpened && (
        <section id={panelId('notes')} role="tabpanel" aria-labelledby={tabId('notes')} hidden={tab !== 'notes'}>
          <NotesView />
        </section>
      )}
    </main>
  )
}
