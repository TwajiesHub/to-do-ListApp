"""Smart dates: find a due date at the end of a task's text.

Dates are only recognised at the end of the text, so the grammar is regular and
regular expressions are enough. Standard library only, no clock and no I/O:
`today` is always passed in.
"""

import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, timedelta

TRIGGERS = "by|on|due|before"
MAX_DAYS_AHEAD = 365
DAYS_IN_WEEK = 7
MONDAY = 0

WEEKDAYS = {
    "monday": 0, "mon": 0,
    "tuesday": 1, "tues": 1, "tue": 1,
    "wednesday": 2, "wed": 2,
    "thursday": 3, "thurs": 3, "thur": 3, "thu": 3,
    "friday": 4, "fri": 4,
    "saturday": 5, "sat": 5,
    "sunday": 6, "sun": 6,
}  # fmt: skip

MONTHS = {
    "january": 1, "jan": 1,
    "february": 2, "feb": 2,
    "march": 3, "mar": 3,
    "april": 4, "apr": 4,
    "may": 5,
    "june": 6, "jun": 6,
    "july": 7, "jul": 7,
    "august": 8, "aug": 8,
    "september": 9, "sept": 9, "sep": 9,
    "october": 10, "oct": 10,
    "november": 11, "nov": 11,
    "december": 12, "dec": 12,
}  # fmt: skip

# Punctuation allowed after the date phrase, and trimmed from the end of the title.
AFTER_PHRASE = r"[\s.,!?;:]*$"
TITLE_TRAILING = re.compile(r"[\s,;:.\-–—]+$")


@dataclass(frozen=True)
class Parsed:
    title: str
    due_date: date | None
    matched: str | None


def _names(names: dict[str, int]) -> str:
    """Build a regex alternation, longest name first so "monday" beats "mon"."""
    return "|".join(sorted(names, key=len, reverse=True))


def _compile(date_part: str, needs_trigger: bool) -> re.Pattern[str]:
    """A phrase at the end of the text, starting at a word boundary.

    Safe dates may have a trigger word (by, on, due, before). Risky dates must.
    """
    trigger = rf"(?:{TRIGGERS})\s+"
    trigger_part = trigger if needs_trigger else f"(?:{trigger})?"
    return re.compile(
        rf"(?<!\S)(?P<phrase>{trigger_part}{date_part}){AFTER_PHRASE}",
        re.IGNORECASE,
    )


def _next_weekday(today: date, weekday: int) -> date:
    """The next given weekday after today, 1 to 7 days ahead."""
    days_ahead = (weekday - today.weekday()) % DAYS_IN_WEEK or DAYS_IN_WEEK
    return today + timedelta(days=days_ahead)


def _resolve_word(match: re.Match[str], today: date) -> date | None:
    if match["word"].lower() in ("tomorrow", "tmr"):
        return today + timedelta(days=1)
    return today


def _resolve_weekday(match: re.Match[str], today: date) -> date | None:
    return _next_weekday(today, WEEKDAYS[match["weekday"].lower()])


def _resolve_next_weekday(match: re.Match[str], today: date) -> date | None:
    return _resolve_weekday(match, today) + timedelta(days=DAYS_IN_WEEK)


def _resolve_next_week(match: re.Match[str], today: date) -> date | None:
    return _next_weekday(today, MONDAY)


def _resolve_in_count(match: re.Match[str], today: date) -> date | None:
    count = int(match["count"])
    if not 1 <= count <= MAX_DAYS_AHEAD:
        return None
    per_unit = DAYS_IN_WEEK if match["unit"].lower().startswith("week") else 1
    return today + timedelta(days=count * per_unit)


def _resolve_day_and_month(match: re.Match[str], today: date) -> date | None:
    """This year, or next year if the date has passed. Impossible dates give None."""
    month = MONTHS[match["month"].lower()]
    day = int(match["day"])
    for year in (today.year, today.year + 1):
        try:
            candidate = date(year, month, day)
        except ValueError:
            return None
        if candidate >= today:
            return candidate
    return None


Resolver = Callable[[re.Match[str], date], date | None]

# Longest patterns first, so "next Friday" beats "Friday".
RULES: list[tuple[re.Pattern[str], Resolver]] = [
    (_compile(rf"next\s+(?P<weekday>{_names(WEEKDAYS)})", False), _resolve_next_weekday),
    (_compile(r"next\s+week", False), _resolve_next_week),
    (_compile(r"in\s+(?P<count>\d+)\s+(?P<unit>days?|weeks?)", False), _resolve_in_count),
    (_compile(r"(?P<word>today|tonight|tomorrow|tmr)", False), _resolve_word),
    (_compile(rf"(?P<weekday>{_names(WEEKDAYS)})", True), _resolve_weekday),
    (
        _compile(rf"(?P<day>\d{{1,2}})(?:st|nd|rd|th)?\s+(?P<month>{_names(MONTHS)})", True),
        _resolve_day_and_month,
    ),
    (
        _compile(rf"(?P<month>{_names(MONTHS)})\s+(?P<day>\d{{1,2}})(?:st|nd|rd|th)?", True),
        _resolve_day_and_month,
    ),
]


def parse(text: str, today: date) -> Parsed:
    """Split text into a title and a due date. With no usable date, the text is the title."""
    text = text.strip()
    for pattern, resolve in RULES:
        match = pattern.search(text)
        if match is None:
            continue
        due_date = resolve(match, today)
        title = TITLE_TRAILING.sub("", text[: match.start("phrase")])
        # The first pattern that fits decides. An impossible date, or a phrase
        # with nothing before it, leaves the text alone.
        if due_date is None or not title:
            break
        return Parsed(title=title, due_date=due_date, matched=match["phrase"])
    return Parsed(title=text, due_date=None, matched=None)
