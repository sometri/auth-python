# V1 Travel — Auth

A small, self-contained authentication web app built with Flask. It ports the
original Next.js auth screens (login, register, forgot/reset password, 2FA) to
server-rendered Jinja2 templates backed by SQLite.

## Features

- Register / login / logout with server-side sessions
- Password reset by time-limited, **hashed** tokens
- Optional two-factor auth (TOTP) with single-use recovery codes
- CSRF protection on every form (Flask-WTF)
- Login + password-reset rate limiting
- Bilingual UI (English / Khmer)
- `flask` CLI for setup

## Project layout

```
app/
  __init__.py        application factory
  config.py          config classes (Config / TestConfig)
  db.py              sqlite helpers + init-db command
  i18n.py            translations + t()
  security.py        current_user, login_required, token hashing, rate limiter
  cli.py             create-admin command
  auth/
    routes.py        /auth/* endpoints
    services.py      user + token + 2FA data access
  main/routes.py     / and language switch
  templates/         Jinja2 templates
  static/            css + js
tests/               pytest suite
run.py               dev entry point
```

## Setup

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate   |   *nix: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then edit SECRET_KEY
```

## Run

```bash
python run.py            # http://127.0.0.1:5000
```

Equivalent with the Flask CLI:

```bash
flask --app run init-db
flask --app run create-admin admin@v1travel.com
flask --app run run --debug
```

There is no mail server configured; password reset links are written to the
server log instead of emailed, so you can copy them during development.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

## Security notes

- Passwords are hashed with Werkzeug's PBKDF2.
- Reset tokens are stored as SHA-256 hashes and expire after 1 hour.
- Session cookies are `HttpOnly` + `SameSite=Lax`; set `SESSION_COOKIE_SECURE=1`
  when serving over HTTPS.
- The rate limiter is in-process memory — put a shared store (e.g. Redis) behind
  it before running more than one worker.
