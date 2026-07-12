from tests.conftest import register, login, ADMIN_ACCOUNT, ADMIN_PASSWORD


def test_register_creates_user_and_sets_cookie(client):
    res = register(client, "Bob", "bob", "bob-pw")
    assert res.status_code == 201
    body = res.json()
    assert body["account"] == "bob"
    assert body["role"] == "regular"
    assert "access_token" in client.cookies


def test_register_rejects_duplicate_account(client):
    register(client, "Bob", "bob", "bob-pw")
    res = register(client, "Bob Again", "bob", "other-pw")
    assert res.status_code == 409


def test_login_with_valid_credentials(client):
    res = login(client, ADMIN_ACCOUNT, ADMIN_PASSWORD)
    assert res.status_code == 200
    assert res.json()["role"] == "admin"


def test_login_with_wrong_password(client):
    res = login(client, ADMIN_ACCOUNT, "wrong-password")
    assert res.status_code == 401


def test_login_unknown_account(client):
    res = login(client, "ghost", "whatever")
    assert res.status_code == 401


def test_me_requires_authentication(client):
    assert client.get("/api/auth/me").status_code == 401


def test_me_returns_current_user(admin_client):
    res = admin_client.get("/api/auth/me")
    assert res.status_code == 200
    assert res.json()["account"] == ADMIN_ACCOUNT


def test_logout_clears_session(admin_client):
    admin_client.post(
        "/api/auth/logout",
        headers={"X-CSRF-Token": admin_client.cookies.get("csrf_token")}
    )
    assert admin_client.get("/api/auth/me").status_code == 401
