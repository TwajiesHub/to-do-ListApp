import pytest

TODAY = "2026-09-28"


def parse(client, text, today=TODAY):
    return client.post("/api/parse", json={"text": text, "today": today})


def test_parse_endpoint_returns_title_date_and_matched_phrase(client):
    response = parse(client, "grade SS2 scripts by Friday")

    assert response.status_code == 200
    assert response.json() == {
        "title": "grade SS2 scripts",
        "due_date": "2026-10-02",
        "matched": "by Friday",
    }


def test_parse_endpoint_returns_nulls_when_no_date_is_found(client):
    response = parse(client, "buy printer ink")

    assert response.status_code == 200
    assert response.json() == {"title": "buy printer ink", "due_date": None, "matched": None}


def test_parse_endpoint_gives_no_date_for_an_impossible_date(client):
    response = parse(client, "meeting on 31 Feb")

    assert response.status_code == 200
    assert response.json() == {"title": "meeting on 31 Feb", "due_date": None, "matched": None}


def test_parse_endpoint_uses_the_today_it_is_given(client):
    response = parse(client, "review work by Monday", today="2026-10-04")

    assert response.json()["due_date"] == "2026-10-05"


def test_parse_endpoint_resolves_next_weekday_by_prd_rule_three(client):
    response = parse(client, "review work next Monday")

    assert response.json()["due_date"] == "2026-10-12"


def test_parse_endpoint_trims_the_text(client):
    response = parse(client, "  call mum tomorrow  ")

    assert response.json()["title"] == "call mum"


def test_parse_endpoint_accepts_text_of_exactly_200_characters(client):
    response = parse(client, "a" * 200)

    assert response.status_code == 200


def test_parse_endpoint_saves_nothing(client):
    parse(client, "call mum tomorrow")

    assert client.get("/api/todos").json() == []


def test_parse_endpoint_rejects_empty_text(client):
    response = parse(client, "")

    assert response.status_code == 422


def test_parse_endpoint_rejects_whitespace_only_text(client):
    response = parse(client, "   ")

    assert response.status_code == 422


def test_parse_endpoint_rejects_text_over_200_characters(client):
    response = parse(client, "a" * 201)

    assert response.status_code == 422


def test_parse_endpoint_rejects_missing_text(client):
    response = client.post("/api/parse", json={"today": TODAY})

    assert response.status_code == 422


def test_parse_endpoint_rejects_missing_today(client):
    response = client.post("/api/parse", json={"text": "call mum"})

    assert response.status_code == 422


@pytest.mark.parametrize("today", ["soon", "2026-02-30", "28/09/2026", "", None, 20260928])
def test_parse_endpoint_rejects_an_invalid_today(client, today):
    response = parse(client, "call mum tomorrow", today=today)

    assert response.status_code == 422
