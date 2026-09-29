import { useEffect, useState } from 'react'

export const TABS = ['tasks', 'notes']
const DEFAULT_TAB = 'tasks'

export function tabHash(tab) {
  return `#/${tab}`
}

function readTab() {
  const tab = window.location.hash.replace('#/', '')
  return TABS.includes(tab) ? tab : DEFAULT_TAB
}

// The current tab lives in the URL hash, so refresh and the back button both work.
export function useHashTab() {
  const [tab, setTab] = useState(readTab)

  useEffect(() => {
    const update = () => setTab(readTab())
    window.addEventListener('hashchange', update)
    return () => window.removeEventListener('hashchange', update)
  }, [])

  return tab
}
