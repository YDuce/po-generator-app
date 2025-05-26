from flask import Blueprint

bp = Blueprint('api', __name__, url_prefix='/api')

from . import catalog
from . import status
from . import results

__all__ = ["bp"]