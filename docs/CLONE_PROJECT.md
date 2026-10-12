# Guide: Clone This Project to Your Local PC

This guide shows how to copy (clone) the **Account & Security** project from GitHub
onto your own computer.

**Repository:** https://github.com/sometri/auth-python
**Clone URL (HTTPS):** `https://github.com/sometri/auth-python.git`

---

## 1. What you need first

- **Git** installed on your PC.
  - Check if you already have it:

    ```bash
    git --version
    ```

  - If not, install it with winget from **PowerShell** or **Command Prompt**:

    ```bash
    winget install Git.Git
    ```

    Or download it from https://git-scm.com/downloads.

- **Python 3.10+** to run the app:
  - Check with `python --version`.
  - Download from https://www.python.org/downloads/.

- If the repo is **private**, you must be logged in / authorized (see Step 3).

---

## 2. Pick a folder for your projects

Open a terminal (PowerShell, Command Prompt, or Git Bash) and go to a place where you
keep your code, for example:

```bash
cd D:\py
```

---

## 3. Clone the repository

The clone command is the same for public and private repos — the only difference is
that private repos require authentication.

### Option A — Public repository

Anyone can clone it with no login:

```bash
git clone https://github.com/sometri/auth-python.git
```

### Option B — Private repository

Only you (or invited collaborators) can clone it. Git will ask for credentials:

- **Username:** `sometri`
- **Password:** a **Personal Access Token** (NOT your account password)
  - Create one at: GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
  - Give it the `repo` scope.

```bash
git clone https://github.com/sometri/auth-python.git
```

> Tip: save the token so you don't retype it — use Git Credential Manager (bundled with
> Git for Windows) or the GitHub CLI (`gh auth login`), which handles auth for you.

### Get the exact URL

On GitHub, open https://github.com/sometri/auth-python, click the green **Code**
button, and copy the **HTTPS** URL.

---

## 4. Go into the cloned folder

```bash
cd auth-python
```

Everything from the repo is now on your PC.

---

## 5. Install dependencies and run

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate   |   *nix: source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Open http://127.0.0.1:5000 in your browser. The database (`auth.db`) is created
automatically on first run.

Run the tests (optional):

```bash
pip install -r requirements-dev.txt
pytest
```

---

## 6. (Optional) Keep it up to date

Later, to pull the latest changes from GitHub:

```bash
git pull
```

---

## Cloning with GitHub CLI (alternative)

If you have the GitHub CLI installed and logged in (`gh auth login`), you can clone
with a shorter command, and it handles private-repo auth automatically:

```bash
gh repo clone sometri/auth-python
```

---

## Common issues

| Problem | Fix |
| --- | --- |
| `git: command not found` | Install Git (Step 1) and reopen the terminal. |
| `Repository not found` on a private repo | Sign in, or use a Personal Access Token with the `repo` scope. |
| `Authentication failed` | Use a **token**, not your account password. |
| `Support for password authentication was removed` | Same as above — use a token or `gh auth login`. |
| `ModuleNotFoundError: flask` | Activate the virtualenv and run `pip install -r requirements.txt`. |
| Wrong branch / missing files | You are on the default branch (`main`); run `git checkout main` if needed. |
