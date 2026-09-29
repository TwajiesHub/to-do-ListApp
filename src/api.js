const API_BASE = '/api'

async function request(path, { method = 'GET', body } = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    method,
    headers: body ? { 'Content-Type': 'application/json' } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  })
  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`)
  }
  return response.status === 204 ? null : response.json()
}

export function getTodos() {
  return request('/todos')
}

export function createTodo(fields) {
  return request('/todos', { method: 'POST', body: fields })
}

export function updateTodo(id, fields) {
  return request(`/todos/${id}`, { method: 'PATCH', body: fields })
}

export function deleteTodo(id) {
  return request(`/todos/${id}`, { method: 'DELETE' })
}

export function clearCompletedTodos() {
  return request('/todos/completed', { method: 'DELETE' })
}

export function reorderTodos(ids) {
  return request('/todos/order', { method: 'PUT', body: { ids } })
}

export function parseText(text, today) {
  return request('/parse', { method: 'POST', body: { text, today } })
}
