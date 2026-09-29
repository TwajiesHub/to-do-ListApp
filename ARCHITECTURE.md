# Architecture

## System overview

```
GitHub (main + feature branches)
   │  every push deploys
   ▼
Vercel project (one live link)
   ├── Static React app      Vite build → dist/
   └── Python function       FastAPI app in api/index.py, all routes under /api
             │  SQL
             ▼
        Neon Postgres        production data, via DATABASE_URL

Local:  Vite :5173 ──proxy /api──▶ uvicorn :8000 ──▶ SQLite todos.db
Tests:  pytest ──▶ temporary SQLite file
```

The parser never touches the database. It takes text and a date and returns a
guess. The Smart dates toggle lives in the browser, so it never reaches the
backend.

## Key decisions

| Decision | Why |
| --- | --- |
| React + Vite, plain JavaScript | Fast to set up and build. No TypeScript, to keep the learning load small this week. |
| FastAPI + SQLModel | Small and typed, with validation and API docs built in. SQLModel combines the table model and the request schemas. |
| One Vercel project for both | Same origin, so no CORS. One link, and push = deploy, with a preview link per branch. |
| Postgres (Neon) in production, SQLite locally | Serverless hosts have no permanent disk, so a SQLite file there loses data. The same code switches via `DATABASE_URL`. |
| Hand-written regular grammar for dates | Free, instant to load (no cold-start cost), fully testable, and explainable line by line. |
| `today` is sent by the browser | Vercel runs in UTC and users are in WAT (UTC+1). Near midnight the server's "today" would be wrong. |
| Toggle stored in localStorage | It's a display preference, so it needs no endpoints. |
| Optimistic updates | A network round trip takes about 100–300ms. The screen updates immediately, and the request runs in the background. |
| Integer `position`, fully rewritten on reorder | Simple and atomic, and fine for dozens of tasks. Fractional indexing is a possible later upgrade. |
| `due_date` column exists from M0 | No migrations are needed later in the week. |
| Current tab in the URL hash | A refresh and the back button keep the tab, with no router library. |
| UTC timestamps always end in `Z` | SQLite loses the timezone. The browser needs it to show local time correctly. |

## Folder structure

```
.
├── api/
│   ├── __init__.py
│   ├── index.py          FastAPI app, lifespan, includes the router (Vercel entrypoint)
│   ├── routes.py         task and parse routes (an APIRouter)
│   ├── notes.py          note routes (an APIRouter)
│   ├── db.py             engine, sessions, DATABASE_URL handling
│   ├── models.py         SQLModel table and request/response schemas
│   └── parser.py         Smart dates grammar (pure function, stdlib only)
├── tests/
│   ├── conftest.py       temporary SQLite database and TestClient fixtures
│   ├── test_todos.py     task endpoint tests
│   ├── test_notes.py     note endpoint tests and the UTC "Z" timestamp checks
│   └── test_parser.py    parser tests, one per PRD example
├── src/
│   ├── main.jsx
│   ├── App.jsx
│   ├── api.js            every fetch call lives here
│   ├── dates.js          today-in-local-time and date formatting helpers
│   ├── hooks/
│   │   ├── useTodos.js   list state, optimistic updates, cache
│   │   ├── useNotes.js   notes state, optimistic updates, cache
│   │   ├── useHashTab.js current tab (tasks or notes) kept in the URL hash
│   │   ├── useToday.js   local date, refreshed so overdue states stay correct
│   │   ├── useSmartDatesSetting.js  the Smart dates switch, saved in localStorage
│   │   └── useSmartParse.js  debounced parsing, stale-response guard
│   ├── components/
│   │   ├── Header.jsx        title and Smart dates toggle (Tasks tab only)
│   │   ├── Tabs.jsx          the Tasks | Notes tab switch
│   │   ├── TasksView.jsx     everything on the Tasks tab (add, list, footer)
│   │   ├── NotesView.jsx     everything on the Notes tab
│   │   ├── AddNote.jsx       title and body form
│   │   ├── NoteItem.jsx      a note with inline edit and inline delete confirm
│   │   ├── PreviewChip.jsx   the "Due Fri 2 Oct, from ..." chip with a remove button
│   │   ├── AddTask.jsx       input, date picker, preview chip (empty slot for M3)
│   │   ├── TodoList.jsx      dnd-kit sortable list
│   │   ├── TodoItem.jsx      handle, checkbox, title/inline edit, delete
│   │   ├── DueDate.jsx       due-date badge, "Add date" button and inline date editor
│   │   └── Footer.jsx        counter and Clear completed
│   └── styles.css
├── index.html
├── package.json
├── vite.config.js
├── requirements.txt
├── requirements-dev.txt
├── vercel.json
├── .gitignore
├── AGENTS.md  CLAUDE.md  PRD.md  ARCHITECTURE.md  STYLE.md  TASTE.md
└── README.md
```

## Approved dependencies

Pin exact versions when installing.

- `requirements.txt`: `fastapi`, `sqlmodel`, `psycopg[binary]`
- `requirements-dev.txt`: `uvicorn[standard]`, `pytest`, `httpx`
- `package.json` dependencies: `react`, `react-dom`, `@dnd-kit/core`,
  `@dnd-kit/sortable`, `@dnd-kit/utilities`
- `package.json` devDependencies: `vite`, `@vitejs/plugin-react`

## Data model

Table `todos`:

| Column | Type | Rules |
| --- | --- | --- |
| `id` | integer | Primary key, auto-increment |
| `title` | varchar(200) | Not null. Trimmed, 1–200 characters |
| `done` | boolean | Not null, default false |
| `position` | integer | Not null. New tasks get max + 1 (0 if the list is empty) |
| `due_date` | date | Nullable |
| `created_at` | timestamp with time zone | Not null, default now (UTC) |

Table `notes` (added in M5):

| Column | Type | Rules |
| --- | --- | --- |
| `id` | integer | Primary key, auto-increment |
| `title` | varchar(200) | Not null. Trimmed, 1–200 characters |
| `body` | varchar(5000) | Not null, default empty. At most 5000 characters. Line breaks are stored as newlines |
| `created_at` | timestamp with time zone | Not null, default now (UTC) |
| `updated_at` | timestamp with time zone | Not null. Set on create and refreshed by every PATCH that changes something |

Tables are created at startup with `SQLModel.metadata.create_all`, which also
creates any table that is missing, so `notes` appears by itself on the first
deploy. There are no migrations in v1. If an existing table's columns must
change, delete the local `todos.db`, and ask before touching Neon.

## API contract

- Base path `/api`. JSON bodies with snake_case keys.
- Dates are `YYYY-MM-DD`. Timestamps are ISO 8601 in UTC and **always end in
  `Z`**. SQLite drops the timezone, so `api/models.py` treats a datetime with no
  timezone as UTC before it is sent (`UtcDateTime`). Postgres values are
  converted to UTC too.
- Interactive docs at `/api/docs` (set `docs_url="/api/docs"` and
  `openapi_url="/api/openapi.json"`).

Todo object:

```json
{
  "id": 1,
  "title": "grade SS2 scripts",
  "done": false,
  "position": 0,
  "due_date": "2026-10-02",
  "created_at": "2026-09-28T10:30:00Z"
}
```

| # | Method and path | Request body | Success | Errors |
| --- | --- | --- | --- | --- |
| 1 | `GET /api/todos` | none | 200, list of todos sorted by position | none |
| 2 | `POST /api/todos` | `{title, due_date?}` | 201, the new todo, added at the end | 422 |
| 3 | `PATCH /api/todos/{id}` | any of `{title, done, due_date}`; `due_date: null` clears it | 200, the updated todo | 404, 422 |
| 4 | `DELETE /api/todos/completed` | none | 200, `{deleted: n}` | none |
| 5 | `DELETE /api/todos/{id}` | none | 204 | 404 |
| 6 | `PUT /api/todos/order` | `{ids: [int]}` | 200, the reordered list | 422 |
| 7 | `POST /api/parse` | `{text, today}` | 200, `{title, due_date, matched}` | 422 |
| 8 | `GET /api/notes` | none | 200, list of notes, most recently edited first | none |
| 9 | `POST /api/notes` | `{title, body?}` | 201, the new note | 422 |
| 10 | `PATCH /api/notes/{id}` | any of `{title, body}` | 200, the updated note | 404, 422 |
| 11 | `DELETE /api/notes/{id}` | none | 204 | 404 |

Notes:

- **PATCH** changes only the fields that were sent (use `exclude_unset`), so a
  missing field and a `null` field mean different things.
- **Route order:** declare `DELETE /api/todos/completed` before
  `DELETE /api/todos/{id}`, or FastAPI treats "completed" as an id and returns 422.
- **Reorder:** `ids` must be exactly the current set of ids, with no missing,
  extra or duplicate ids, or the request returns 422. Rewrite all positions in
  one transaction.
- **Parse:** `text` must be 1–200 characters and `today` a valid date.
  `matched` is the phrase that was recognised (for example `"by Friday"`), or
  `null`. The endpoint saves nothing. Grammar and rules are in `PRD.md`.
- **Notes:** the note object is `{id, title, body, created_at, updated_at}`.
  `title` is trimmed and 1–200 characters. `body` is optional (default empty),
  at most 5000 characters, and Windows line breaks are turned into plain ones.
  Neither field can be `null` in a PATCH (send an empty string to clear the
  body). A PATCH that changes at least one field sets `updated_at` to now, and an
  empty PATCH changes nothing. The list is ordered by `updated_at` descending,
  then `id` descending.

## Backend modules

- **`api/db.py`**: reads `DATABASE_URL`, defaulting to `sqlite:///./todos.db`.
  Rewrites `postgres://` and `postgresql://` to `postgresql+psycopg://` (Neon
  and Vercel supply the plain form). Creates the engine with
  `pool_pre_ping=True`. For SQLite, passes `check_same_thread=False`. Provides a
  `get_session` dependency that tests override.
- **`api/models.py`**: the `Todo` and `Note` table models, plus `TodoCreate`,
  `TodoUpdate`, `TodoRead`, `NoteCreate`, `NoteUpdate`, `NoteRead`,
  `ReorderRequest`, `ParseRequest` and `ParseResult`. `UtcDateTime` is the type
  that puts a `Z` on every timestamp sent out.
- **`api/parser.py`**: `parse(text: str, today: date) -> Parsed`, where `Parsed`
  is a frozen dataclass `(title, due_date, matched)`. Pure, with no I/O, and
  imports only `re`, `datetime` and other standard-library modules (no
  SQLModel), so `POST /api/parse` copies it into the `ParseResult` schema.
  Regex patterns are compiled once at import with `re.IGNORECASE` and tried
  longest first. The first pattern that fits decides: an impossible date
  (31 Feb, 29 Feb in a non-leap year, `in 400 days`) leaves the text alone.
- **`api/routes.py`**: an `APIRouter` with prefix `/api` holding the task and
  parse routes. Split out of `index.py` to stay under about 200 lines. The
  `completed` and `order` routes are declared before `/todos/{todo_id}`.
- **`api/notes.py`**: an `APIRouter` with prefix `/api` holding the note routes.
- **`api/index.py`**: creates the FastAPI app, creates tables in the lifespan
  handler, and includes the routers from `routes.py` and `notes.py`. This is the
  Vercel entrypoint.

## Frontend modules

- **`src/api.js`**: all requests go through here, with base path `/api`.
  Throws an `Error` with a readable message on any non-2xx response.
- **`src/dates.js`**: `todayLocal()` returns the browser's local date as
  `YYYY-MM-DD`. Do **not** use `toISOString()`, which gives the UTC date and is
  wrong between midnight and 01:00 WAT. `formatDue()` uses
  `Intl.DateTimeFormat('en-GB', { weekday: 'short', day: 'numeric', month: 'short' })`,
  which gives "Fri 2 Oct" (September comes out as "Sept"). `isOverdue()` and
  `isDueToday()` compare `YYYY-MM-DD` strings, and done tasks are never either.
  `formatEdited()` shows a note's UTC `updated_at` in local time, for example
  "29 Sept, 09:45" (the year is added only for a different year).
- **`src/hooks/useTodos.js`**: holds the ordered array of todos. On load it
  shows the cached list from localStorage (`tick.todos.v1`), then refreshes from
  the server. Add, toggle, edit, delete, reorder and clear are optimistic, with
  rollback and an error message on failure. A new task gets a temporary negative
  id until the server responds.
- **`src/hooks/useNotes.js`**: the same pattern as `useTodos`, for notes: a cached
  list (`tick.notes.v1`), then a refresh from the server, and optimistic add,
  edit and delete with rollback and the save-error message. Notes are always
  kept most recently edited first. A new note has a temporary negative id, and its
  Edit and Delete buttons are disabled until the server replies. An edit moves the
  note to the top at once, and the server's own `updated_at` replaces the guess.
- **`src/hooks/useHashTab.js`**: the current tab (`tasks` or `notes`) is read from
  `location.hash` (`#/tasks`, `#/notes`) and follows `hashchange`, so the back
  button works. Anything else means Tasks.
- **`src/components/Tabs.jsx`**: two links with `role="tab"`, moved with the arrow
  keys, Home and End. `App.jsx` shows each view in a `role="tabpanel"`. The Notes
  view is mounted the first time its tab opens (so notes load then), and after
  that both views stay mounted, with the other one `hidden`.
- **`src/hooks/useSmartParse.js`**: waits 300ms after typing stops, then calls
  `/api/parse`. A request counter ignores responses for older text. Exposes
  `parseNow()` for use when Add is pressed while the preview is stale.
- **`src/hooks/useToday.js`**: returns `todayLocal()` and refreshes it every
  minute and when the tab becomes visible, so a tab left open past midnight
  stays correct.
- **`src/components/DueDate.jsx`**: the badge ("Fri 2 Oct", "Today" or "Overdue"),
  the "Add date" button for tasks without a date, and the inline editor. The
  editor's date input is uncontrolled and saves on each valid change (years
  below 1000 are ignored while typing). Esc, Enter or blur closes it.
- **`AddTask`** keeps the due date in one `dueDate` state that both the picker
  and Smart dates set, plus a `dateSource` (`none`, `smart`, `picker` or
  `dismissed`). The chip is shown only for `smart`, and only the chip changes
  the title: with `picker` or `dismissed`, or with the switch off, the text is
  saved exactly as typed. The `dismissed` state lasts until the input is
  cleared or the task is added. The `.add-task-preview` slot under the input
  holds the chip and takes no space while empty.
- **Overdue** means `due_date < todayLocal()` and not done.
- **Toggle** is stored in localStorage as `tick.smartDates`, default `true`.

## Local development

`vite.config.js` proxies `/api` to `http://localhost:8000`. The app is
same-origin both locally and in production, so no CORS middleware is needed.

## Deployment on Vercel

- One project at the repo root. The Vite framework preset builds to `dist/`.
- The FastAPI app in `api/index.py` runs as a Python function. `vercel.json`
  sends every `/api/...` request to it.
- **Before writing `vercel.json`, check Vercel's current docs** for running
  FastAPI alongside a Vite frontend in one project. Prove it works in M0 with the
  hello-world version, including that `api/index.py` can import its sibling
  modules on Vercel.
- **Neon:** create it from the Vercel dashboard (Storage, then Postgres), which
  adds the environment variables. Set `DATABASE_URL` to the **pooled**
  connection string (the host contains `-pooler`).
- **Current setup:**
  - The Vercel project is named `todo`. Live URL: `todo-inky-one-57.vercel.app`.
  - The function region is London (`lhr1`), next to the database.
  - A Neon Postgres database in London is connected. `DATABASE_URL` is set for
    **Production and Preview only**, not Development, so local work falls back
    to SQLite.
  - Python 3.14 is installed locally. Check that `pydantic-core` and
    `psycopg[binary]` have wheels for it before pinning versions.
- Secrets live only in Vercel's environment settings and in a local `.env`,
  which is gitignored.
- Every branch push gets a preview URL. `main` is production.

## Performance

- Optimistic updates, a cached list on load, and a 300ms debounce on parsing.
- Parser regexes are compiled once, and there are no heavy libraries.
- `GET /api/todos` on page load warms both the function and the database.
- Neon's pooled connection string suits short-lived serverless connections.
- No keep-alive pinger: it would use up Neon's free compute hours.

## Known risks

| Risk | Plan |
| --- | --- |
| Vercel configuration for Vite + Python in one project | Prove it in M0, before any features |
| Import paths inside `api/` behaving differently on Vercel | Prove it in M0 |
| Neon wakes slowly after about 5 minutes idle | Hidden by the cached list and the waking message |
| Everyone shares one list (no accounts) | Accepted for v1. Mention it in the README |
