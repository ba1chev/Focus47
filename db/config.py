import os
from pathlib import Path


# Path to the SQLite file. Overridable via FOCUS47_DB_PATH (used by tests and
# alternate deployments); defaults to focus47.db in the project root.
_env_path = os.getenv("FOCUS47_DB_PATH")
DEFAULT_DB_PATH = (
    Path(_env_path) if _env_path
    else Path(__file__).resolve().parent.parent / "focus47.db"
)
