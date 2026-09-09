import os, configparser
from datetime import datetime, timezone
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_babel import Babel
from flask_babel import lazy_gettext as _

app = Flask(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# Load and cache config once at startup
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), "app.cfg"))
VALID_NEWS_REGIONS = {x.strip() for x in config.get("news", "regions").split(",")}

SUPPORTED_LANGS = {x.strip() for x in config.get("base", "languages").split(",")}

# Handle locales by Babel
def get_locale():
    return request.accept_languages.best_match(SUPPORTED_LANGS)
babel = Babel()
babel.init_app(app, locale_selector=get_locale)

# Set shared template variables
@app.context_processor
def inject_locale():
    return dict(current_locale=get_locale(), current_year=datetime.now(timezone.utc).year)


# Home
@app.route("/")
def home():
    return render_template("home.html", title=_('home page title'))

# Privacy policy
@app.route("/privacy")
def privacy():
    return render_template("privacy.html", title=_('privacy page title'))

# News
@app.route("/news")
def news():
    return render_template("news.html", title=_('news page title'))
@app.route("/api/news")
def api_news():

    # 1. Parse region
    region = request.args.get("lang", "en")

    # 2. Validate using config values
    if region not in VALID_NEWS_REGIONS:
        return jsonify({"error": f"Invalid region '{region}'", "valid": list(VALID_NEWS_REGIONS)}), 400

    # 3. Return JSON file (no template rendering)
    return send_from_directory(
        f"{DATA_DIR}/news/{region}",
        "news-latest.json",
        mimetype="application/json"
    )

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=6600)