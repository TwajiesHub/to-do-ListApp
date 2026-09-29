import { useCallback, useEffect, useState } from 'react'

const STORAGE_KEY = 'tick.smartDates'

// On by default, so reviewers see the feature straight away.
function readSetting() {
  try {
    return localStorage.getItem(STORAGE_KEY) !== 'false'
  } catch {
    return true
  }
}

export function useSmartDatesSetting() {
  const [enabled, setEnabled] = useState(readSetting)

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, String(enabled))
    } catch {
      // The setting just won't survive a refresh. Nothing else depends on it.
    }
  }, [enabled])

  const toggle = useCallback(() => setEnabled((current) => !current), [])

  return [enabled, toggle]
}
