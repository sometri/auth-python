import os

from flask import Flask, send_from_directory
from flask_wtf.csrf import CSRFProtect

from . import db as db_module
from . import i18n, security
from .config import Config

csrf = CSRFProtect()


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    @app.route("/asset/<path:filename>")
    def asset(filename):
        return send_from_directory(os.path.join(app.root_path, "asset"), filename)

    csrf.init_app(app)
    db_module.init_app(app)
    i18n.init_app(app)
    security.init_app(app)

    from .auth.routes import auth_bp
    from .main.routes import main_bp
    from .cli import register_cli

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(main_bp)
    register_cli(app)

    with app.app_context():
        db_module.init_db()

    return app
