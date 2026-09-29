import { TABS, tabHash } from '../hooks/useHashTab.js'

const LABELS = { tasks: 'Tasks', notes: 'Notes' }

export function tabId(tab) {
  return `tab-${tab}`
}

export function panelId(tab) {
  return `panel-${tab}`
}

// Links to the URL hash, so the back button works. Arrow keys move between tabs.
export default function Tabs({ current }) {
  function handleKeyDown(event) {
    const index = TABS.indexOf(current)
    const moves = {
      ArrowRight: (index + 1) % TABS.length,
      ArrowLeft: (index - 1 + TABS.length) % TABS.length,
      Home: 0,
      End: TABS.length - 1,
    }
    if (!(event.key in moves)) return
    event.preventDefault()
    const next = TABS[moves[event.key]]
    window.location.hash = tabHash(next)
    document.getElementById(tabId(next))?.focus()
  }

  return (
    <div className="tabs" role="tablist" aria-label="Sections" onKeyDown={handleKeyDown}>
      {TABS.map((tab) => (
        <a
          key={tab}
          id={tabId(tab)}
          className="tab"
          role="tab"
          href={tabHash(tab)}
          aria-selected={tab === current}
          aria-controls={panelId(tab)}
          tabIndex={tab === current ? 0 : -1}
        >
          {LABELS[tab]}
        </a>
      ))}
    </div>
  )
}
