from tests.conftest import register, login, post_with_csrf, ADMIN_ACCOUNT, ADMIN_PASSWORD

TASK = {
    "title": "Task", "start": "2026-07-13T09:00:00", "end": "2026-07-13T10:00:00"
}


def _make_task(client, **overrides):
    return post_with_csrf(client, "/api/tasks", {**TASK, **overrides})


def test_task_is_scoped_to_creator(client):
    # Alice creates a task; Bob must not see it.
    register(client, "Alice", "alice", "alice-pw")
    login(client, "alice", "alice-pw")
    _make_task(client, title="Alice task")

    login(client, ADMIN_ACCOUNT, ADMIN_PASSWORD)
    register(client, "Bob", "bob", "bob-pw")
    login(client, "bob", "bob-pw")
    tasks = client.get(
        "/api/tasks?start=2026-07-01T00:00:00&end=2026-07-31T00:00:00"
    ).json()
    assert tasks == []


def test_regular_user_cannot_list_users(regular_client):
    assert regular_client.get("/api/users").status_code == 403


def test_admin_can_list_users(admin_client):
    assert admin_client.get("/api/users").status_code == 200


def test_regular_user_cannot_access_others_task(client):
    register(client, "Alice", "alice", "alice-pw")
    login(client, "alice", "alice-pw")
    task_id = _make_task(client).json()["id"]

    register(client, "Bob", "bob", "bob-pw")
    login(client, "bob", "bob-pw")
    assert client.get(f"/api/tasks/{task_id}").status_code == 404


def test_injected_user_id_is_ignored_for_regular_user(client):
    register(client, "Alice", "alice", "alice-pw")
    login(client, "alice", "alice-pw")
    created = _make_task(client, user_id=999).json()
    mine = client.get(
        "/api/tasks?start=2026-07-01T00:00:00&end=2026-07-31T00:00:00"
    ).json()
    assert len(mine) == 1
    assert mine[0]["id"] == created["id"]


def test_admin_can_view_another_users_board(client):
    register(client, "Alice", "alice", "alice-pw")
    login(client, "alice", "alice-pw")
    _make_task(client, title="Alice task")
    alice_id = client.get("/api/auth/me").json()["id"]

    login(client, ADMIN_ACCOUNT, ADMIN_PASSWORD)
    tasks = client.get(
        f"/api/tasks?start=2026-07-01T00:00:00&end=2026-07-31T00:00:00&user_id={alice_id}"
    ).json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Alice task"
