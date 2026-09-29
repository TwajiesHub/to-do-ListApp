import { useEffect, useState } from 'react'
import { todayLocal } from '../dates.js'

const CHECK_INTERVAL_MS = 60_000

// The local date, refreshed so a tab left open past midnight doesn't show stale states.
export function useToday() {
  const [today, setToday] = useState(todayLocal)

  useEffect(() => {
    const refresh = () => setToday(todayLocal())
    const timer = setInterval(refresh, CHECK_INTERVAL_MS)
    document.addEventListener('visibilitychange', refresh)
    return () => {
      clearInterval(timer)
      document.removeEventListener('visibilitychange', refresh)
    }
  }, [])

  return today
}
