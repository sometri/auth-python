import hmac
import json
import secrets
from datetime import datetime, timezone

from flask import current_app
from werkzeug.security import check_password_hash, generate_password_hash

from ..db import get_db
from ..security import hash_token


def _now():
    return datetime.now(timezone.utc)


def create_user(name, email, password, role="CUSTOMER"):
    db = get_db()
    cur = db.execute(
        """
        INSERT INTO users (name, email, password_hash, role, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (name, email, generate_password_hash(password), role, _now().isoformat()),
    )
    db.commit()
    return cur.lastrowid


def get_user_by_email(email):
    return get_db().execute(
        "SELECT * FROM users WHERE lower(email) = lower(?)", (email,)
    ).fetchone()


def get_user_by_id(user_id):
    return get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def verify_credentials(email, password):
    user = get_user_by_email(email)
    if user and check_password_hash(user["password_hash"], password):
        return user
    return None


def set_password(user_id, password):
    db = get_db()
    db.execute(
        "UPDATE users SET password_hash = ? WHERE id = ?",
        (generate_password_hash(password), user_id),
    )
    db.commit()


# --------------------------------------------------------------------------
# Password reset
# --------------------------------------------------------------------------
def issue_reset_token(user):
    token = secrets.token_urlsafe(32)
    expires = (_now() + current_app.config["RESET_TOKEN_TTL"]).isoformat()
    db = get_db()
    db.execute(
        "UPDATE users SET reset_token_hash = ?, reset_token_expires = ? WHERE id = ?",
        (hash_token(token), expires, user["id"]),
    )
    db.commit()
    return token


def user_for_reset_token(token):
    if not token:
        return None
    row = get_db().execute(
        "SELECT * FROM users WHERE reset_token_hash = ?", (hash_token(token),)
    ).fetchone()
    if not row or not row["reset_token_expires"]:
        return None
    if datetime.fromisoformat(row["reset_token_expires"]) < _now():
        return None
    return row


def clear_reset_token(user_id):
    db = get_db()
    db.execute(
        "UPDATE users SET reset_token_hash = NULL, reset_token_expires = NULL WHERE id = ?",
        (user_id,),
    )
    db.commit()


# --------------------------------------------------------------------------
# Two-factor authentication
# --------------------------------------------------------------------------
def enable_two_factor(user_id, secret, recovery_codes):
    db = get_db()
    db.execute(
        """
        UPDATE users
        SET two_factor_secret = ?, two_factor_enabled = 1, recovery_codes = ?
        WHERE id = ?
        """,
        (secret, json.dumps(recovery_codes), user_id),
    )
    db.commit()


def disable_two_factor(user_id):
    db = get_db()
    db.execute(
        """
        UPDATE users
        SET two_factor_secret = NULL, two_factor_enabled = 0, recovery_codes = NULL
        WHERE id = ?
        """,
        (user_id,),
    )
    db.commit()


def consume_recovery_code(user, code):
    if not user["recovery_codes"]:
        return False
    codes = json.loads(user["recovery_codes"])
    match = next((c for c in codes if hmac.compare_digest(c, code)), None)
    if match is None:
        return False
    codes.remove(match)
    db = get_db()
    db.execute(
        "UPDATE users SET recovery_codes = ? WHERE id = ?",
        (json.dumps(codes), user["id"]),
    )
    db.commit()
    return True
