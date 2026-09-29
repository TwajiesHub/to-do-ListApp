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

export default function TodoList({ todos, onToggle, onDelete, onRename, onReorder }) {
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  )

  // A reorder sends every id, so wait until no task is still waiting for its real id.
  const reorderLocked = todos.some(isPending)

  function handleDragEnd({ active, over }) {
    if (!over || active.id === over.id) return
    const from = todos.findIndex((t) => t.id === active.id)
    const to = todos.findIndex((t) => t.id === over.id)
    onReorder(arrayMove(todos, from, to))
  }

  return (
    <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
      <SortableContext items={todos.map((t) => t.id)} strategy={verticalListSortingStrategy}>
        <ul className="todo-list">
          {todos.map((todo) => (
            <TodoItem
              key={todo.id}
              todo={todo}
              reorderLocked={reorderLocked}
              onToggle={onToggle}
              onDelete={onDelete}
              onRename={onRename}
            />
          ))}
        </ul>
      </SortableContext>
    </DndContext>
  )
}
