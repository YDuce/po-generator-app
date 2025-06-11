"""Initialize Flask extensions.

Layer: app
"""
from __future__ import annotations

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

__all__ = ["db", "migrate", "cors"]

# Instantiate extensions
db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
