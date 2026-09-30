import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "devguard-development-key")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
    DATABASE_PATH = os.path.join("instance", "devguard.db")