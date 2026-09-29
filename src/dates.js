const DUE_FORMAT = new Intl.DateTimeFormat('en-GB', {
  weekday: 'short',
  day: 'numeric',
  month: 'short',
})

function pad(number) {
  return String(number).padStart(2, '0')
}

// Built from local parts on purpose. toISOString() gives the UTC date, which is
// wrong between midnight and 01:00 in WAT.
export function todayLocal(now = new Date()) {
  return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`
}

// "2026-10-02" -> "Fri 2 Oct". Parsed as a local date so the day never shifts.
export function formatDue(dueDate) {
  const [year, month, day] = dueDate.split('-').map(Number)
  return DUE_FORMAT.format(new Date(year, month - 1, day)).replace(',', '')
}

// YYYY-MM-DD strings sort the same way as the dates they describe.
export function isOverdue(todo, today) {
  return !todo.done && Boolean(todo.due_date) && todo.due_date < today
}

export function isDueToday(todo, today) {
  return !todo.done && todo.due_date === today
}

const EDITED_FORMAT = { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit', hour12: false }

// A UTC timestamp from the API, shown in the browser's local time: "29 Sept, 09:45".
// The year is added only when the edit was not this year.
export function formatEdited(timestamp, now = new Date()) {
  const edited = new Date(timestamp)
  const options = edited.getFullYear() === now.getFullYear() ? EDITED_FORMAT : { ...EDITED_FORMAT, year: 'numeric' }
  return new Intl.DateTimeFormat('en-GB', options).format(edited)
}
