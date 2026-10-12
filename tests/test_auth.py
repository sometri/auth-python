import pyotp


def _register(client, email="qa@v1travel.com", password="secret123"):
    return client.post(
        "/auth/register",
        data={
            "name": "QA User",
            "email": email,
            "password": password,
            "password_confirmation": password,
        },
        follow_redirects=True,
    )


def test_pages_render(client):
    for path in ("/", "/auth/login", "/auth/register", "/auth/forgot-password"):
        assert client.get(path).status_code == 200


def test_register_then_login(client):
    resp = _register(client)
    assert b"Registration successful" in resp.data

    resp = client.post(
        "/auth/login",
        data={"email": "qa@v1travel.com", "password": "secret123"},
        follow_redirects=True,
    )
    assert b"You are signed in" in resp.data
    assert b"Log out" in resp.data


def test_register_rejects_duplicate_email(client, make_user):
    make_user(email="dup@v1travel.com")
    resp = _register(client, email="dup@v1travel.com")
    assert b"already registered" in resp.data


def test_login_rejects_wrong_password(client, make_user):
    make_user()
    resp = client.post(
        "/auth/login", data={"email": "user@v1travel.com", "password": "nope"}
    )
    assert b"Invalid email or password" in resp.data


def test_login_is_rate_limited(client, make_user):
    make_user()
    for _ in range(3):
        client.post(
            "/auth/login", data={"email": "user@v1travel.com", "password": "nope"}
        )
    resp = client.post(
        "/auth/login", data={"email": "user@v1travel.com", "password": "nope"}
    )
    assert b"Too many attempts" in resp.data


def test_forgot_and_reset_password(app, client, make_user):
    from app.auth import services

    make_user()
    resp = client.post(
        "/auth/forgot-password",
        data={"email": "user@v1travel.com"},
        follow_redirects=True,
    )
    assert b"reset link has been sent" in resp.data

    with app.app_context():
        user = services.get_user_by_email("user@v1travel.com")
        assert user["reset_token_hash"]
        token = services.issue_reset_token(user)

    resp = client.get(f"/auth/reset-password?token={token}")
    assert b"Set a new password" in resp.data

    resp = client.post(
        "/auth/reset-password",
        data={"token": token, "password": "brandnew1", "confirmPassword": "brandnew1"},
        follow_redirects=True,
    )
    assert b"Password Reset Successful" in resp.data

    resp = client.post(
        "/auth/login",
        data={"email": "user@v1travel.com", "password": "brandnew1"},
        follow_redirects=True,
    )
    assert b"You are signed in" in resp.data


def test_invalid_reset_token(client):
    resp = client.get("/auth/reset-password?token=bogus")
    assert b"Invalid Link" in resp.data


def test_two_factor_login_flow(app, client, make_user):
    from app.auth import services

    make_user()
    with app.app_context():
        user = services.get_user_by_email("user@v1travel.com")
        secret = pyotp.random_base32()
        services.enable_two_factor(user["id"], secret, ["recovery123"])

    resp = client.post(
        "/auth/login", data={"email": "user@v1travel.com", "password": "secret123"}
    )
    assert resp.status_code == 302
    assert "/auth/two-factor" in resp.headers["Location"]

    resp = client.post("/auth/two-factor", data={"code": "000000"})
    assert b"Invalid or expired 2FA code" in resp.data

    resp = client.post(
        "/auth/two-factor", data={"code": pyotp.TOTP(secret).now()},
        follow_redirects=True,
    )
    assert b"You are signed in" in resp.data


def test_recovery_code_works_once(app, client, make_user):
    from app.auth import services

    make_user()
    with app.app_context():
        user = services.get_user_by_email("user@v1travel.com")
        secret = pyotp.random_base32()
        services.enable_two_factor(user["id"], secret, ["recovery123"])

    client.post("/auth/login", data={"email": "user@v1travel.com", "password": "secret123"})
    resp = client.post(
        "/auth/two-factor", data={"code": "recovery123"}, follow_redirects=True
    )
    assert b"You are signed in" in resp.data

    client.get("/auth/logout")
    with app.app_context():
        user = services.get_user_by_email("user@v1travel.com")
        assert user["recovery_codes"] == "[]"


def test_two_factor_settings_requires_login(client):
    resp = client.get("/auth/settings/two-factor")
    assert resp.status_code == 302
    assert "/auth/login" in resp.headers["Location"]
