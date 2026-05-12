"""TPO (Training and Placement Officer) Blueprint."""
from flask import Blueprint

bp = Blueprint('tpo', __name__, url_prefix='/tpo')

from app.tpo import routes
