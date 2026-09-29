from datetime import date

import pytest

from api.parser import Parsed, parse

# The PRD fixes today as Monday 28 Sep 2026 for its examples.
TODAY = date(2026, 9, 28)


def due(text, today=TODAY):
    return parse(text, today).due_date


# Every row of the PRD's acceptance table.
PRD_EXAMPLES = [
    ("grade SS2 scripts by Friday", "grade SS2 scripts", date(2026, 10, 2)),
    ("call mum tomorrow", "call mum", date(2026, 9, 29)),
    ("submit results due tmr", "submit results", date(2026, 9, 29)),
    ("submit HNG stage one today", "submit HNG stage one", date(2026, 9, 28)),
    ("lesson notes next Friday", "lesson notes", date(2026, 10, 9)),
    ("print exam papers in 3 days", "print exam papers", date(2026, 10, 1)),
    ("pay NEPA bill in 2 weeks", "pay NEPA bill", date(2026, 10, 12)),
    ("plan next term next week", "plan next term", date(2026, 10, 5)),
    ("review work by Monday", "review work", date(2026, 10, 5)),
    ("review work by mon", "review work", date(2026, 10, 5)),
    ("PTA meeting on 5 Oct", "PTA meeting", date(2026, 10, 5)),
    ("PTA meeting on Oct 5th", "PTA meeting", date(2026, 10, 5)),
    ("renew domain by 3 Jan", "renew domain", date(2027, 1, 3)),
    ("GRADE SCRIPTS BY FRIDAY", "GRADE SCRIPTS", date(2026, 10, 2)),
    ("call Sunday about fees", "call Sunday about fees", None),
    ("call Sunday", "call Sunday", None),
    ("stand by me", "stand by me", None),
    ("meeting on 31 Feb", "meeting on 31 Feb", None),
    ("rest in 400 days", "rest in 400 days", None),
    ("tomorrow", "tomorrow", None),
    ("buy printer ink", "buy printer ink", None),
]


@pytest.mark.parametrize("text, title, due_date", PRD_EXAMPLES)
def test_parse_matches_prd_example(text, title, due_date):
    result = parse(text, TODAY)

    assert result.title == title
    assert result.due_date == due_date


@pytest.mark.parametrize("text, title, due_date", PRD_EXAMPLES)
def test_parse_reports_matched_phrase_only_when_a_date_is_found(text, title, due_date):
    result = parse(text, TODAY)

    assert (result.matched is not None) == (due_date is not None)


# Weekday rules (PRD rules 2 and 3)


def test_parse_weekday_on_the_same_weekday_means_next_week():
    assert due("review work by Monday") == date(2026, 10, 5)


def test_parse_next_weekday_adds_seven_days_to_the_next_one():
    assert due("review work next Monday") == date(2026, 10, 12)


def test_parse_next_weekday_with_trigger_word():
    result = parse("review work by next Monday", TODAY)

    assert result.title == "review work"
    assert result.due_date == date(2026, 10, 12)
    assert result.matched == "by next Monday"


@pytest.mark.parametrize(
    "today, text, expected",
    [
        (date(2026, 10, 2), "call by Friday", date(2026, 10, 9)),
        (date(2026, 10, 2), "call by Saturday", date(2026, 10, 3)),
        (date(2026, 10, 2), "call next Saturday", date(2026, 10, 10)),
        (date(2026, 10, 4), "call by Monday", date(2026, 10, 5)),
        (date(2026, 10, 4), "call next Sunday", date(2026, 10, 18)),
        (date(2026, 12, 30), "call by Friday", date(2027, 1, 1)),
    ],
)
def test_parse_weekday_counts_one_to_seven_days_ahead(today, text, expected):
    assert due(text, today) == expected


@pytest.mark.parametrize(
    "today, expected",
    [
        (date(2026, 9, 28), date(2026, 10, 5)),
        (date(2026, 9, 30), date(2026, 10, 5)),
        (date(2026, 10, 4), date(2026, 10, 5)),
    ],
)
def test_parse_next_week_is_the_next_monday(today, expected):
    assert due("plan term next week", today) == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        ("call by tue", date(2026, 9, 29)),
        ("call by tues", date(2026, 9, 29)),
        ("call by Wednesday", date(2026, 9, 30)),
        ("call by thu", date(2026, 10, 1)),
        ("call by thurs", date(2026, 10, 1)),
        ("call by Thursday", date(2026, 10, 1)),
        ("call by sat", date(2026, 10, 3)),
        ("call by sun", date(2026, 10, 4)),
    ],
)
def test_parse_accepts_short_weekday_names(text, expected):
    assert due(text) == expected


# Safe words, and the trigger words


@pytest.mark.parametrize("trigger", ["by", "on", "due", "before"])
def test_parse_accepts_each_trigger_word(trigger):
    result = parse(f"call mum {trigger} friday", TODAY)

    assert result.title == "call mum"
    assert result.due_date == date(2026, 10, 2)
    assert result.matched == f"{trigger} friday"


def test_parse_removes_trigger_word_before_a_safe_date():
    result = parse("call mum by tomorrow", TODAY)

    assert result.title == "call mum"
    assert result.due_date == date(2026, 9, 29)
    assert result.matched == "by tomorrow"


def test_parse_treats_tonight_as_today():
    assert due("finish essay tonight") == TODAY


def test_parse_keeps_the_users_capitals_in_matched():
    result = parse("GRADE SCRIPTS BY FRIDAY", TODAY)

    assert result.matched == "BY FRIDAY"


def test_parse_ignores_case_of_the_date_phrase():
    assert due("call mum TOMORROW") == date(2026, 9, 29)


# "in N days/weeks" (PRD rule 5)


@pytest.mark.parametrize(
    "text, expected",
    [
        ("pay rent in 1 day", date(2026, 9, 29)),
        ("pay rent in 1 week", date(2026, 10, 5)),
        ("pay rent in 365 days", date(2027, 9, 28)),
        ("pay rent in 52 weeks", date(2027, 9, 27)),
        # The limit applies to N as typed (PRD rule 5), so 53 weeks is allowed.
        ("pay rent in 53 weeks", date(2027, 10, 4)),
        ("pay rent in 365 weeks", date(2033, 9, 26)),
    ],
)
def test_parse_accepts_counts_from_one_to_365(text, expected):
    assert due(text) == expected


@pytest.mark.parametrize(
    "text",
    ["rest in 0 days", "rest in 366 days", "rest in 400 days", "rest in 0 weeks", "rest in 366 weeks"],
)
def test_parse_rejects_counts_outside_one_to_365(text):
    result = parse(text, TODAY)

    assert result == Parsed(title=text, due_date=None, matched=None)


# Day and month (PRD rule 6)


@pytest.mark.parametrize(
    "text, expected",
    [
        ("PTA on 28 Sep", date(2026, 9, 28)),
        ("PTA on 27 Sep", date(2027, 9, 27)),
        ("PTA on Sept 30th", date(2026, 9, 30)),
        ("PTA on 1st October", date(2026, 10, 1)),
        ("PTA on 2nd Oct", date(2026, 10, 2)),
        ("PTA on 3rd Oct", date(2026, 10, 3)),
        ("PTA on October 4th", date(2026, 10, 4)),
        ("PTA on 31 dec", date(2026, 12, 31)),
        ("PTA on 1 Jan", date(2027, 1, 1)),
    ],
)
def test_parse_reads_day_and_month_in_either_order(text, expected):
    assert due(text) == expected


def test_parse_keeps_capitals_of_title_when_month_is_uppercase():
    result = parse("PTA MEETING ON OCT 5", TODAY)

    assert result.title == "PTA MEETING"
    assert result.due_date == date(2026, 10, 5)


@pytest.mark.parametrize(
    "text", ["meeting on 31 Feb", "meeting on 0 Jan", "meeting on 32 Jan", "meeting on Apr 31"]
)
def test_parse_gives_no_date_for_impossible_days(text):
    result = parse(text, TODAY)

    assert result == Parsed(title=text, due_date=None, matched=None)


@pytest.mark.parametrize(
    "today, expected",
    [
        (date(2028, 1, 10), date(2028, 2, 29)),
        (date(2026, 9, 28), None),  # 2026 is not a leap year
        (date(2028, 3, 1), None),  # passed in 2028, and 2029 is not a leap year
    ],
)
def test_parse_handles_29_feb(today, expected):
    assert due("renew by 29 Feb", today) == expected


# What is not a date


@pytest.mark.parametrize(
    "text",
    [
        "call mum tomorrow morning",
        "tomorrow call mum",
        "renew domain by 3 Jan 2027",
        "meet by the 5th",
        "call Sunday",
        "call on may",
        "stand by me",
        "standby",
        "meet subtomorrow",
        "sun",
        "buy 2 mon",
    ],
)
def test_parse_leaves_text_without_a_date_phrase_alone(text):
    result = parse(text, TODAY)

    assert result == Parsed(title=text, due_date=None, matched=None)


def test_parse_keeps_full_text_when_only_a_date_phrase_is_given():
    result = parse("by tomorrow", TODAY)

    assert result == Parsed(title="by tomorrow", due_date=None, matched=None)


def test_parse_requires_a_word_boundary_before_the_phrase():
    result = parse("standby tomorrow", TODAY)

    assert result.title == "standby"
    assert result.due_date == date(2026, 9, 29)


# Title cleaning


@pytest.mark.parametrize(
    "text, title",
    [
        ("call mum tomorrow.", "call mum"),
        ("call mum tomorrow!", "call mum"),
        ("call mum, tomorrow", "call mum"),
        ("call mum - tomorrow", "call mum"),
        ("  call mum   tomorrow  ", "call mum"),
        ("call mum: bring food tomorrow", "call mum: bring food"),
    ],
)
def test_parse_cleans_spaces_and_punctuation_around_the_phrase(text, title):
    result = parse(text, TODAY)

    assert result.title == title
    assert result.due_date == date(2026, 9, 29)


def test_parse_trims_text_with_no_date():
    result = parse("  buy ink  ", TODAY)

    assert result == Parsed(title="buy ink", due_date=None, matched=None)


def test_parse_of_empty_text_gives_empty_title():
    assert parse("", TODAY) == Parsed(title="", due_date=None, matched=None)
