import os
import logging
from flask import Flask, render_template, request, jsonify, g
from logging.handlers import RotatingFileHandler

from config import config
from database import SessionLocal
# API blueprints
from api import bp as api_bp
from api.porf import bp as porf_bp
from api.export import bp as export_bp


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Setup logging (optional, minimal)
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('PO Generator startup')

    @app.before_request
    def open_session():
        g.db = SessionLocal()

    @app.teardown_request
    def close_session(exception=None):
        db = g.pop('db', None)
        if db:
            if exception:
                db.rollback()
            else:
                db.commit()
            db.close()

    # User-facing routes (minimal, per blueprint)
    @app.route('/')
    def index():
        return render_template('dashboard.html')

    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db = getattr(g, 'db', None)
        if db:
            db.rollback()
        app.logger.exception(error)
        return jsonify({'error': 'Internal server error'}), 500

    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(porf_bp)
    app.register_blueprint(export_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
