import {
  DndContext,
  KeyboardSensor,
  PointerSensor,
  closestCenter,
  useSensor,
  useSensors,
} from '@dnd-kit/core'
import {
  SortableContext,
  arrayMove,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable'
import { isPending } from '../hooks/useTodos.js'
import TodoItem from './TodoItem.jsx'

export default function TodoList({
  todos,
  today,
  onToggle,
  onDelete,
  onRename,
  onSetDueDate,
  onReorder,
}) {
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  )

  // A reorder sends every id, so wait until no task is still waiting for its real id.
  const reorderLocked = todos.some(isPending)

  // Screen readers hear task titles and positions, not dnd-kit's default ids.
  const titleOf = (id) => todos.find((t) => t.id === id)?.title ?? 'Task'
  const positionOf = (id) => todos.findIndex((t) => t.id === id) + 1
  const where = (id) => `position ${positionOf(id)} of ${todos.length}`
  const announcements = {
    onDragStart: ({ active }) =>
      `Picked up ${titleOf(active.id)}. Position ${positionOf(active.id)} of ${todos.length}.`,
    // Over itself means nothing has moved yet, so keep "Picked up" on screen.
    onDragOver: ({ active, over }) =>
      over && over.id !== active.id ? `${titleOf(active.id)} moved to ${where(over.id)}.` : undefined,
    onDragEnd: ({ active, over }) =>
      over
        ? `${titleOf(active.id)} dropped at ${where(over.id)}.`
        : `${titleOf(active.id)} dropped.`,
    onDragCancel: ({ active }) =>
      `Reorder cancelled. ${titleOf(active.id)} is back at ${where(active.id)}.`,
  }

  function handleDragEnd({ active, over }) {
    if (!over || active.id === over.id) return
    const from = todos.findIndex((t) => t.id === active.id)
    const to = todos.findIndex((t) => t.id === over.id)
    onReorder(arrayMove(todos, from, to))
  }

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCenter}
      accessibility={{ announcements }}
      onDragEnd={handleDragEnd}
    >
      <SortableContext items={todos.map((t) => t.id)} strategy={verticalListSortingStrategy}>
        <ul className="todo-list">
          {todos.map((todo) => (
            <TodoItem
              key={todo.id}
              todo={todo}
              today={today}
              reorderLocked={reorderLocked}
              onToggle={onToggle}
              onDelete={onDelete}
              onRename={onRename}
              onSetDueDate={onSetDueDate}
            />
          ))}
        </ul>
      </SortableContext>
    </DndContext>
  )
}
