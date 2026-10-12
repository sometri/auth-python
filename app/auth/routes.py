import json
import secrets

import pyotp
from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from ..i18n import translate as t
from ..security import current_user, is_safe_redirect, login_limiter, login_required
from . import services

auth_bp = Blueprint("auth", __name__)


def _client_key(prefix, extra=""):
    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "?")
    ip = ip.split(",")[0].strip()
    return f"{prefix}:{ip}:{extra}"


def _complete_login(user):
    session.clear()
    session["user_id"] = user["id"]
    session.permanent = True


def _log_event(user, status):
    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "?")
    ip = ip.split(",")[0].strip()
    services.record_login_event(
        user["id"],
        user["email"],
        status,
        ip=ip,
        user_agent=request.user_agent.string[:255],
    )


# --------------------------------------------------------------------------
# Register
# --------------------------------------------------------------------------
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("main.index"))

    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip()
        password = request.form.get("password") or ""
        confirm = request.form.get("password_confirmation") or ""

        if not name or not email or not password:
            flash(t("auth.errors.fillAllFields"), "error")
        elif password != confirm:
            flash(t("auth.errors.passwordsDontMatch"), "error")
        elif len(password) < 6:
            flash(t("auth.errors.passwordTooShort"), "error")
        elif services.get_user_by_email(email):
            flash(t("auth.errors.emailInUse"), "error")
        else:
            services.create_user(name, email, password)
            flash(t("auth.registerSuccess"), "success")
            redirect_target = request.args.get("redirect")
            if is_safe_redirect(redirect_target):
                return redirect(url_for("auth.login", redirect=redirect_target))
            return redirect(url_for("auth.login"))

    return render_template("register.html")


# --------------------------------------------------------------------------
# Login (+ optional 2FA challenge)
# --------------------------------------------------------------------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("main.index"))

    if request.method == "POST":
        email = (request.form.get("email") or "").strip()
        password = request.form.get("password") or ""

        key = _client_key("login", email.lower())
        limiter_ok = login_limiter.allow(
            key,
            current_app.config["LOGIN_MAX_ATTEMPTS"],
            current_app.config["LOGIN_WINDOW_SECONDS"],
        )
        if not limiter_ok:
            flash(t("auth.errors.tooManyAttempts"), "error")
            return render_template("login.html", email=email)

        user = services.verify_credentials(email, password)
        if not user:
            known = services.get_user_by_email(email)
            if known:
                _log_event(known, "failed")
            flash(t("auth.invalidCredentials"), "error")
            return render_template("login.html", email=email)

        login_limiter.reset(key)

        if user["two_factor_enabled"] and user["two_factor_secret"]:
            session["pending_2fa_user"] = user["id"]
            return redirect(url_for("auth.two_factor"))

        _complete_login(user)
        _log_event(user, "success")
        redirect_target = request.form.get("redirect") or request.args.get("redirect")
        if is_safe_redirect(redirect_target):
            return redirect(redirect_target)
        return redirect(url_for("main.index"))

    return render_template("login.html")


@auth_bp.route("/two-factor", methods=["GET", "POST"])
def two_factor():
    user_id = session.get("pending_2fa_user")
    if not user_id:
        return redirect(url_for("auth.login"))
    user = services.get_user_by_id(user_id)
    if not user:
        session.pop("pending_2fa_user", None)
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        code = (request.form.get("code") or "").strip()
        valid = False

        if len(code) >= 6 and pyotp.TOTP(user["two_factor_secret"]).verify(
            code, valid_window=1
        ):
            valid = True
        elif services.consume_recovery_code(user, code):
            valid = True

        if valid:
            session.pop("pending_2fa_user", None)
            _complete_login(user)
            _log_event(user, "2fa_success")
            return redirect(url_for("main.index"))

        _log_event(user, "2fa_failed")
        flash(t("auth.errors.invalid2fa"), "error")

    return render_template(
        "two_factor.html",
        dev_secret=user["two_factor_secret"] if current_app.debug else None,
    )


# --------------------------------------------------------------------------
# Forgot / reset password
# --------------------------------------------------------------------------
@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip()
        ip_key = _client_key("forgot")
        if not login_limiter.allow(ip_key, 5, 600):
            flash(t("auth.errors.tooManyAttempts"), "error")
            return render_template("forgot_password.html")

        if not email:
            flash(t("auth.errors.emailRequired"), "error")
            return render_template("forgot_password.html")

        user = services.get_user_by_email(email)
        if user:
            token = services.issue_reset_token(user)
            reset_link = url_for("auth.reset_password", token=token, _external=True)
            current_app.logger.info("Password reset link for %s: %s", email, reset_link)

        flash(t("auth.resetLinkSent"), "success")
        return redirect(url_for("auth.forgot_password"))

    return render_template("forgot_password.html")


@auth_bp.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    token = request.args.get("token") or request.form.get("token") or ""
    user = services.user_for_reset_token(token)

    if not user:
        flash(t("auth.errors.invalidResetLink"), "error")
        return render_template("reset_password.html", token=None)

    if request.method == "POST":
        password = request.form.get("password") or ""
        confirm = request.form.get("confirmPassword") or ""

        if password != confirm:
            flash(t("auth.errors.passwordsDontMatch"), "error")
        elif len(password) < 6:
            flash(t("auth.errors.passwordTooShort"), "error")
        else:
            services.set_password(user["id"], password)
            services.clear_reset_token(user["id"])
            flash(t("auth.passwordResetSuccess"), "success")
            return redirect(url_for("auth.login"))

    return render_template("reset_password.html", token=token, email=user["email"])


# --------------------------------------------------------------------------
# Two-factor setup
# --------------------------------------------------------------------------
@auth_bp.route("/settings/two-factor", methods=["GET", "POST"])
@login_required
def two_factor_settings():
    user = current_user()

    if request.method == "POST":
        action = request.form.get("action")

        if action == "enable":
            secret = request.form.get("secret") or pyotp.random_base32()
            code = (request.form.get("code") or "").strip()
            if pyotp.TOTP(secret).verify(code, valid_window=1):
                recovery = [secrets.token_hex(5) for _ in range(8)]
                services.enable_two_factor(user["id"], secret, recovery)
                flash(t("auth.twoFactorEnabledMsg"), "success")
                return redirect(url_for("auth.two_factor_settings"))
            flash(t("auth.errors.invalid2fa"), "error")

        elif action == "disable":
            services.disable_two_factor(user["id"])
            flash(t("auth.twoFactorDisabledMsg"), "success")
            return redirect(url_for("auth.two_factor_settings"))

    user = current_user()
    pending_secret = otpauth_uri = recovery_codes = None

    if not user["two_factor_enabled"]:
        pending_secret = pyotp.random_base32()
        otpauth_uri = pyotp.TOTP(pending_secret).provisioning_uri(
            name=user["email"], issuer_name="Account & Security"
        )
    elif user["recovery_codes"]:
        recovery_codes = json.loads(user["recovery_codes"])

    return render_template(
        "two_factor_settings.html",
        pending_secret=pending_secret,
        otpauth_uri=otpauth_uri,
        recovery_codes=recovery_codes,
    )


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))


# --------------------------------------------------------------------------
# Change password
# --------------------------------------------------------------------------
@auth_bp.route("/change-password", methods=["POST"])
@login_required
def change_password():
    user = current_user()
    current = request.form.get("current_password") or ""
    new = request.form.get("new_password") or ""
    confirm = request.form.get("confirm_password") or ""

    if not services.verify_password(user, current):
        flash(t("auth.errors.wrongPassword"), "error")
    elif new != confirm:
        flash(t("auth.errors.passwordsDontMatch"), "error")
    elif len(new) < 6:
        flash(t("auth.errors.passwordTooShort"), "error")
    else:
        services.set_password(user["id"], new)
        _log_event(user, "password_changed")
        flash(t("auth.passwordChanged"), "success")

    return redirect(url_for("main.index") + "#password")
