import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

STATIC_DIR = Path(__file__).resolve().parent / "static"
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

APP_TITLE = "Focus47"
DEFAULT_COLOR = "#6264a7"

ADMIN_ACCOUNT = os.getenv("ADMIN_ACCOUNT", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
JWT_TTL_HOURS = 24
