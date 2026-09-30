import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

IS_PRODUCTION = os.getenv("FLASK_ENV", "").lower() == "production"
ENV_SECRET_KEY = os.getenv("SECRET_KEY")

if IS_PRODUCTION and not ENV_SECRET_KEY:
    raise RuntimeError("SECRET_KEY must be set in production.")


class Config:
    SECRET_KEY = ENV_SECRET_KEY or "devguard-development-key"
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

    DATABASE_PATH = os.getenv(
        "DATABASE_PATH",
        str(BASE_DIR / "database" / "devguard.db")
    )

    DEBUG = False
    TESTING = False