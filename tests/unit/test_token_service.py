import jwt
from datetime import timedelta

from app.security.token_service import TokenService

SECRET = "unit-test-secret-key-32-bytes-minimum!"


def test_create_and_decode_roundtrip():
    service = TokenService(SECRET)
    token = service.create(user_id=7, role="admin")
    payload = service.decode(token)
    assert payload is not None
    assert payload["sub"] == "7"
    assert payload["role"] == "admin"


def test_decode_rejects_garbage_token():
    service = TokenService(SECRET)
    assert service.decode("not-a-real-token") is None


def test_decode_rejects_wrong_secret():
    issuer = TokenService(SECRET)
    verifier = TokenService("a-different-secret-key-of-length-32ch")
    token = issuer.create(user_id=1, role="regular")
    assert verifier.decode(token) is None


def test_decode_rejects_expired_token():
    service = TokenService(SECRET, ttl_hours=-1)  # already expired
    token = service.create(user_id=1, role="regular")
    assert service.decode(token) is None


def test_expiry_is_in_the_future_for_positive_ttl():
    service = TokenService(SECRET, ttl_hours=24)
    token = service.create(user_id=1, role="regular")
    payload = jwt.decode(token, SECRET, algorithms=["HS256"])
    assert payload["exp"] > payload["iat"]
    assert payload["exp"] - payload["iat"] == int(timedelta(hours=24).total_seconds())
