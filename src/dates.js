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
