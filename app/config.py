import os
from datetime import timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Vercel's filesystem is read-only except /tmp, so store the SQLite file there.
_DEFAULT_DB_DIR = "/tmp" if os.getenv("VERCEL") else BASE_DIR


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    DATABASE = os.getenv("DATABASE", os.path.join(_DEFAULT_DB_DIR, "auth.db"))
    # When set (e.g. a Vercel Postgres / Neon URL), PostgreSQL is used instead of SQLite.
    DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL")

    # Session hardening
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "0") == "1"
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # CSRF
    WTF_CSRF_TIME_LIMIT = None

    # Password reset tokens
    RESET_TOKEN_TTL = timedelta(hours=1)

    # Login throttle: attempts per window
    LOGIN_MAX_ATTEMPTS = 8
    LOGIN_WINDOW_SECONDS = 300

    # Public base URL used to build password reset links
    APP_BASE_URL = os.getenv("APP_BASE_URL", "http://127.0.0.1:5000")


class TestConfig(Config):
    TESTING = True
    SECRET_KEY = "test-secret"
    WTF_CSRF_ENABLED = False
    DATABASE = os.path.join(BASE_DIR, "test_auth.db")
    DATABASE_URL = None
