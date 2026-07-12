import pytest


@pytest.mark.parametrize("header,expected", [
    ("x-content-type-options", "nosniff"),
    ("x-frame-options", "DENY"),
    ("referrer-policy", "same-origin")
])
def test_security_headers_present(client, header, expected):
    res = client.get("/login")
    assert res.headers.get(header) == expected


def test_content_security_policy_restricts_to_self(client):
    res = client.get("/login")
    csp = res.headers.get("content-security-policy")
    assert csp is not None
    assert "default-src 'self'" in csp
    assert "frame-ancestors 'none'" in csp


def test_auth_cookie_is_httponly_and_samesite_strict(client):
    from tests.conftest import login, ADMIN_ACCOUNT, ADMIN_PASSWORD
    res = login(client, ADMIN_ACCOUNT, ADMIN_PASSWORD)
    set_cookie = res.headers.get("set-cookie", "")
    assert "access_token=" in set_cookie
    assert "HttpOnly" in set_cookie
    assert "samesite=strict" in set_cookie.lower()
