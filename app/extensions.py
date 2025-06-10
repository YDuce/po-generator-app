"""Flask extensions.

This module initializes and configures all Flask extensions used in the application.
The extensions are initialized here and then attached to the Flask application
in the application factory.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_cors import CORS

# Initialize extensions
db = SQLAlchemy()  # Database ORM
login = LoginManager()  # User session management
migrate = Migrate()  # Database migrations
cors = CORS()  # Cross-Origin Resource Sharing

# Configure login manager
login.login_view = 'auth.login'
login.login_message = 'Please log in to access this page.'
login.login_message_category = 'info'

@login.user_loader
def load_user(user_id):
    """Load user by ID.
    
    This function is called by Flask-Login to load a user from the database.
    It's used to maintain the user's session.
    
    Args:
        user_id: The ID of the user to load
        
    Returns:
        User: The user object if found, None otherwise
    """
    from app.core.models.user import User
    return User.query.get(int(user_id)) 