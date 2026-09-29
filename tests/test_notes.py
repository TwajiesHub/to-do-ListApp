import time
from datetime import datetime, timedelta, timezone


def add_note(client, title="Staff meeting", **extra):
    return client.post("/api/notes", json={"title": title, **extra}).json()


def titles(client):
    return [note["title"] for note in client.get("/api/notes").json()]


def parse_time(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


# GET /api/notes


def test_list_notes_returns_empty_list_when_no_notes(client):
    response = client.get("/api/notes")

    assert response.status_code == 200
    assert response.json() == []


def test_list_notes_returns_most_recently_edited_first(client):
    first = add_note(client, "first")
    add_note(client, "second")
    add_note(client, "third")

    time.sleep(0.01)
    client.patch(f"/api/notes/{first['id']}", json={"body": "edited"})

    assert titles(client) == ["first", "third", "second"]


# POST /api/notes


def test_create_note_returns_201_with_defaults(client):
    response = client.post("/api/notes", json={"title": "Staff meeting"})

    body = response.json()
    assert response.status_code == 201
    assert body["title"] == "Staff meeting"
    assert body["body"] == ""
    assert body["id"]
    assert body["created_at"] == body["updated_at"]


def test_create_note_trims_title(client):
    response = client.post("/api/notes", json={"title": "  Staff meeting  "})

    assert response.json()["title"] == "Staff meeting"


def test_create_note_keeps_line_breaks_in_body(client):
    response = client.post(
        "/api/notes", json={"title": "List", "body": "chalk\nmarkers\n\nregister"}
    )

    assert response.json()["body"] == "chalk\nmarkers\n\nregister"


def test_create_note_normalises_windows_line_breaks(client):
    response = client.post("/api/notes", json={"title": "List", "body": "a\r\nb\rc"})

    assert response.json()["body"] == "a\nb\nc"


def test_create_note_accepts_the_longest_title_and_body(client):
    response = client.post("/api/notes", json={"title": "t" * 200, "body": "b" * 5000})

    assert response.status_code == 201


def test_create_note_rejects_empty_title(client):
    response = client.post("/api/notes", json={"title": ""})

    assert response.status_code == 422


def test_create_note_rejects_whitespace_only_title(client):
    response = client.post("/api/notes", json={"title": "   "})

    assert response.status_code == 422


def test_create_note_rejects_title_over_200_characters(client):
    response = client.post("/api/notes", json={"title": "t" * 201})

    assert response.status_code == 422


def test_create_note_rejects_missing_title(client):
    response = client.post("/api/notes", json={"body": "no title"})

    assert response.status_code == 422


def test_create_note_rejects_body_over_5000_characters(client):
    response = client.post("/api/notes", json={"title": "x", "body": "b" * 5001})

    assert response.status_code == 422


def test_create_note_rejects_a_body_that_is_not_text(client):
    response = client.post("/api/notes", json={"title": "x", "body": 5})

    assert response.status_code == 422


# PATCH /api/notes/{id}


def test_update_note_changes_title(client):
    note = add_note(client, body="keep me")

    response = client.patch(f"/api/notes/{note['id']}", json={"title": " New title "})

    body = response.json()
    assert response.status_code == 200
    assert body["title"] == "New title"
    assert body["body"] == "keep me"


def test_update_note_changes_body_and_leaves_title(client):
    note = add_note(client, "Keep")

    response = client.patch(f"/api/notes/{note['id']}", json={"body": "line 1\nline 2"})

    body = response.json()
    assert body["title"] == "Keep"
    assert body["body"] == "line 1\nline 2"


def test_update_note_clears_body_with_empty_string(client):
    note = add_note(client, body="something")

    response = client.patch(f"/api/notes/{note['id']}", json={"body": ""})

    assert response.json()["body"] == ""


def test_update_note_refreshes_updated_at_and_keeps_created_at(client):
    note = add_note(client)

    time.sleep(0.01)
    response = client.patch(f"/api/notes/{note['id']}", json={"title": "Changed"})

    body = response.json()
    assert parse_time(body["updated_at"]) > parse_time(note["updated_at"])
    assert body["created_at"] == note["created_at"]


def test_update_note_with_empty_body_changes_nothing(client):
    note = add_note(client)

    response = client.patch(f"/api/notes/{note['id']}", json={})

    assert response.status_code == 200
    assert response.json()["updated_at"] == note["updated_at"]


def test_update_note_returns_404_for_missing_id(client):
    response = client.patch("/api/notes/999", json={"title": "x"})

    assert response.status_code == 404


def test_update_note_rejects_empty_title(client):
    note = add_note(client)

    response = client.patch(f"/api/notes/{note['id']}", json={"title": " "})

    assert response.status_code == 422


def test_update_note_rejects_null_title(client):
    note = add_note(client)

    response = client.patch(f"/api/notes/{note['id']}", json={"title": None})

    assert response.status_code == 422


def test_update_note_rejects_null_body(client):
    note = add_note(client)

    response = client.patch(f"/api/notes/{note['id']}", json={"body": None})

    assert response.status_code == 422


def test_update_note_rejects_body_over_5000_characters(client):
    note = add_note(client)

    response = client.patch(f"/api/notes/{note['id']}", json={"body": "b" * 5001})

    assert response.status_code == 422


# DELETE /api/notes/{id}


def test_delete_note_returns_204_and_removes_it(client):
    note = add_note(client)

    response = client.delete(f"/api/notes/{note['id']}")

    assert response.status_code == 204
    assert titles(client) == []


def test_delete_note_returns_404_for_missing_id(client):
    response = client.delete("/api/notes/999")

    assert response.status_code == 404


def test_delete_note_leaves_other_notes(client):
    keep = add_note(client, "keep")
    gone = add_note(client, "gone")

    client.delete(f"/api/notes/{gone['id']}")

    assert titles(client) == [keep["title"]]


# Timestamps always go out as UTC with a Z, even from SQLite, which drops the timezone.


def assert_utc_with_z(value):
    assert value.endswith("Z")
    assert parse_time(value).utcoffset() == timedelta(0)


def test_note_timestamps_end_in_z_on_create_list_and_update(client):
    created = client.post("/api/notes", json={"title": "x"}).json()
    listed = client.get("/api/notes").json()[0]
    updated = client.patch(f"/api/notes/{created['id']}", json={"body": "y"}).json()

    for note in (created, listed, updated):
        assert_utc_with_z(note["created_at"])
        assert_utc_with_z(note["updated_at"])


def test_note_timestamps_are_the_current_utc_time(client):
    before = datetime.now(timezone.utc) - timedelta(seconds=5)

    note = add_note(client)

    assert before <= parse_time(note["created_at"]) <= datetime.now(timezone.utc) + timedelta(seconds=5)


def test_todo_created_at_also_ends_in_z(client):
    todo = client.post("/api/todos", json={"title": "x"}).json()
    listed = client.get("/api/todos").json()[0]

    assert_utc_with_z(todo["created_at"])
    assert_utc_with_z(listed["created_at"])


def test_note_id_must_be_an_integer(client):
    response = client.delete("/api/notes/abc")

    assert response.status_code == 422
