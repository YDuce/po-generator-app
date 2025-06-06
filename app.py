import os
import logging
from flask import Flask, render_template, request, jsonify, g, send_from_directory
from logging.handlers import RotatingFileHandler

from config import config
from database import SessionLocal

# API blueprints
from api import init_app as init_api

REACT_BUILD_DIR = os.path.join(
    os.path.dirname(__file__),
    "frontend",
    "0c94bda7-b321-4f9a-855a-ac2802303c88",
    "dist",
)


def create_app(config_name="default"):
    app = Flask(__name__, template_folder="templates")
    app.config.from_object(config[config_name])

    # Setup logging (optional, minimal)
    if not app.debug:
        if not os.path.exists("logs"):
            os.mkdir("logs")
        file_handler = RotatingFileHandler(
            "logs/app.log", maxBytes=10240, backupCount=10
        )
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
            )
        )
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info("PO Generator startup")

    @app.before_request
    def open_session():
        g.db = SessionLocal()

    @app.teardown_request
    def close_session(exception=None):
        db = g.pop("db", None)
        if db:
            if exception:
                db.rollback()
            else:
                db.commit()
            db.close()

    # Remove or comment out old main app routes
    # @app.route('/')
    # def index():
    #     return render_template('dashboard.html')
    # @app.route('/dashboard')
    # def dashboard():
    #     return render_template('dashboard.html')
    # @app.route('/demo')
    # def demo():
    #     return render_template('demo.html')
    # @app.route('/spa')
    # def spa_dashboard():
    #     return render_template('spa_dashboard.html')

    # Serve React static files and index.html for all frontend routes
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_react(path):
        if path != "" and os.path.exists(os.path.join(REACT_BUILD_DIR, path)):
            return send_from_directory(REACT_BUILD_DIR, path)
        else:
            return send_from_directory(REACT_BUILD_DIR, "index.html")

    @app.route("/routes")
    def list_routes():
        import urllib

        output = []
        for rule in app.url_map.iter_rules():
            methods = ",".join(rule.methods)
            url = urllib.parse.unquote(str(rule))
            output.append(f"{url} [{methods}] => {rule.endpoint}")
        return "<br>".join(output)

    @app.route("/test")
    def test():
        return "<h1>Test Page</h1>"

    @app.route("/hello")
    def hello():
        return render_template("hello.html")

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db = getattr(g, "db", None)
        if db:
            db.rollback()
        app.logger.exception(error)
        return jsonify({"error": "Internal server error"}), 500

    init_api(app)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
