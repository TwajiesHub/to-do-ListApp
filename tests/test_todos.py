def add_todo(client, title="buy chalk", **extra):
    return client.post("/api/todos", json={"title": title, **extra}).json()


def titles(client):
    return [todo["title"] for todo in client.get("/api/todos").json()]


# GET /api/todos


def test_list_todos_returns_empty_list_when_no_todos(client):
    response = client.get("/api/todos")

    assert response.status_code == 200
    assert response.json() == []


def test_list_todos_returns_todos_sorted_by_position(client):
    add_todo(client, "first")
    add_todo(client, "second")

    assert titles(client) == ["first", "second"]


# POST /api/todos


def test_create_todo_returns_201_with_defaults(client):
    response = client.post("/api/todos", json={"title": "buy chalk"})

    body = response.json()
    assert response.status_code == 201
    assert body["title"] == "buy chalk"
    assert body["done"] is False
    assert body["position"] == 0
    assert body["due_date"] is None
    assert body["created_at"]


def test_create_todo_trims_title(client):
    response = client.post("/api/todos", json={"title": "  buy chalk  "})

    assert response.json()["title"] == "buy chalk"


def test_create_todo_appends_at_the_end(client):
    add_todo(client, "first")

    second = add_todo(client, "second")

    assert second["position"] == 1


def test_create_todo_accepts_due_date(client):
    response = client.post(
        "/api/todos", json={"title": "grade scripts", "due_date": "2026-10-02"}
    )

    assert response.json()["due_date"] == "2026-10-02"


def test_create_todo_accepts_title_of_exactly_200_characters(client):
    response = client.post("/api/todos", json={"title": "a" * 200})

    assert response.status_code == 201


def test_create_todo_rejects_empty_title(client):
    response = client.post("/api/todos", json={"title": ""})

    assert response.status_code == 422


def test_create_todo_rejects_whitespace_only_title(client):
    response = client.post("/api/todos", json={"title": "   "})

    assert response.status_code == 422


def test_create_todo_rejects_title_over_200_characters(client):
    response = client.post("/api/todos", json={"title": "a" * 201})

    assert response.status_code == 422


def test_create_todo_rejects_missing_title(client):
    response = client.post("/api/todos", json={})

    assert response.status_code == 422


def test_create_todo_rejects_invalid_due_date(client):
    response = client.post("/api/todos", json={"title": "x", "due_date": "not-a-date"})

    assert response.status_code == 422


# PATCH /api/todos/{id}


def test_update_todo_marks_done(client):
    todo = add_todo(client)

    response = client.patch(f"/api/todos/{todo['id']}", json={"done": True})

    assert response.status_code == 200
    assert response.json()["done"] is True


def test_update_todo_changes_title_and_leaves_other_fields(client):
    todo = add_todo(client, due_date="2026-10-02")

    response = client.patch(f"/api/todos/{todo['id']}", json={"title": " new "})

    body = response.json()
    assert body["title"] == "new"
    assert body["due_date"] == "2026-10-02"


def test_update_todo_clears_due_date_with_null(client):
    todo = add_todo(client, due_date="2026-10-02")

    response = client.patch(f"/api/todos/{todo['id']}", json={"due_date": None})

    assert response.json()["due_date"] is None


def test_update_todo_with_empty_body_changes_nothing(client):
    todo = add_todo(client, due_date="2026-10-02")

    response = client.patch(f"/api/todos/{todo['id']}", json={})

    assert response.status_code == 200
    assert response.json()["due_date"] == "2026-10-02"


def test_update_todo_returns_404_for_missing_id(client):
    response = client.patch("/api/todos/999", json={"done": True})

    assert response.status_code == 404


def test_update_todo_rejects_empty_title(client):
    todo = add_todo(client)

    response = client.patch(f"/api/todos/{todo['id']}", json={"title": " "})

    assert response.status_code == 422


def test_update_todo_rejects_null_title(client):
    todo = add_todo(client)

    response = client.patch(f"/api/todos/{todo['id']}", json={"title": None})

    assert response.status_code == 422


def test_update_todo_rejects_null_done(client):
    todo = add_todo(client)

    response = client.patch(f"/api/todos/{todo['id']}", json={"done": None})

    assert response.status_code == 422


def test_update_todo_rejects_invalid_due_date(client):
    todo = add_todo(client)

    response = client.patch(f"/api/todos/{todo['id']}", json={"due_date": "soon"})

    assert response.status_code == 422


# DELETE /api/todos/{id}


def test_delete_todo_returns_204_and_removes_it(client):
    todo = add_todo(client)

    response = client.delete(f"/api/todos/{todo['id']}")

    assert response.status_code == 204
    assert titles(client) == []


def test_delete_todo_returns_404_for_missing_id(client):
    response = client.delete("/api/todos/999")

    assert response.status_code == 404


# DELETE /api/todos/completed


def test_clear_completed_deletes_only_done_todos(client):
    add_todo(client, "keep")
    done = add_todo(client, "done")
    client.patch(f"/api/todos/{done['id']}", json={"done": True})

    response = client.delete("/api/todos/completed")

    assert response.status_code == 200
    assert response.json() == {"deleted": 1}
    assert titles(client) == ["keep"]


def test_clear_completed_with_nothing_done_deletes_zero(client):
    add_todo(client)

    response = client.delete("/api/todos/completed")

    assert response.json() == {"deleted": 0}


# PUT /api/todos/order


def test_reorder_todos_rewrites_positions(client):
    a = add_todo(client, "a")
    b = add_todo(client, "b")
    c = add_todo(client, "c")

    response = client.put("/api/todos/order", json={"ids": [c["id"], a["id"], b["id"]]})

    body = response.json()
    assert response.status_code == 200
    assert [todo["title"] for todo in body] == ["c", "a", "b"]
    assert [todo["position"] for todo in body] == [0, 1, 2]
    assert titles(client) == ["c", "a", "b"]


def test_reorder_todos_rejects_missing_id(client):
    a = add_todo(client, "a")
    add_todo(client, "b")

    response = client.put("/api/todos/order", json={"ids": [a["id"]]})

    assert response.status_code == 422


def test_reorder_todos_rejects_extra_id(client):
    a = add_todo(client, "a")

    response = client.put("/api/todos/order", json={"ids": [a["id"], 999]})

    assert response.status_code == 422


def test_reorder_todos_rejects_duplicate_id(client):
    a = add_todo(client, "a")
    add_todo(client, "b")

    response = client.put("/api/todos/order", json={"ids": [a["id"], a["id"]]})

    assert response.status_code == 422


def test_reorder_todos_rejects_non_integer_ids(client):
    response = client.put("/api/todos/order", json={"ids": ["x"]})

    assert response.status_code == 422
