# Account & Security

A small, self-contained authentication web app built with **Flask**. It provides
login, registration, password reset, and optional two-factor authentication (2FA),
with server-rendered Jinja2 templates backed by SQLite.

**Repository:** https://github.com/sometri/auth-python

## Features

- Register / login / logout with server-side sessions
- Password reset by time-limited, **hashed** tokens
- Optional two-factor auth (TOTP) with single-use recovery codes
- CSRF protection on every form (Flask-WTF)
- Login + password-reset rate limiting
- Bilingual UI (English / Khmer)
- `flask` CLI for setup

## Project structure

```
auth/
├── app/
│   ├── __init__.py        # application factory
│   ├── config.py          # Config / TestConfig
│   ├── db.py              # SQLite helpers + init-db command
│   ├── i18n.py            # translations + t()
│   ├── security.py        # current_user, login_required, tokens, rate limiter
│   ├── cli.py             # create-admin command
│   ├── auth/              # /auth/* routes + data services
│   ├── main/              # / and language switch
│   ├── templates/         # Jinja2 templates
│   └── static/            # css + js
├── tests/                 # pytest suite
├── docs/                  # you are here
├── run.py                 # dev entry point
├── requirements.txt
└── requirements-dev.txt
```

## Requirements

- Python 3.10+
- See `requirements.txt` (Flask, Flask-WTF, pyotp, python-dotenv)

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

Then open http://127.0.0.1:5000. The `auth.db` SQLite database is created
automatically on first run.

Equivalent with the Flask CLI:

```bash
flask --app run init-db
flask --app run create-admin admin@example.com
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

## More guides

- [CLONE_PROJECT.md](CLONE_PROJECT.md) — clone this project onto your PC
- [PUSH_TO_GITHUB.md](PUSH_TO_GITHUB.md) — push this project to GitHub

## Notes

- All SQL uses parameterized statements (`?`) to prevent SQL injection.
