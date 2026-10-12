import hashlib
import hmac
import time
from collections import defaultdict
from functools import wraps

from flask import redirect, request, session, url_for

from .db import get_db


# --------------------------------------------------------------------------
# Password reset tokens (stored hashed, never in plaintext)
# --------------------------------------------------------------------------
def hash_token(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------
# Current user / access control
# --------------------------------------------------------------------------
def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return get_db().execute(
        "SELECT * FROM users WHERE id = ?", (user_id,)
    ).fetchone()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("auth.login", redirect=request.path))
        return view(*args, **kwargs)

    return wrapped


def is_safe_redirect(target):
    return bool(target) and target.startswith("/") and not target.startswith("//")


# --------------------------------------------------------------------------
# Tiny in-memory rate limiter (per-process; good enough for a single node)
# --------------------------------------------------------------------------
class RateLimiter:
    def __init__(self):
        self._hits = defaultdict(list)

    def allow(self, key, limit, window_seconds):
        now = time.time()
        bucket = [t for t in self._hits[key] if now - t < window_seconds]
        if len(bucket) >= limit:
            self._hits[key] = bucket
            return False
        bucket.append(now)
        self._hits[key] = bucket
        return True

    def reset(self, key):
        self._hits.pop(key, None)


login_limiter = RateLimiter()


def init_app(app):
    @app.context_processor
    def inject_current_user():
        return {"current_user": current_user()}
