def test_list_todos_returns_empty_list_when_no_todos(client):
    response = client.get("/api/todos")

    assert response.status_code == 200
    assert response.json() == []
