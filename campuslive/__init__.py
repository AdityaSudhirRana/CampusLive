"""CampusLive: real-time academic activity monitoring for colleges."""
from flask import Flask, jsonify, render_template
from . import config
from .db import init_db


def create_app():
    app = Flask(__name__)
    app.secret_key = config.SECRET_KEY
    app.config.update(SESSION_COOKIE_SAMESITE="Lax")
    init_db()

    from . import realtime
    from .routes import auth, root, org, teaching, monitor, manage, timetable, livesession, reports
    for module in (auth, root, org, teaching, monitor, manage, timetable, livesession, reports, realtime):
        app.register_blueprint(module.bp)

    @app.errorhandler(ValueError)
    def bad_request(err):
        return jsonify(error=str(err)), 400

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/healthz")
    def health():
        return jsonify(ok=True)

    return app
