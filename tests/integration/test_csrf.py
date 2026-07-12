from tests.conftest import register, ADMIN_ACCOUNT, ADMIN_PASSWORD

TASK = {
    "title": "Task", "start": "2026-07-13T09:00:00", "end": "2026-07-13T10:00:00"
}


def test_mutating_request_without_csrf_header_is_rejected(regular_client):
    res = regular_client.post("/api/tasks", json=TASK)
    assert res.status_code == 403


def test_mutating_request_with_wrong_csrf_header_is_rejected(regular_client):
    res = regular_client.post(
        "/api/tasks", json=TASK, headers={"X-CSRF-Token": "bogus"}
    )
    assert res.status_code == 403


def test_mutating_request_with_correct_csrf_header_succeeds(regular_client):
    token = regular_client.cookies.get("csrf_token")
    res = regular_client.post(
        "/api/tasks", json=TASK, headers={"X-CSRF-Token": token}
    )
    assert res.status_code == 201


def test_login_is_csrf_exempt(client):
    res = client.post(
        "/api/auth/login",
        json={"account": ADMIN_ACCOUNT, "password": ADMIN_PASSWORD}
    )
    assert res.status_code == 200


def test_register_is_csrf_exempt(client):
    res = register(client, "Carol", "carol", "carol-pw")
    assert res.status_code == 201


def test_safe_get_sets_csrf_cookie(client):
    client.get("/login")
    assert client.cookies.get("csrf_token")
