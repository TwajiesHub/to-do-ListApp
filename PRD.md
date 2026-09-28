# PRD: Tick, a to-do list with smart dates

- Owner: Uwajie Bonnke
- Context: HNG Internship 15, Stage One
- Deadline: Tuesday 29 Sep 2026, 23:59 WAT (feature cutoff 14:00 WAT)
- Working name "Tick" can change freely.

## Problem

People write tasks the way they speak: "grade SS2 scripts by Friday". Simple
to-do apps make you type the task, then open a date picker separately, so dates
get skipped and deadlines slip. The best-rated apps (Todoist, TickTick) solve
this with natural-language input. Tick brings a small, free version of that idea.

## Users

- **Primary:** a teacher juggling grading, lesson notes and admin, often on a phone.
- **Secondary:** HNG reviewers, who will open the live link and try the app in
  about two minutes.

## Goals

1. Meet the stage requirements: a working to-do app, a public GitHub repo and a
   live link.
2. Make the extra feature obvious within 10 seconds of opening the app.
3. Never lose or silently misread what the user typed.

## Out of scope for v1

User accounts and login, notes tab, reminders and notifications, recurring
tasks, calendar views, search and filters (they conflict with drag-and-drop
reordering), categories and hashtags, AI or paid APIs, offline editing.
Priority flags are a stretch goal only, after v1 ships.

## Baseline requirements

| ID | Requirement |
| --- | --- |
| B1 | **Add:** text input, "Add task" button, and Enter to submit. Title is trimmed and must be 1–200 characters. The button is disabled while the input is empty. |
| B2 | **Check off:** the checkbox toggles done. Done tasks show a tick and faded text, and stay in place. |
| B3 | **Edit:** double-click a title (or focus it and press Enter) to edit inline. Enter saves, Esc cancels, an empty title cancels. |
| B4 | **Delete:** a delete button on each task, with the accessible name "Delete task: {title}". |
| B5 | **Reorder:** drag by the handle with mouse or touch; keyboard reorder with Space to pick up, arrow keys to move, Space to drop. Order survives a refresh. |
| B6 | **Counter:** "3 left", plus "1 overdue" when any task is overdue. |
| B7 | **Clear completed:** a button, shown only when at least one task is done, that removes all done tasks. |
| B8 | **Persistence:** every change is saved to the database. A refresh shows the same tasks in the same order. |
| B9 | **Responsive:** works at 360px wide and on desktop. |

## Extra feature: Smart dates

### F1. Due dates (always available)

- An optional due date when adding (date picker) and when editing (click the
  due-date badge).
- The badge reads "Fri 2 Oct", "Today", or "Overdue". Overdue means the due date
  is before today and the task is not done.
- Clearing the date removes the badge.

### F2. Smart add

- With Smart dates on, the app reads the text after a 300ms pause in typing and
  shows the detected date as a chip under the input, for example:
  `Due Fri 2 Oct, from "by Friday"` with a × button.
- Nothing is saved while typing.
- Pressing Add saves the title without the date words, with the detected date.
- Pressing × on the chip dismisses it. The full original text becomes the title
  and no date is set.
- Picking a date manually overrides the detected date.
- If the preview is out of date when Add is pressed, parse first, then save.
  If parsing fails (for example, a network error), save the full text as the
  title with no date.

### F3. Toggle

- A switch labelled "Smart dates" in the header.
- **On by default**, so reviewers see the feature immediately.
- Stored in the browser (localStorage). No backend endpoint.
- When off, text is saved exactly as typed.
- Turning it off never hides dates that are already saved.

## Parser specification

Dates are only recognised at the **end** of the text. Because of that, the
grammar is regular, so regular expressions (finite automata) are enough.

```
input       → title [ date_phrase ]
date_phrase → safe_date | trigger risky_date
trigger     → by | on | due | before
safe_date   → today | tonight | tomorrow | tmr
            | next week
            | in NUMBER (day | days | week | weeks)
            | next WEEKDAY
risky_date  → WEEKDAY | DAY MONTH | MONTH DAY
```

- **Safe dates** work with or without a trigger word.
- **Risky dates** need a trigger word, because weekdays and months double as
  names (Sunday, Monday, May).
- Weekdays and months accept short forms (`mon`, `tue`, `jan`, `sept`). Days
  accept `st`, `nd`, `rd`, `th`.
- Matching ignores case. The title keeps the user's original capitals.

### Resolution rules

`today` is always supplied by the browser.

1. `today`, `tonight` → today. `tomorrow`, `tmr` → today + 1.
2. A weekday → the next one after today (1 to 7 days ahead). "by Monday" said
   on a Monday means next Monday.
3. `next` + weekday → that date + 7 days.
4. `next week` → next Monday.
5. `in N days` → today + N. `in N weeks` → today + 7N. N must be 1–365;
   otherwise there is no date.
6. DAY MONTH or MONTH DAY → this year, or next year if the date has passed.
   Impossible dates (31 Feb) give no date instead of an error.
7. Try longer patterns first, so "next Friday" beats "Friday".

### Title rules

- Remove the matched date phrase and its trigger word, then trim spaces and
  trailing punctuation.
- If nothing is left (the whole input was "tomorrow"), keep the full text as
  the title with no date.

### Acceptance examples

Today is fixed as **Monday 28 Sep 2026**. Every row is a test.

| Input | Title | Due date |
| --- | --- | --- |
| `grade SS2 scripts by Friday` | grade SS2 scripts | 2026-10-02 |
| `call mum tomorrow` | call mum | 2026-09-29 |
| `submit results due tmr` | submit results | 2026-09-29 |
| `submit HNG stage one today` | submit HNG stage one | 2026-09-28 |
| `lesson notes next Friday` | lesson notes | 2026-10-09 |
| `print exam papers in 3 days` | print exam papers | 2026-10-01 |
| `pay NEPA bill in 2 weeks` | pay NEPA bill | 2026-10-12 |
| `plan next term next week` | plan next term | 2026-10-05 |
| `review work by Monday` | review work | 2026-10-05 |
| `review work by mon` | review work | 2026-10-05 |
| `PTA meeting on 5 Oct` | PTA meeting | 2026-10-05 |
| `PTA meeting on Oct 5th` | PTA meeting | 2026-10-05 |
| `renew domain by 3 Jan` | renew domain | 2027-01-03 |
| `GRADE SCRIPTS BY FRIDAY` | GRADE SCRIPTS | 2026-10-02 |
| `call Sunday about fees` | call Sunday about fees | none |
| `call Sunday` | call Sunday | none |
| `stand by me` | stand by me | none |
| `meeting on 31 Feb` | meeting on 31 Feb | none |
| `rest in 400 days` | rest in 400 days | none |
| `tomorrow` | tomorrow | none |
| `buy printer ink` | buy printer ink | none |

## Interface states

- **First load:** show the cached list instantly. If there is no cache and the
  server takes over one second, show "Waking up the server…".
- **Empty list:** "Nothing to do yet. Add your first task above."
- **Save error:** undo the on-screen change and show "Couldn't save that change.
  Check your connection and try again."

## Success criteria

- Every acceptance example passes as an automated test.
- A reviewer can add a dated task using plain text within 10 seconds.
- Actions feel instant once the server is warm. The first load after idle takes
  under about three seconds.
- The whole app works with the keyboard alone, with no console errors.

## Submission checklist

- [ ] Public GitHub repo, with `main` deployed
- [ ] The live Vercel link works in a private window and on a phone
- [ ] README covers: what it is, the live link, features, how Smart dates work
      (the regular grammar), why SQLite locally and Postgres in production, how
      to run it, how to test it, and how AI was used
- [ ] Form: email, Zedu username, live link, AI model(s), IDE (Claude Code), and
      an honest prompt count
- [ ] Submitted on Tuesday 29 Sep, well before 23:59 WAT
