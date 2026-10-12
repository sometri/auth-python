# V1 Travel — Auth

A small, self-contained authentication web app built with **Flask**. It provides
login, registration, password reset, and optional two-factor authentication (2FA),
with server-rendered Jinja2 templates backed by SQLite.

**Repository:** https://github.com/sometri/auth-python

The full project reference lives in the repository root: [`../README.md`](../README.md).

## What it does

- Register / login / logout with server-side sessions
- Password reset by time-limited, **hashed** tokens
- Optional two-factor auth (TOTP) with single-use recovery codes
- CSRF protection on every form (Flask-WTF)
- Login + password-reset rate limiting
- Bilingual UI (English / Khmer)

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

## Setup & run

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate   |   *nix: source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Then open http://127.0.0.1:5000. The `auth.db` SQLite database is created
automatically on first run.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

## More guides

- [CLONE_PROJECT.md](CLONE_PROJECT.md) — clone this project onto your PC
- [PUSH_TO_GITHUB.md](PUSH_TO_GITHUB.md) — push any project to GitHub

## Notes

- All SQL uses parameterized statements (`?`) to prevent SQL injection.
- No mail server is configured; password-reset links are written to the server log.
