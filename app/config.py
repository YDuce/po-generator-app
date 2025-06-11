import os
from datetime import timedelta
from dotenv import load_dotenv
load_dotenv()

class BaseConfig:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    FRONTEND_URL = os.getenv('FRONTEND_URL')
    CORS_ORIGINS = [FRONTEND_URL]
    JWT_EXPIRATION = timedelta(days=1)
    TWO_WAY_SYNC_ENABLED = os.getenv('TWO_WAY_SYNC_ENABLED','false').lower() == 'true'

class DevelopmentConfig(BaseConfig):
    DEBUG = True

class ProductionConfig(BaseConfig):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
