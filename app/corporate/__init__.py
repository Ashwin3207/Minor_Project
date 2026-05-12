"""Corporate Blueprint."""
from flask import Blueprint

bp = Blueprint('corporate', __name__, url_prefix='/corporate')

from app.corporate import routes
