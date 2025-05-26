import os
import logging
from flask import Flask, render_template, request, jsonify, send_from_directory, g
from flask_dance.contrib.google import make_google_blueprint, google
from flask_login import LoginManager, login_required, current_user
from werkzeug.utils import secure_filename
from logging.handlers import RotatingFileHandler

from config import config
from database import SessionLocal
from models.allocation import Allocation
# API blueprints
from api import bp as api_bp
from api.porf import bp as porf_bp
from api.export import bp as export_bp
# from channels import get_connector  # Uncomment if needed for channel logic

# User model import for user_loader stub (replace with your actual user model)
# from models.user import User

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Setup logging
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

    # Setup Google OAuth
    google_bp = make_google_blueprint(
        client_id=app.config['GOOGLE_OAUTH_CLIENT_ID'],
        client_secret=app.config['GOOGLE_OAUTH_CLIENT_SECRET'],
        scope=['profile', 'email']
    )
    app.register_blueprint(google_bp, url_prefix='/login')

    # Setup Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'google.login'

    @login_manager.user_loader
    def load_user(user_id):
        # Replace with actual user lookup
        return None

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

    # User-facing routes
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/dashboard')
    @login_required
    def dashboard():
        return render_template('dashboard.html')

    @app.route('/results/<job_id>')
    @login_required
    def results(job_id):
        return render_template('results.html', job_id=job_id)
    
    @app.route('/downloads/<filename>')
    @login_required
    def download_file(filename):
        return send_from_directory(app.config['OUTPUT_FOLDER'], filename)
    
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
