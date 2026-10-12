import json
import os

from flask import request, session

SUPPORTED = ("en", "km")
DEFAULT_LANG = "en"

_translations = {}


def load_translations(app):
    folder = os.path.join(app.root_path, "locales")
    data = {}
    for lang in SUPPORTED:
        with open(os.path.join(folder, f"{lang}.json"), encoding="utf-8") as fh:
            data[lang] = json.load(fh)
    return data


def get_locale():
    lang = request.args.get("lang") or session.get("lang")
    if lang not in SUPPORTED:
        lang = DEFAULT_LANG
    return lang


def translate(key, default=None, lang=None):
    lang = lang or get_locale()
    node = _translations.get(lang, _translations.get(DEFAULT_LANG, {}))
    for part in key.split("."):
        if isinstance(node, dict) and part in node:
            node = node[part]
        else:
            node = None
            break
    if node is None:
        return default if default is not None else key
    return node


def init_app(app):
    from datetime import datetime, timezone

    global _translations
    _translations = load_translations(app)

    @app.context_processor
    def inject_globals():
        return {
            "t": translate,
            "lang": get_locale(),
            "now": datetime.now(timezone.utc),
        }
