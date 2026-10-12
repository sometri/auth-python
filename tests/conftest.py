import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.config import TestConfig
from app.db import init_db


@pytest.fixture
def app(tmp_path):
    class Cfg(TestConfig):
        DATABASE = str(tmp_path / "test.db")
        LOGIN_MAX_ATTEMPTS = 3
        LOGIN_WINDOW_SECONDS = 300

    application = create_app(Cfg)
    with application.app_context():
        init_db()
    yield application


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    from app.security import login_limiter

    login_limiter._hits.clear()
    yield
    login_limiter._hits.clear()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def make_user(app):
    from app.auth import services

    def _make(email="user@v1travel.com", password="secret123", name="Test User"):
        with app.app_context():
            return services.create_user(name, email, password)

    return _make
