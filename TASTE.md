# Taste

How Tick should look, feel and read.

## The idea

Tick is a teacher's exercise book, not a software dashboard: ruled lines, a red
margin, blue-black ink, and the tick a teacher puts on finished work. Everything
else stays quiet.

## Principles

1. **Show before saving.** The app shows what it understood before it saves anything.
2. **Instant.** Every action appears on screen immediately.
3. **Never lose what the user typed.**
4. **One memorable thing.** The hand-drawn tick when a task is done. Nothing
   else competes with it.
5. **Phone first.** Many reviewers and teachers will open it on a phone.

## Palette

| Name | Hex | Use |
| --- | --- | --- |
| Paper | `#F7F9FC` | Page background. A cool white, not cream. |
| Rule | `#D3DFEE` | Ruled lines between tasks, input borders |
| Ink | `#1C2A4D` | Text, primary button, the tick |
| Faded ink | `#62708F` | Secondary text, done tasks, dates |
| Marking red | `#C93A3A` | The margin line and overdue only |
| Focus | `#2F6FEB` | Keyboard focus rings |

- Red means overdue or the margin line. Nothing else is red.
- No gradients, no shadows, no purple.
- Text must meet WCAG AA contrast on Paper.
- No dark mode in v1.

## Type

- **Atkinson Hyperlegible** from Google Fonts, falling back to `system-ui,
  sans-serif`. It was designed for legibility, which suits a list read at a glance.
- Sizes: body and tasks 17px, page title 28px at weight 700, small text 14px.
- Line height 1.5. Task rows sit on the ruled lines.
- Sentence case everywhere. No all-caps labels.

## Layout

A single left-aligned column, max width 640px, centred on wide screens. The red
margin line runs down the left of the list like an exercise book, and the drag
handles sit in the margin.

```
Tick                         Smart dates [on]
─────────────────────────────────────────────
[ Add a task, like "mark SS2 scripts by Friday" ] [ date ] [Add task]
  Due Fri 2 Oct, from "by Friday"  ×
─────────────────────────────────────────────
⠿ │ ✓  Buy chalk                    (faded)
⠿ │ ☐  Lesson notes                 Thu 1 Oct
⠿ ┃ ☐  Submit results               Overdue
⠿ │ ☐  Call Mr Ade                  Today
─────────────────────────────────────────────
3 left, 1 overdue             Clear completed
```

The margin line beside an overdue task thickens and turns fully red, so
overdue work stands out without a banner.

## Components

- **Task row:** at least 48px tall (a comfortable touch target), separated by a
  Rule line. No cards, no boxes.
- **Checkbox:** a rounded square outlined in Ink. When checked, a hand-drawn tick
  SVG draws in over about 250ms and the title fades to Faded ink. No
  strikethrough: the tick is the signal.
- **Due badge:** right-aligned small text. "Fri 2 Oct" in Faded ink, "Today" in
  Ink at weight 700, "Overdue" in Marking red. Click it to change or clear the date.
- **Preview chip:** under the input, outlined in Ink:
  `Due Fri 2 Oct, from "by Friday"` with a × button labelled "Remove due date".
- **Toggle:** a switch labelled "Smart dates" in the header, on the Tasks tab only.
- **Tabs:** "Tasks" and "Notes" as plain text under the title, over a Rule line.
  The current tab is in Ink with a 2px Ink underline. The other is in Faded ink.
  No pills, boxes or icons. Rows are at least 48px tall.
- **Note:** a bold title (17px, weight 700), the body underneath with its line
  breaks kept, then "Edited 29 Sept, 09:45" in Faded ink at 14px, then text
  buttons "Edit" and "Delete". Notes sit on Rule lines like tasks, with no cards,
  no margin line and no drag handles.
- **Note forms:** a title input and a taller text box, styled like the add-task
  input. "Add note" is a solid Ink button. When editing, "Save" is solid Ink and
  "Cancel" is a text button, both in place of the note's text.
- **Confirm delete:** pressing "Delete" swaps "Edit" and "Delete" for a bold
  "Confirm delete" and "Cancel" in the same place. No modal, no red.
- **Buttons:** "Add task" is solid Ink with Paper text. Secondary actions are
  text buttons. Corner radius 6px on inputs and buttons only.

## Motion

- Only three moments move: the tick drawing in, rows sliding while dragging,
  and the preview chip fading in (about 120ms).
- With `prefers-reduced-motion`, the tick appears without animating.
- No page-load animations, no hover effects on every row.

## Copy

Plain, short, sentence case, active verbs. A button says what happens.

| Where | Text |
| --- | --- |
| Input placeholder, Smart dates on | Add a task, like "mark SS2 scripts by Friday" |
| Input placeholder, Smart dates off | Add a task |
| Add button | Add task |
| Empty list | Nothing to do yet. Add your first task above. |
| Counter | 3 left, 1 overdue |
| Clear button | Clear completed |
| Save error | Couldn't save that change. Check your connection and try again. |
| Slow first load | Waking up the server… |
| Note title placeholder | Note title |
| Note body placeholder | Write a note (optional) |
| Add note button | Add note |
| Note edit buttons | Save, Cancel |
| Note delete buttons | Delete, then Confirm delete and Cancel |
| Note edit time | Edited 29 Sept, 09:45 |
| Empty notes | No notes yet. Add your first note above. |
| Notes load error | Couldn't load your notes. Check your connection and try again. |

- Errors say what happened and what to do. They don't apologise.
- Success needs no message: the change on screen is the confirmation.

## Avoid

Cards with shadows, gradients, purple, emoji in the interface, all-caps labels,
arrows on buttons, spinners that block the page, modals for simple edits,
success toasts and confetti.

## Quality floor

- Works at 360px wide and on desktop.
- Usable with the keyboard alone, with visible focus rings.
- Labels on every input.
- AA contrast.
- Reduced motion respected.
