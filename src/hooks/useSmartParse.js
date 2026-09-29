import { useCallback, useEffect, useRef, useState } from 'react'
import * as api from '../api.js'

const PARSE_DELAY_MS = 300

// Asks the server what date it finds in the text, 300ms after typing stops.
// `preview` is the latest answer, with the text it was asked about: { text, title, due_date, matched }.
export function useSmartParse(text, today, enabled) {
  const [preview, setPreview] = useState(null)
  // Every change bumps this, so a slow answer for older text is ignored.
  const latestRequest = useRef(0)

  useEffect(() => {
    latestRequest.current += 1
    const request = latestRequest.current
    const trimmed = text.trim()

    if (!enabled || !trimmed) {
      setPreview(null)
      return undefined
    }

    const timer = setTimeout(async () => {
      try {
        const result = await api.parseText(trimmed, today)
        if (request === latestRequest.current) setPreview({ text: trimmed, ...result })
      } catch {
        if (request === latestRequest.current) setPreview(null)
      }
    }, PARSE_DELAY_MS)
    return () => clearTimeout(timer)
  }, [text, today, enabled])

  // For when Add is pressed before the preview has caught up. Returns null if the request fails.
  const parseNow = useCallback(async () => {
    latestRequest.current += 1
    try {
      return await api.parseText(text.trim(), today)
    } catch {
      return null
    }
  }, [text, today])

  return { preview, parseNow }
}
