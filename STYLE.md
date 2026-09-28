# Style

Code conventions for this repo. The goal is code a beginner can read and
explain: clear over clever.

## General

- Small functions that do one thing, with names that say what they do.
- Comments explain **why**, not what. Skip comments that repeat the code.
- No dead code, commented-out blocks or leftover `print`/`console.log` calls.
- No magic numbers: name them (`MAX_TITLE_LENGTH = 200`, `PARSE_DELAY_MS = 300`).
- Keep files focused. Split a file when it passes about 200 lines.

## Python (backend)

- Follow PEP 8: 4-space indents, `snake_case` for functions and variables,
  `PascalCase` for classes, `UPPER_CASE` for constants.
- Type hints on every function signature.
- Use SQLModel/Pydantic models for all request and response bodies. Never read
  raw dicts from requests.
- Validate at the edge: lengths, trimming and date formats live in the models,
  so route handlers stay short.
- Raise `HTTPException` with a clear `detail`, for example
  `"Todo 12 not found"`.
- The parser is a pure function: no database, no clock, no I/O. `today` is
  always passed in.
- Compile regex patterns once, at module level, with `re.IGNORECASE`.
- Short docstrings on public functions, one or two lines.

## Tests

- `pytest`, with files named `test_<area>.py` and tests named
  `test_<what>_<condition>`, for example `test_create_todo_rejects_empty_title`.
- Arrange, act, assert, with a blank line between each part.
- The parser tests use `pytest.mark.parametrize` over the PRD examples, with
  `today = date(2026, 9, 28)`.
- Each test starts from an empty temporary database. No test depends on
  another test's data.

## JavaScript and React (frontend)

- Function components and hooks only. One component per file.
- `PascalCase` for components and their files, `camelCase` for functions and
  variables.
- Components never call `fetch` directly. All requests go through `src/api.js`.
- State and side effects live in hooks (`useTodos`, `useSmartParse`).
  Components mostly render.
- Keep props few and named clearly: `onToggle`, `onDelete`, `onRename`.
- Dates cross the API as `YYYY-MM-DD` strings. Use the helpers in `src/dates.js`
  for the local date and formatting.

## CSS

- One `src/styles.css`, with design tokens as CSS variables on `:root`, taken
  from `TASTE.md`.
- `kebab-case` class names named for what the thing is: `.todo-item`,
  `.due-badge`, `.preview-chip`.
- No inline styles, except for values computed at runtime (such as dnd-kit
  transforms).
- No CSS framework.
- Mobile first: base styles for 360px, then a `min-width` media query for wider
  screens.

## Accessibility

- Every input has a label (visible, or `aria-label` when the design has none).
- Icon-only buttons get an `aria-label`, for example "Delete task: call mum".
- Everything works with the keyboard, and focus is always visible.
- Respect `prefers-reduced-motion`.

## API conventions

- JSON keys in `snake_case`, on both sides of the API.
- Status codes: 200 read or update, 201 created, 204 deleted, 404 not found,
  422 invalid input.

## Git

- Branch per milestone: `setup`, `core`, `due-dates`, `smart-add`, `polish`.
- Small commits with short, imperative messages:
  `Add due date badge to todo items`, `Fix parser for "next week"`.
- Run the tests before every commit.
- Never commit `.env`, `todos.db`, `.venv/`, `node_modules/` or `dist/`.
