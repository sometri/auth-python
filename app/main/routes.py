from flask import Blueprint, redirect, render_template, request, session, url_for

from ..i18n import SUPPORTED

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return render_template("dashboard.html")


@main_bp.route("/set-language/<lang>")
def set_language(lang):
    if lang in SUPPORTED:
        session["lang"] = lang
    return redirect(request.referrer or url_for("main.index"))


@main_bp.app_errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404
