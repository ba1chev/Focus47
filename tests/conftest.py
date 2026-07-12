import os

os.environ.setdefault("ADMIN_ACCOUNT", "admin")
os.environ.setdefault("ADMIN_PASSWORD", "admin-test-pw")
os.environ.setdefault("JWT_SECRET", "test-secret-key-long-enough-32-bytes-min")

import pytest
from fastapi.testclient import TestClient

from db.engine import Database
from app.main import Application
from app.constants import CSRF_COOKIE_NAME

ADMIN_ACCOUNT = "admin"
ADMIN_PASSWORD = "admin-test-pw"


@pytest.fixture
def database(tmp_path) -> Database:
    uri = f"sqlite:///{tmp_path / 'test.db'}"
    return Database(database_uri=uri)


@pytest.fixture
def client(database) -> TestClient:
    app = Application(database=database).app
    with TestClient(app) as test_client:
        yield test_client


def _csrf(client: TestClient) -> str:
    client.get("/login")
    return client.cookies.get(CSRF_COOKIE_NAME)


@pytest.fixture
def csrf(client) -> str:
    return _csrf(client)


def register(client: TestClient, name: str, account: str, password: str):
    return client.post(
        "/api/auth/register",
        json={"name": name, "account": account, "password": password}
    )


def login(client: TestClient, account: str, password: str):
    return client.post(
        "/api/auth/login", json={"account": account, "password": password}
    )


@pytest.fixture
def admin_client(client) -> TestClient:
    login(client, ADMIN_ACCOUNT, ADMIN_PASSWORD)
    return client


@pytest.fixture
def regular_client(client) -> TestClient:
    register(client, "Alice", "alice", "alice-pw")
    login(client, "alice", "alice-pw")
    return client


def post_with_csrf(client: TestClient, url: str, json: dict):
    return client.post(url, json=json, headers={"X-CSRF-Token": _csrf(client)})


def patch_with_csrf(client: TestClient, url: str, json: dict):
    return client.patch(url, json=json, headers={"X-CSRF-Token": _csrf(client)})


def delete_with_csrf(client: TestClient, url: str):
    return client.delete(url, headers={"X-CSRF-Token": _csrf(client)})
