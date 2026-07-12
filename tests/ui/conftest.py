import os
import time
import httpx
import pytest
import socket
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ADMIN_ACCOUNT = "admin"
ADMIN_PASSWORD = "ui-test-pw"


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.fixture(scope="session")
def live_server(tmp_path_factory):
    port = _free_port()
    db_path = tmp_path_factory.mktemp("uidb") / "ui.db"
    env = {
        **os.environ,
        "ADMIN_ACCOUNT": ADMIN_ACCOUNT,
        "ADMIN_PASSWORD": ADMIN_PASSWORD,
        "JWT_SECRET": "ui-test-secret-key-long-enough-32-bytes",
        "FOCUS47_DB_PATH": str(db_path)
    }
    proc = subprocess.Popen(
        [
            str(PROJECT_ROOT / ".venv" / "bin" / "uvicorn"),
            "app.main:app", "--port", str(port), "--log-level", "warning"
        ],
        cwd=str(PROJECT_ROOT), env=env
    )
    base_url = f"http://127.0.0.1:{port}"
    _wait_until_ready(base_url, proc)
    try:
        yield base_url
    finally:
        proc.terminate()
        proc.wait(timeout=10)


def _wait_until_ready(base_url: str, proc, timeout: float = 15.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if proc.poll() is not None:
            raise RuntimeError("uvicorn exited before becoming ready")
        try:
            if httpx.get(f"{base_url}/login", timeout=1).status_code == 200:
                return
        except httpx.TransportError:
            time.sleep(0.2)
    raise RuntimeError("server did not become ready in time")
