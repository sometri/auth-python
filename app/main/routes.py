from datetime import datetime, timezone

from flask import Blueprint, redirect, render_template, request, session, url_for

from ..auth import services
from ..i18n import SUPPORTED
from ..security import current_user

main_bp = Blueprint("main", __name__)


def _account_days(user):
    try:
        created = datetime.fromisoformat(user["created_at"])
    except (ValueError, TypeError):
        return 0
    return max((datetime.now(timezone.utc) - created).days, 0)


@main_bp.route("/")
def index():
    user = current_user()
    if user:
        return render_template(
            "dashboard.html",
            events=services.list_login_events(user["id"], limit=8),
            recovery_remaining=services.recovery_codes_remaining(user),
            account_days=_account_days(user),
        )
    return render_template("landing.html")


@main_bp.route("/set-language/<lang>")
def set_language(lang):
    if lang in SUPPORTED:
        session["lang"] = lang
    return redirect(request.referrer or url_for("main.index"))


@main_bp.app_errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404
