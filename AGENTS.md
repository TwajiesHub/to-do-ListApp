# AGENTS.md

Instructions for AI coding agents (Claude Code) working in this repository.

## The project in one paragraph

Tick (working name) is a to-do list web app for HNG Internship 15, Stage One.
The baseline lets you add, check off, edit, delete and reorder tasks. The extra
feature is **Smart dates**: type "grade SS2 scripts by Friday" and the app
detects the due date with a small hand-written grammar, shows it as a preview,
and saves the task with that date.

- Deadline: **Tuesday 29 Sep 2026, 23:59 WAT**
- Feature cutoff: **Tuesday 29 Sep 2026, 18:00 WAT**. Whatever is merged to `main` by then is what ships. Target: M3 merged by 17:00.

## Read these before working

| File | Read it |
| --- | --- |
| `PRD.md` | Before any task. What to build, scope, acceptance criteria. |
| `ARCHITECTURE.md` | Before writing code. Structure, data model, API contract, deployment. |
| `STYLE.md` | Before writing code. Code conventions. |
| `TASTE.md` | Before any UI work. Look, feel and copy. |

If the docs conflict, `PRD.md` wins on *what* to build and `ARCHITECTURE.md`
wins on *how*. If a decision changes, update the relevant doc in the same change.

## Working with me

- I'm new to React and FastAPI. I know Python and some Django. After each step,
  explain what you did in short, plain language.
- Before building a milestone, give me a short plan and list any decisions you
  are making, with the default you picked. Wait for my OK.
- If you need a decision the docs don't cover, ask one clear question and say
  what you recommend.
- Don't hide problems. If a command fails or a test is flaky, tell me.

## Rules (non-negotiable)

1. Every endpoint gets tests in the same change: the success case plus each
   error case (422 for invalid input, 404 for a missing item).
2. Every example in the parser table in `PRD.md` is a test case (use
   `pytest.mark.parametrize`). Every parser bug you fix gets a new test.
3. Never delete, skip or weaken a failing test to make it pass. Fix the code,
   or stop and tell me.
4. Tests use a temporary SQLite database. Never the local `todos.db`, never Neon.
5. Never commit secrets or local files: `.env`, any `DATABASE_URL` value,
   `todos.db`, `.venv/`, `node_modules/`, `dist/`. Keep `.gitignore` up to date.
6. Use only the dependencies listed in `ARCHITECTURE.md`. Ask before adding any other.
7. The parser uses the Python standard library only (`re`, `datetime`).
   No `dateparser`, no paid APIs, no AI calls.
8. Stay in scope. Anything in the PRD's "Out of scope" list needs my explicit OK.
9. `main` must always deploy and work. Build on a branch and merge only when
   the Definition of Done below is met.

## Commands

Backend (from the repo root):

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # macOS / Linux
pip install -r requirements.txt -r requirements-dev.txt
uvicorn api.index:app --reload --port 8000
pytest
```

Frontend (from the repo root, in a second terminal):

```bash
npm install
npm run dev       # http://localhost:5173 (requests to /api are proxied to :8000)
npm run build
```

## Milestones and branches

| # | Branch | Goal |
| --- | --- | --- |
| M0 | `setup` | Hello world: Vite page plus `GET /api/todos` returning `[]`, deployed on Vercel with Neon connected. Proves the deployment works before any features. |
| M1 | `core` | Baseline: add, check off, double-click edit, delete, drag-and-drop reorder, counter, clear completed. |
| M2 | `due-dates` | Manual due date picker, due-date badge, overdue and due-today states, overdue count. |
| M3 | `smart-add` | Parser, `POST /api/parse`, preview chip, Smart dates toggle. |
| M4 | `polish` | README, empty and error states, mobile check, final deploy. |
| Stretch | `priority` | Only after M4 is merged. |

Merge each milestone before starting the next. If M3 is not merged by the
cutoff, ship M2.

### M4 extras (found during M1)

- On touch screens, a single tap on a task title opens the editor (double-tap
  is awkward on phones). Keep double-click and Enter on desktop.
- Make dnd-kit's screen-reader announcements use task titles instead of ids
  (`accessibility.announcements` on `DndContext`).

## Definition of done (every milestone)

- [ ] `pytest` passes with no skipped tests
- [ ] `npm run build` succeeds with no errors
- [ ] You ran the app and checked the feature in a browser, including at a
      narrow (360px) width
- [ ] The Vercel preview deployment for the branch works
- [ ] No secrets or local files are staged
- [ ] Docs are updated if any decision changed
- [ ] You gave me a short, plain-language summary of what changed
