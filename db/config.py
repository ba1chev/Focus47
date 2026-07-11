from pathlib import Path


DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "focus47.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schemas" / "schema.sql"